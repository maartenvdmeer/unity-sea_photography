import sys
import os
import json

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
    from bpy.props import EnumProperty, BoolProperty
except ImportError:
    # Standard python relauncher for interactive development
    import subprocess
    blender_exe = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
    blend_file = os.path.join(workspace_dir, "blend_files", "fish_generation.blend")
    blend_file_backup = os.path.join(workspace_dir, "blend_files", "fish_generation.blend1")
    
    cmd_args = [blender_exe]
    if os.path.exists(blend_file):
        cmd_args.append(blend_file)
    elif os.path.exists(blend_file_backup):
        cmd_args.append(blend_file_backup)
    cmd_args.extend(["-P", __file__])
    
    print(f"[RELAUNCH] System python detected. Relaunching in Blender: {' '.join(cmd_args)}")
    result = subprocess.run(cmd_args)
    sys.exit(result.returncode)

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
                        # Full-featured modern USD export with Z-Up Orientation and color attributes
                        bpy.ops.wm.usd_export(
                            filepath=usd_output_path,
                            selected_objects_only=True,
                            export_animation=True,
                            export_hair=False,
                            export_materials=True,
                            export_mesh_colors=True,
                            generate_preview_surface=True,
                            export_armatures=True,
                            convert_orientation=True,
                            export_global_up_selection='Z',
                            export_global_forward_selection='Y'
                        )
                    except TypeError:
                        try:
                            # Fallback for alternative parameter configurations (safely preserving orientation conversion and colors)
                            bpy.ops.wm.usd_export(
                                filepath=usd_output_path,
                                selected_objects_only=True,
                                export_animation=True,
                                export_materials=True,
                                export_mesh_colors=True,
                                generate_preview_surface=True,
                                convert_orientation=True,
                                export_global_up_selection='Z',
                                export_global_forward_selection='Y'
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

# ==============================================================================
# INTERACTIVE ITERATION BLENDER ADDON
# Allows UI-driven selection, dynamic module reloading, and live fish spawning
# ==============================================================================

class OBJECT_OT_procedural_fish_spawn(bpy.types.Operator):
    """Reloads VS Code modules, cleans active workspace, and Spawns selected species info"""
    bl_label = "Spawn Selected Fish"
    bl_idname = "object.procedural_fish_spawn"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        species_id = scene.fish_generator_species
        stage_id = scene.fish_generator_stage
        
        # 1. Reload Python modules dynamically live from workspace
        try:
            import importlib
            import procedural_fish
            importlib.reload(procedural_fish.definitions)
            importlib.reload(procedural_fish.cleanup)
            importlib.reload(procedural_fish.shading)
            importlib.reload(procedural_fish.models)
            importlib.reload(procedural_fish.rigging)
            importlib.reload(procedural_fish)
            self.report({'INFO'}, "Successfully reloaded all procedural_fish workspace modules!")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to reload workspace modules: {e}")
            return {'CANCELLED'}
            
        # 2. Cleanup existing procedurally spawned entities
        try:
            procedural_fish.bulk_cleanup(
                prefixes=("Fish_", "Rig_"),
                protected_names=("Default_Camera", "Default_Light")
            )
        except Exception as e:
            self.report({'WARNING'}, f"Workspace cleanup warning: {e}")
            
        # 3. Create the selected species variant
        try:
            spec = procedural_fish.SPECIES_TEMPLATES[species_id]
            stage = procedural_fish.LIFE_STAGES[stage_id]
            
            fish_name = f"Fish_{species_id.capitalize()}_{stage_id.capitalize()}"
            actual_length = spec["base_length"] * stage["scale_mod"]
            
            # Create standard procedural mesh
            join_components = scene.fish_generator_join_components
            fish_obj = procedural_fish.create_procedural_fish_mesh(
                name=fish_name,
                length=actual_length,
                species=species_id,
                join_components=join_components
            )
            
            # Morph color variations
            base_col = list(spec["base_color"])
            stripe_col = list(spec["stripe_color"])
            if stage_id == "mature_male":
                base_col[0] = min(1.0, base_col[0] * 1.3)
                base_col[1] = min(1.0, base_col[1] * 1.3)
                base_col[2] = min(1.0, base_col[2] * 1.3)
            elif stage_id == "fry" or stage_id == "juvenile":
                base_col[3] = 0.65
                
            # Build and apply procedurally compiled shader materials
            procedural_fish.apply_procedural_materials(
                obj=fish_obj,
                base_color=tuple(base_col),
                stripe_color=tuple(stripe_col),
                pattern_type=spec["pattern"],
                species=species_id,
                length=actual_length
            )
            
            # Rig skeleton bone nodes and bind armature
            rig_obj = procedural_fish.rig_and_animate_fish(fish_obj, num_bones=5)
            
            # Select and focus on the generated armature & mesh
            bpy.ops.object.select_all(action='DESELECT')
            fish_obj.select_set(True)
            rig_obj.select_set(True)
            context.view_layer.objects.active = rig_obj
            
            self.report({'INFO'}, f"Spawned {fish_name} successfully!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Spawning system error: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

class OBJECT_OT_procedural_fish_export_all(bpy.types.Operator):
    """Generates and Exports all 20 combinations of fishes and saves metadata"""
    bl_label = "Export All Fish (Library)"
    bl_idname = "object.procedural_fish_export_all"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Reimport modules to make sure latest code is selected
            import importlib
            import procedural_fish
            importlib.reload(procedural_fish.definitions)
            importlib.reload(procedural_fish.cleanup)
            importlib.reload(procedural_fish.shading)
            importlib.reload(procedural_fish.models)
            importlib.reload(procedural_fish.rigging)
            importlib.reload(procedural_fish)
            
            run_procedural_fish_generation()
            self.report({'INFO'}, "Successfully generated and exported full library!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Batch Export Error: {e}")
            return {'CANCELLED'}

class OBJECT_OT_procedural_fish_deploy(bpy.types.Operator):
    """Deploys generated assets and behaviors directly to NVIDIA Isaac Sim / OceanSim"""
    bl_label = "Deploy to Isaac Sim"
    bl_idname = "object.procedural_fish_deploy"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
            deploy_script = os.path.join(script_path, "deploy_isaac_sim.py")
            if os.path.exists(deploy_script):
                # Dynamically loading behavior
                import sys
                if script_path not in sys.path:
                    sys.path.append(script_path)
                import deploy_isaac_sim
                importlib.reload(deploy_isaac_sim)
                deploy_isaac_sim.deploy_to_isaac_sim()
                self.report({'INFO'}, "Successfully deployed materials, metadata, and behaviors to Isaac Sim!")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Could not locate deploy_isaac_sim.py in workspace!")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Deployment error: {e}")
            return {'CANCELLED'}

class VIEW3D_PT_procedural_fish_generator(bpy.types.Panel):
    """Creates a custom Viewport Sidebar Panel for procedural fish setup"""
    bl_label = "Procedural Fish Tool"
    bl_idname = "VIEW3D_PT_procedural_fish_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Fish Generator'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Iteration Dashboard", icon='INFO')
        box = layout.box()
        box.prop(scene, "fish_generator_species", text="Species")
        box.prop(scene, "fish_generator_stage", text="Stage")
        box.prop(scene, "fish_generator_join_components", text="Join Components")
        
        layout.separator()
        layout.scale_y = 1.3
        layout.operator("object.procedural_fish_spawn", text="Reload Code & Spawn Single", icon='FILE_REFRESH')
        
        layout.separator()
        layout.label(text="Pipeline Operations", icon='TOOL_SETTINGS')
        row = layout.row(align=True)
        row.operator("object.procedural_fish_export_all", text="Export 20x Mesh Library", icon='OUTPUT')
        row.operator("object.procedural_fish_deploy", text="Deploy to Isaac Sim", icon='EXPORT')

