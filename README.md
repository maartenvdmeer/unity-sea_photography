# Sea Photography & Simulation Asset Pipeline

This repository hosts the procedural generation, modeling, and simulation behaviors for the Sea Photography pipeline. It features an automated Blender 5.1 generation engine, a Unity-ready asset configuration, and clean integration into NVIDIA Isaac Sim (OceanSim) for advanced species-detection sonar and photography validation.

---

## 🚀 Quick Start Run Commands

Run these commands using Git Bash (or your preferred terminal) from the repository root:

### 1. Generating Procedural Fish (Blender 5.1)
The master orchestration script automatically detects standard Blender installations. To generate/regenerate the 20 procedural fish types (including different ages, genders, and spot markings):

```bash
# Run headless (in background) - Recommended
python blender/scripts/main.py --background

# Run with Blender GUI open
python blender/scripts/main.py
```

### 2. Deploying Models & Behaviors to NVIDIA Isaac Sim
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
