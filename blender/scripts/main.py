import sys, os

base_path = r"C:\sea_models\unity-sea_photography"
script_path = os.path.join(base_path, "blender", "scripts")

if script_path not in sys.path:
    sys.path.append(script_path)

import bpy
import time

import cleanup
import importlib

for module in [cleanup]:
    importlib.reload(module)

def main():
    for module in [cleanup]:
        importlib.reload(module)

        # Set names to protect from cleanup
    cleanup.bulk_cleanup(prefixes=(
        "Cube",
    ), protected_names = ("Tomato_LowPoly", "Tomato", "Crown", "Arm_L", "Arm_R", "Crown_LowPoly")
    )


# === run main only if in Blender context ===
if __name__ == "__main__" or bpy.context.space_data is not None:
    main()