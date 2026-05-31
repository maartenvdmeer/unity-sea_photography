# Gaussian Splatting Workflow Notes

This note captures the typical modular workflow for using 3D Gaussian Splatting environments with Isaac Sim and underwater robotics.

## Workflow Diagram

```mermaid
graph TD
    subgraph Capture_and_Process
        A[Collect Underwater Video or Images] --> B[Run SfM or COLMAP Reconstruction]
        B --> C[Train Gaussian Splatting Model]
        C --> D[Export 3DGS Scene as PLY]
    end

    subgraph Omniverse_and_Isaac
        D --> E[Import PLY into Isaac Sim or Omniverse]
        E --> F[Render as Photorealistic Background]
        G[Create Invisible Physics Colliders] --> H[Collision and Navigation Layer]
        F --- H
    end

    subgraph Simulation
        H --> I[Spawn Robot with Cameras and Sensors]
        H --> J[Spawn Procedural Fish]
        I --> K[Collect Vision and Navigation Data]
        J --> K
    end
```

## Practical Notes

- The splat is mainly visual, so physics usually needs a separate collision layer.
- This works well for camera-based robotics experiments.
- Procedural fish can be added as standard USD actors on top of the splat scene.
