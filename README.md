# Sea Photography & Simulation Asset Pipeline

This repository hosts the procedural generation, modeling, and simulation behaviors for the Sea Photography pipeline. It features an automated Blender 5.1 generation engine, a Unity-ready asset configuration, and clean integration into NVIDIA Isaac Sim (OceanSim) for advanced species-detection sonar and photography validation.

---

## 🚀 Quick Start Run Commands

Run these commands using Git Bash (or your preferred terminal) from the repository root:

### 1. Interactive Mesh & Code Iteration (Blender 5.1 GUI Panel Addon)
If you want to live-edit parameters/geometry equations in VS Code and inspect them inside Blender instantly:

1. Launch the interactive workspace inside Blender:
   ```bash
   python blender/scripts/main.py
   ```
2. In the Blender 3D Viewport window, press `N` on your keyboard to toggle the side property shelf, and select the **Fish Generator** tab.
3. Select your desired **Species** & **Life Stage** from the dropdowns.
4. Open the physics generation files (e.g. [blender/scripts/procedural_fish/definitions.py](blender/scripts/procedural_fish/definitions.py) or [blender/scripts/procedural_fish/models.py](blender/scripts/procedural_fish/models.py)) in VS Code and save your edits.
5. In Blender, click **Reload Code & Spawn**. The addon automatically re-imports your modified python files, cleans up previous geometries, and spawns the fresh fish!

### 2. Standard Batch Generation (Headless)
To generate and export the full library of 20 unified `.fbx` and `.usd` models and compiled catalog JSON structures:

```bash
python blender/scripts/main.py --background
```

### 3. Deploying Models & Behaviors to NVIDIA Isaac Sim
Once meshes and textures/vertex colors are built, sync them directly to your Isaac Sim (OceanSim extension) asset and Python folders:

```bash
python blender/scripts/deploy_isaac_sim.py
```

---

## 🛠️ Key Files & Configurations

- **Simulation Spawner Config**: Spawner rates, camera proximity offset clusters, speed coefficients, and return-to-center physics bubble parameters are located at the top of:
  * `blender/scripts/fish_spawner_behavior.py`
- **Main Generator Logic**:
  * `blender/scripts/main.py`
- **Procedural Math Models**: Modifies base meshes, armatures, fin locations, and color spot details:
  * `blender/scripts/procedural_fish/models.py`
- **Unity Scripts**: Real-time behavioral controllers and spawners inside Unity:
  * `unity/scripts/FishBehaviorController.cs`
  * `unity/scripts/FishSpawningSystem.cs`
- **Metadata Database**:
  * `blender/fish_library_meta.json`

---

## 📌 Architecture Highlights
1. **Hybrid Rigged Assets**: Merges custom procedural modifiers using Python & Geometry Nodes with pre-skinned skeletal rigs, enabling clean and low-overhead animatable `.fbx` and `.usd` exports.
2. **Proximity-Based Simulation Spawner**: The Isaac Sim runtime behavioral logic manages proximity fleeing vectors and returns drifted fish back to a tight 5x5m horizontal cluster in front of the active robotic camera.
