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
    blender_exe = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
    
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

# Import custom submodules
import cleanup
import curve_generator
import create_fish_components
import species_definitions
import importlib

importlib.reload(cleanup)
importlib.reload(curve_generator)
importlib.reload(create_fish_components)
importlib.reload(species_definitions)

def run_procedural_fish_generation():
    print("--------------------------------------------------")
    print("STARTING PROCEDURAL FISH CORE GENERATION PIPELINE")
    print("--------------------------------------------------")
    
    # 1. Clean the current blender session of legacy temporary objects
    cleanup.bulk_cleanup(
        prefixes=("Fish_", "Rig_", "Material_", "Eye_"),
        protected_names=("Default_Camera", "Default_Light")
    )
    
    # 2. Setup exporting directories
    export_dir = os.path.join(workspace_dir, "exported_assets")
    os.makedirs(export_dir, exist_ok=True)
    
    # Metadata database to compile
    exported_catalog = {}
    
    # Iterate species and life-stages
    for species_id, spec in species_definitions.SPECIES_TEMPLATES.items():
        exported_catalog[species_id] = {
            "name": spec["name"],
            "scientific_name": spec["scientific_name"],
            "description": spec["description"],
            "diet": spec["diet"],
            "spawn_months": spec["spawn_months"],
            "spawn_locations": spec["spawn_locations"],
            "life_stages": {}
        }
        
        for stage_id, stage in species_definitions.LIFE_STAGES.items():
            # Desired names for organization
            fish_name = f"Fish_{species_id.capitalize()}_{stage_id.capitalize()}"
            
            # Select anatomical profiles
            h_profile, w_profile, off_profile = spec["profile_func"]()
            
            # Compute physical dimensions
            actual_length = spec["base_length"] * stage["scale_mod"]
            
            # Create base procedural mesh
            print(f"Generating physical mesh structure for: {fish_name} (Length: {actual_length:.2f}m)...")
            fish_obj = create_fish_components.create_procedural_fish_mesh(
                name=fish_name,
                length=actual_length,
                height_profile=h_profile,
                width_profile=w_profile,
                offset_profile=off_profile,
                fish_type=species_id
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
                # Babies are more translucent or camouflaged
                base_col[3] = 0.65  # Slight transparency
            
            # Build and apply procedurally compiled shader materials
            create_fish_components.apply_procedural_materials(
                obj=fish_obj,
                base_color=tuple(base_col),
                stripe_color=tuple(stripe_col),
                pattern_type=spec["pattern"]
            )
            
            # Spherically place and map eyes
            eye_sizing = 0.05 * (actual_length**0.7) * stage["eye_scale_mod"]
            create_fish_components.add_fish_eyes(
                fish_obj=fish_obj,
                snout_y_factor=0.15,
                height=actual_length * 0.08,
                lateral_spacing=actual_length * 0.1,
                eye_size=eye_sizing
            )
            
            # Spawn customized fins
            create_fish_components.add_procedural_fins(
                fish_obj=fish_obj,
                fish_type=species_id,
                size=actual_length * 0.8
            )
            
            # Rig armature skeleton over spine and create beautiful idle swim animations
            rig_obj = create_fish_components.rig_and_animate_fish(fish_obj, num_bones=5)
            
            # Generate comprehensive metadata catalog entry for Unity backend integration
            extended_behaviors = list(spec["base_behaviors"]) + stage["behavior_mods"]
            stage_metadata = {
                "asset_model_name": f"{fish_name}.fbx",
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
                for child in fish_obj.children:
                    child.select_set(True)
                    
                fbx_output_path = os.path.join(export_dir, f"{fish_name}.fbx")
                
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