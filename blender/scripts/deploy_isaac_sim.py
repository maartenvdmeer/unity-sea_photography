import os
import shutil
import json

def deploy_to_isaac_sim():
    """
    Automates the synchronization/deployment of procedurally generated USD models
    and behavior metadata from the sea-photography workspace directly to OceanSim and Isaac Sim.
    """
    print("======================================================================")
    # Source paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blender_dir = os.path.dirname(script_dir)
    exported_assets_src = os.path.join(blender_dir, "exported_assets")
    meta_src = os.path.join(blender_dir, "fish_library_meta.json")

    # Destination paths as requested/specified by user
    isaac_assets_root = r"C:\projects\ocean-sim_assets\OceanSim_assets"
    isaac_ext_root = r"C:\isaac-sim\extsUser\OceanSim"

    print(f"Starting Isaac Sim / OceanSim Asset Deployer...")
    print(f"Source Assets Directory: {exported_assets_src}")

    # Validate source
    if not os.path.exists(exported_assets_src):
        print(f"[ERROR] Source exported assets folder not found: {exported_assets_src}")
        print("Please run the procedural generation pipeline first (run_blender.bat)!")
        return

    # Check for target directories
    deploy_assets = os.path.exists(isaac_assets_root)
    deploy_ext = os.path.exists(isaac_ext_root)

    if not deploy_assets:
        print(f"[WARNING] OceanSim assets directory not found: {isaac_assets_root}")
    if not deploy_ext:
        print(f"[WARNING] OceanSim extension directory not found: {isaac_ext_root}")

    # Determine destination folders inside OceanSim assets
    # Standard Omniverse directory schema organizes models under /models or /fish
    dest_models_dir = os.path.join(isaac_assets_root, "Models", "ProceduralFish")
    dest_meta_dir = os.path.join(isaac_ext_root, "data") if deploy_ext else None

    # Copy USD files to OceanSim Assets
    if deploy_assets:
        try:
            os.makedirs(dest_models_dir, exist_ok=True)
            copied_files = 0
            for root, dirs, files in os.walk(exported_assets_src):
                for file_name in files:
                    if file_name.lower().endswith((".usd", ".usda", ".usdc")):
                        src_file = os.path.join(root, file_name)
                        rel_path = os.path.relpath(src_file, exported_assets_src)
                        dest_file = os.path.join(dest_models_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(src_file, dest_file)
                        print(f" -> Synchronized USD: {rel_path} to OceanSim_assets")
                        copied_files += 1
            print(f"[SUCCESS] Successfully deployed {copied_files} USD models to: {dest_models_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to synchronize USD models: {e}")

    # Copy fish_library_meta.json to OceanSim Extension
    if deploy_ext and dest_meta_dir:
        try:
            os.makedirs(dest_meta_dir, exist_ok=True)
            dest_meta_file = os.path.join(dest_meta_dir, "fish_library_meta.json")
            shutil.copy2(meta_src, dest_meta_file)
            print(f"[SUCCESS] Successfully synced metadata database to OceanSim user extension: {dest_meta_file}")
        except Exception as e:
            print(f"[ERROR] Failed to synchronize metadata database: {e}")
    else:
        # Fallback: copy metadata directly to the assets root so the extension can read it from there
        if deploy_assets:
            try:
                dest_meta_file = os.path.join(isaac_assets_root, "fish_library_meta.json")
                shutil.copy2(meta_src, dest_meta_file)
                print(f"[SUCCESS] Synced metadata database to assets root: {dest_meta_file}")
            except Exception as e:
                print(f"[ERROR] Failed to copy metadata: {e}")

    print("======================================================================")
    print("Omniverse/Isaac Sim assets deployment process complete.")
    print("Whales with markings and other marine life are ready for OceanSim robotics!")
    print("======================================================================")

if __name__ == "__main__":
    deploy_to_isaac_sim()
