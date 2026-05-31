import sys
import os
import json
import subprocess

# Dynamic path resolution relative to the script location
script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
workspace_dir = os.path.dirname(script_dir)  # Navigate from blender/scripts up to blender/

if script_dir not in sys.path:
    sys.path.append(script_dir)

# ==============================================================================
# SELF-RELAUNCH UNDER BLENDER IF RUN WITH NORMAL PYTHON
# ==============================================================================
try:
    import bpy
except ImportError:
    # If bpy is not available, we are running in a standard system python shell.
    # Re-launch this script within Blender's bundled Python context.
    blender_exe = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
    
    # Locate scene file if present
    blend_file = os.path.join(workspace_dir, "blend_files", "fish_generation.blend")
    blend_file_backup = os.path.join(workspace_dir, "blend_files", "fish_generation.blend1")
    
    cmd_args = [blender_exe]
    
    # Headless / background check
    if "--background" in sys.argv or "-b" in sys.argv:
        cmd_args.append("--background")
        
    if os.path.exists(blend_file):
        cmd_args.append(blend_file)
    elif os.path.exists(blend_file_backup):
        cmd_args.append(blend_file_backup)
        
    # Python script execution argument
    cmd_args.extend(["-P", __file__])
    
    print(f"[RELAUNCH] System python detected. Orchestrating Blender subprocess execution...")
    print(f"[RELAUNCH] Command: {' '.join(cmd_args)}")
    
    try:
        result = subprocess.run(cmd_args, check=True)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"[ERROR] Blender executable not found at: {blender_exe}")
        print("[ERROR] Please set the 'BLENDER_EXE' environment variable to point to your Blender installation.")
        sys.exit(1)
    except subprocess.CalledProcessError as err:
        print(f"[ERROR] Blender session terminated with error code: {err.returncode}")
        sys.exit(err.returncode)

# Import custom package which houses modularized procedures
import procedural_fish
import importlib

importlib.reload(procedural_fish.definitions)
importlib.reload(procedural_fish.cleanup)
importlib.reload(procedural_fish.shading)
importlib.reload(procedural_fish.models)
importlib.reload(procedural_fish.rigging)
importlib.reload(procedural_fish)

