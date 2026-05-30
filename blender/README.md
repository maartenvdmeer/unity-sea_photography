# Procedural Fish Generation Pipeline for Underwater Photography Game

This repository handles the procedural generation and metadata extraction of fish varieties (sharks, manta rays, whales, cichlids, algae eaters, etc.) in Blender. The generated assets and metadata are prepared for low-overhead, seamless integration into a Unity-based underwater photography and ecology game.

---

## 🏗️ Architectural Choice: Hybrid Scripting, Base Mesh Armature, and Modifiers

When designing procedural organic assets with skeleton-based animations for Unity, we evaluated three prominent approaches:

| Metric | Option A: Pure Python Mesh Generation | Option B: Pure Geometry Nodes (Spatially Procedural) | Option C: Hybrid Scripting + Modifiers + Armatures (Chosen) |
| :--- | :--- | :--- | :--- |
| **Visual Fidelity** | Very Hard (complex trigonometric manipulation of vertices) | Excellent (highly interactive, math-driven node groups) | Excellent (artist-sculpted base meshes combined with dynamic deformation) |
| **Rigging & Skinning** | Extremely Complex (assigning vertex groups/weights manually) | Hard/Incomplete (difficult to export dynamic armatures to FBX smoothly) | Perfect (uses pre-configured professional armatures that deform cleanly) |
| **Animation Baking** | Difficult (must animate via code or regenerate shapes) | Hard (requires complex shape keys or vertex animation textures) | Native (standard bone/armature action clips like Swim, Tased, Caught) |
| **Game Optimization** | High (exact vertex count control) | High (dynamic LODs direct from nodes) | High (built-in decimate modifiers, LOD exporting, low-poly bones) |
| **Speed & Variety** | Moderate (computationally intensive in Python) | Very Fast (C++ multi-threaded execution in Blender) | Very Fast (script-driven modifier settings, shape keys, and materials) |

### Why We Chose the **Hybrid Approach (Option C)**:
1. **Game Engine Readiness**: Unity expects standard skeletal mesh skins (`SkinnedMeshRenderer`) and classic FBX bone animation files (`.fbx` with embedded or external `.anim` clips). Creating these animatable models entirely from scratch in python or pure Geometry Nodes leads to messy rigging/skinning output that often fails to import cleanly into Unity.
2. **Dynamic Ecology Variations**: We can model a generic base fish shape (or specialized base shapes like "Fusiform" for sharks/cichlids, "Flat/Capry" for manta rays, and "Gigantic" for whales) with a rigged armature. Python then procedurally alters:
   - **Proportions**: Adjusts scale, bone lengths, or shape keys (e.g., juveniles have larger eyes/heads; males has longer fins or defensive spines).
   - **Mesh Deformations**: Applies random or structured modifiers (e.g., Simple Deform, Lattices, or custom Geometry Nodes modifiers) to vary tail length, body thickness, and mouth structures.
   - **Shading & Texture**: Interacts with Blender's shader nodes to change color schemes, add spots/stripes, and adjust roughness or translucency based on gender and age, which are baked out or dynamically tinted in Unity.
   - **LOD Generation**: Automatically applies a `Decimate` modifier and exports different LOD stages (`LOD0`, `LOD1`, `LOD2`) to ensure high rendering performance.

---

## 📁 Repository Structure

```
blender/
├── blend_files/
│   └── fish_generation.blend          # Master blender file containing base rigs, material nodes, and animations
├── scripts/
│   ├── main.py                         # Master orchestration script (runs the generation pipeline)
│   ├── cleanup.py                      # Safeguards and cleanups Blender scene to prevent memory leaks or duplicate objects
│   ├── curve_generator.py              # Procedurally constructs fins and custom path guides using Blender bezier curves
│   └── create_fish_components.py       # Python library that builds procedural structural meshes and sets modifiers
├── README.md                           # Architectual and system documentation (This File)
└── fish_library_meta.json              # Procedurally exported metadata catalog for Unity's seasonal and spawning engine
```

---

## 🧬 Ecology & Game Mechanics Design

The Blender output pipeline exports both **3D Assets (.fbx)** and a **Metadata Catalog (.json)**. This catalog is used by Unity to drive game systems dynamically:

### 1. Life Stages & Gender Morphology
- **Fry / Larval / Juvenile**:
  - *Blender Adjustment*: Mesh scaled down, eye scale increased, head-to-body ratio increased, fins shortened.
  - *Behavior Meta*: Weak swimmers, swim in schools near cover (kelp/reefs), very shy (high retreat velocity).
- **Mature Male**:
  - *Blender Adjustment*: Bright, high-contrast procedural colors (mating display), larger fins/clasp/features.
  - *Behavior Meta*: Highly territorial, aggressive towards other males, displays animation triggers.
- **Mature Female**:
  - *Blender Adjustment*: Slightly larger base size, duller/camouflage textures (egg protection), wider midsection.
  - *Behavior Meta*: Focused on algae/plankton grazing, school-oriented, defensive.

### 2. Interaction Animations
Every generated FBX contains a shared, standardized set of bone animations or shape key streams:
- `Swim_Idle`: Default elegant swimming speed, varies by species.
- `Swim_Fast`: Escape or predatory pursuit.
- `React_Tased`: Spasmodic micro-shivers followed by sinking or floatation, representing temporary paralysis.
- `React_Caught`: Panicked flapping inside the netting structure.
- `React_Light`: Blinking, turning away from heavy diver flashlights, or being drawn towards bioluminescence.
- `React_Photo`: Brief flinch when high-intensity flash is triggered.

### 3. Seasonality (Month) and Location Rules
The procedurally generated JSON metadata maps each species, gender, and life stage to specific seasonal conditions:
- **Months (1-12)**: Represents seasonal migrations (e.g., Whale Sharks are migratory and only spawn in Summer; Salmon run in Autumn; Cichlids display breeding behaviors in Spring/Summer).
- **Locations**: Reef, Deep Trench, Cave, Open Ocean, Estuary.
- **Behaviors**: Grazer, Apex Predator, Detritivore, Coral Picker.

---

## 🚀 How to Run the Pipeline

To run the generator and output the library of rigged low-poly assets along with their metadata:

1. Ensure Blender 4.5+ is installed.
2. Run the provided batch file:
   ```cmd
   blender/scripts/run_blender.bat
   ```
   Or execute background headless generation using:
   ```cmd
   "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b blender/blend_files/fish_generation.blend -P blender/scripts/main.py
   ```
3. The exported assets will be placed in the target Unity assets folders (`Assets/Models/Fish/` and `Assets/Resources/FishMetadata.json`).