# Addon registration
classes = (
    OBJECT_OT_procedural_fish_spawn,
    OBJECT_OT_procedural_fish_export_all,
    OBJECT_OT_procedural_fish_deploy,
    VIEW3D_PT_procedural_fish_generator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.fish_generator_species = EnumProperty(
        name="Species",
        description="Procedural species template configurations",
        items=[
            ("shark", "Reef Shark", "Swept dorsal and ventral, large tail, high velocity skeleton model"),
            ("manta", "Manta Ray", "Flat wing-like geometries, side wing sweep meshes"),
            ("whale", "Whale Cetacean", "Gigantic round streamlined structures, top blowhole layout"),
            ("cichlid", "Cichlid", "Compressed tall oval depth profile"),
            ("algae_eater", "Algae Eater", "Flat belly structures and suction profile shape")
        ],
        default="shark"
    )
    
    bpy.types.Scene.fish_generator_stage = EnumProperty(
        name="Life Stage",
        description="Age and gender morphology values",
        items=[
            ("fry", "Fry (Baby)", "Oversized eye-scales with translucent shaders"),
            ("juvenile", "Juvenile", "Translucent growing proportion modifier sizes"),
            ("mature_male", "Mature Male", "High vivid/contrast display pattern pigments"),
            ("mature_female", "Mature Female", "Camouflaged wide spawning geometries")
        ],
        default="mature_male"
    )
    
    bpy.types.Scene.fish_generator_join_components = BoolProperty(
        name="Join Components",
        description="Whether to join eyes, fins, and body into a single mesh (True) or keep them separate (False)",
        default=True
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.fish_generator_species
    del bpy.types.Scene.fish_generator_stage

def main():
    register()
    print("\n" + "="*80)
    print(" PROCEDURAL FISH GENERATION INTERACTIVE ADDON ACTIVE")
    print(" Press 'N' in the Blender 3D Viewport and open the 'Fish Generator' panel!")
    print(" Edit parameters in VS Code, and click 'Reload Code & Spawn' to iterate live.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()