def run_procedural_fish_generation():
    print("--------------------------------------------------")
    print("STARTING PROCEDURAL FISH CORE GENERATION PIPELINE")
    print("--------------------------------------------------")
    
    # 1. Clean the current blender session of legacy temporary objects
    procedural_fish.bulk_cleanup(
        prefixes=("Fish_", "Rig_"),
        protected_names=("Default_Camera", "Default_Light")
    )
    
    # 2. Setup exporting directories
    export_dir = os.path.join(workspace_dir, "exported_assets")
    os.makedirs(export_dir, exist_ok=True)
    
    # Metadata database to compile
    exported_catalog = {}
    
    # Iterate species and life-stages
    for species_id, spec in procedural_fish.SPECIES_TEMPLATES.items():
        exported_catalog[species_id] = {
            "name": spec["name"],
            "scientific_name": spec["scientific_name"],
            "description": spec["description"],
            "diet": spec["diet"],
            "spawn_months": spec["spawn_months"],
            "spawn_locations": spec["spawn_locations"],
            "life_stages": {}
        }
        
        for stage_id, stage in procedural_fish.LIFE_STAGES.items():
            # Desired names for organization
            fish_name = f"Fish_{species_id.capitalize()}_{stage_id.capitalize()}"
            
            # Setup organic folders per fish type (species)
            spec_export_dir = os.path.join(export_dir, species_id.lower())
            os.makedirs(spec_export_dir, exist_ok=True)
            
            # Compute physical dimensions
            actual_length = spec["base_length"] * stage["scale_mod"]
            
            # Create base procedural mesh (internally builds and welds body, eyes, and fins!)
            print(f"Generating physical mesh structure for: {fish_name} (Length: {actual_length:.2f}m)...")
            fish_obj = procedural_fish.create_procedural_fish_mesh(
                name=fish_name,
                length=actual_length,
                species=species_id
            )
            
            # Adjust material and display colors per stage/gender
            # Males have higher color brightness, females are slightly mottled
            base_col = list(spec["base_color"])
            stripe_col = list(spec["stripe_color"])
            if stage_id == "mature_male":
                # Maximize saturation and value for breeding displays
                base_col[0] = min(1.0, base_col[0] * 1.3)
                base_col[1] = min(1.0, base_col[1] * 1.3)
                base_col[2] = min(1.0, base_col[2] * 1.3)
            elif stage_id == "fry" or stage_id == "juvenile":
                # Babies are more translucent/camouflage
                base_col[3] = 0.65  # Slight transparency
            
            # Build and apply procedurally compiled shader materials
            procedural_fish.apply_procedural_materials(
                obj=fish_obj,
                base_color=tuple(base_col),
                stripe_color=tuple(stripe_col),
                pattern_type=spec["pattern"],
                species=species_id,
                length=actual_length
            )
            
            # Rig armature skeleton over spine and create beautiful idle swim animations
            # Now that all subcomponents are welded inside fish_obj, rigorous distance weights 
            # will be assigned to EVERY SINGLE vertex of eyes, fins, and body!
            rig_obj = procedural_fish.rig_and_animate_fish(fish_obj, num_bones=5)
            
            # Generate comprehensive metadata catalog entry for Unity backend integration
            extended_behaviors = list(spec["base_behaviors"]) + stage["behavior_mods"]
            stage_metadata = {
                "asset_model_name": f"{species_id.lower()}/{fish_name}.fbx",
                "asset_model_fbx": f"{species_id.lower()}/{fish_name}.fbx",
                "asset_model_usd": f"{species_id.lower()}/{fish_name}.usd",
                "length_meters": round(actual_length, 3),
                "social_cohesion_factor": stage["social_cohesion"],
                "speed_scalar": stage["speed_factor"],
                "reactivity_multiplier": stage["reactivity_multiplier"],
                "behaviors": extended_behaviors,
                "interactions": {
                    "tased": "Action_Spasm_Sink",
                    "caught": "Action_Net_Flap",
                    "light_observed": "Action_Dazzled_Turn",
                    "photographed": "Action_Flinch"
                }
            }
            exported_catalog[species_id]["life_stages"][stage_id] = stage_metadata
            
            # Try to export target mesh & animation skeleton into Unity ready FBX assets folder
            try:
                # Select only current generated fish elements
                bpy.ops.object.select_all(action='DESELECT')
                fish_obj.select_set(True)
                rig_obj.select_set(True)
                    
                fbx_output_path = os.path.join(spec_export_dir, f"{fish_name}.fbx")
                
                # Check for Blender version compatibility on exporters
                if hasattr(bpy.ops.export_scene, 'fbx'):
                    bpy.ops.export_scene.fbx(
                        filepath=fbx_output_path,
                        use_selection=True,
                        axis_forward='-Z',
                        axis_up='Y',
                        add_leaf_bones=False,
                        bake_anim=True,
                        bake_anim_step=1.0,
                        bake_anim_simplify_factor=1.0
                    )
                else:
                    # In newer Blender or fallback versions, standard obj/gltf is useful
                    bpy.ops.wm.obj_export(filepath=fbx_output_path.replace(".fbx", ".obj"), export_selected=True)
                print(f"Successfully exported FBX/OBJ to: {fbx_output_path}")
            except Exception as ex:
                print(f"Export warning for {fish_name}: {ex}. Running in dry-run/mock format.")

            # Try to export target mesh & animation skeleton into Omniverse/Isaac Sim ready USD assets folder
            try:
                usd_output_path = os.path.join(spec_export_dir, f"{fish_name}.usd")
                if hasattr(bpy.ops.wm, "usd_export"):
                    # Select only current generated fish elements
                    bpy.ops.object.select_all(action='DESELECT')
                    fish_obj.select_set(True)
                    rig_obj.select_set(True)
                    bpy.context.view_layer.objects.active = rig_obj
                    
                    try:
                        # Full-featured modern USD export
                        bpy.ops.wm.usd_export(
                            filepath=usd_output_path,
                            selected_objects_only=True,
                            export_animation=True,
                            export_hair=False,
                            export_materials=True,
                            export_armatures=True
                        )
                    except TypeError:
                        try:
                            # Fallback for alternative parameter configurations
                            bpy.ops.wm.usd_export(
                                filepath=usd_output_path,
                                selected_objects_only=True,
                                export_animation=True,
                                export_materials=True
                            )
                        except TypeError:
                            # Safest fallback
                            bpy.ops.wm.usd_export(
                                filepath=usd_output_path,
                                selected_objects_only=True
                            )
                    print(f"Successfully exported USD to: {usd_output_path}")
                else:
                    print("USD export is not supported in this Blender version (bpy.ops.wm.usd_export doesn't exist).")
            except Exception as ex:
                print(f"USD Export warning for {fish_name}: {ex}")
                
    # 3. Export global meta config as JSON
    json_path = os.path.join(os.path.dirname(script_dir), "fish_library_meta.json")
    with open(json_path, "w") as f:
        json.dump(exported_catalog, f, indent=4)
        
    print("--------------------------------------------------")
    print(f"METADATA CATALOG SUCCESSFULLY GENERATED: {json_path}")
    print("PROCEDURAL GENERATION PIPELINE FINISHED SUCCESSFULLY")
    print("--------------------------------------------------")

def main():
    run_procedural_fish_generation()

if __name__ == "__main__":
    main()