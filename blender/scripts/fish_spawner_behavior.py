"""
Dynamic Procedural Fish Spawning and Avoidance Simulation System for NVIDIA Isaac Sim.
Integrates with the OceanSim framework to spawn Z-up oriented procedural fish, animate them
with calculated translation velocity, and steering behaviors to avoid nearby robots/players.
"""

import math
import random
import os
import omni
from pxr import Usd, Gf, Sdf, UsdGeom
import omni.usd
from omni.isaac.core.utils.prims import is_prim_path_valid, get_prim_path
from omni.isaac.core.prims import GeometryPrim, XFormPrim

# ==============================================================================
# INTUITIVE SIMULATION CONFIGURATION
# Adjust these values to modify spawning density, placement, ranges, and sizes!
# ==============================================================================
SPAWNER_CONFIG = {
    "spawn_interval": 1.0,         # Spawn a fish every X seconds (Default: 1.0)
    "max_fish_count": 25,          # Maximum concurrent fish allowed in the scene
    
    # Close-up Placement relative to robot/camera (meters)
    "spawn_offset_x": (-3.0, 3.0), # Spawn left/right range relative to robot
    "spawn_offset_y": (2.5, 6.5),  # Spawn depth (directly in front of camera/robot)
    "spawn_offset_z": (-1.2, 1.2), # Spawn height relative to robot
    
    # Restrictive Movement bubble around robot (meters)
    "max_drift_distance": 5.0,     # Max distance fish can travel from robot (keeps them in 5x5m sphere)
    "flee_trigger_distance": 3.0,  # Proximity trigger distance for escape maneuvers
    "return_steer_speed": 180.0,   # Turning speed in degrees/sec when returning inside the bubble
    
    # Speed bounds
    "speed_coefficient": 0.6,      # Scaler for general swim velocity (lower speed makes filming/detecting easier)
}

class IsaacFishSimulationManager:
    """
    Manages dynamic spawning of fish USD instances, updates their translations
    forward in space, and drives avoidance steering behaviors when robots/sensors are near.
    """
    def __init__(self, assets_directory=None, fish_metadata=None):
        self.fish_instances = []
        self.spawn_timer = 0.0
        self.spawn_interval = SPAWNER_CONFIG["spawn_interval"]
        self.max_fish_count = SPAWNER_CONFIG["max_fish_count"]
        
        # Resolve assets path
        self.assets_dir = assets_directory or r"C:\projects\ocean-sim_assets\OceanSim_assets\Models\ProceduralFish"
        self.metadata = fish_metadata or {}
        self.fish_types = ["shark", "manta", "whale", "cichlid", "algae_eater"]
        self.life_stages = ["fry", "juvenile", "mature_male", "mature_female"]
        
        # Load local database if empty
        meta_path = r"C:\isaac-sim\extsUser\OceanSim\data\fish_library_meta.json"
        if not self.metadata and os.path.exists(meta_path):
            import json
            try:
                with open(meta_path, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"[FishSim] Error loading metadata: {e}")

    def update_simulation(self, step_time: float, robot_position: Gf.Vec3f = None):
        """
        Calculates updates for every active fish instance:
         1. Handles spawner timer to create new assets.
         2. Drives active fish forward based on base velocity and current rotation.
         3. Calculates proximity to the robot; triggers steering deviation if nearby.
        """
        # Spawning mechanism
        if len(self.fish_instances) < self.max_fish_count:
            self.spawn_timer += step_time
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0.0
                self.spawn_random_fish(robot_position)

        # Update cycle for existing fish
        active_instances = []
        for fish in self.fish_instances:
            if not is_prim_path_valid(fish["prim_path"]):
                continue  # Clean up dead or unlinked Prims
                
            # Perform movement logic
            keep_alive = self.update_fish_movement(fish, step_time, robot_position)
            if keep_alive:
                active_instances.append(fish)
            else:
                # Remove fish that swam too far or got deleted
                self.destroy_fish(fish)
                
        self.fish_instances = active_instances

    def spawn_random_fish(self, robot_position=None):
        """
        Creates a randomized fish instance in the active Omniverse stage.
        """
        stage = omni.usd.get_context().get_stage()
        if not stage:
            return

        species = random.choice(self.fish_types)
        stage_id = random.choice(self.life_stages)
        
        # Match names to directory structure
        species_folder = species
        fish_name = f"Fish_{species.capitalize()}_{stage_id.capitalize()}"
        usd_filename = f"{fish_name}.usd"
        usd_path = os.path.join(self.assets_dir, species_folder, usd_filename)
        
        if not os.path.exists(usd_path):
            # Try flat fallback path
            usd_path = os.path.join(self.assets_dir, usd_filename)
            if not os.path.exists(usd_path):
                print(f"[FishSim] Model file not found: {usd_path}")
                return

        # Choose spawn location around robot or origin Safely supporting numpy arrays/lists/Gf.Vec
        if robot_position is not None:
            origin = Gf.Vec3f(float(robot_position[0]), float(robot_position[1]), float(robot_position[2]))
        else:
            origin = Gf.Vec3f(0.0, 0.0, -15.0)

        # Spawn right in front of the camera using offsets from our SPAWNER_CONFIG
        spawn_offset = Gf.Vec3f(
            random.uniform(SPAWNER_CONFIG["spawn_offset_x"][0], SPAWNER_CONFIG["spawn_offset_x"][1]),
            random.uniform(SPAWNER_CONFIG["spawn_offset_y"][0], SPAWNER_CONFIG["spawn_offset_y"][1]),
            random.uniform(SPAWNER_CONFIG["spawn_offset_z"][0], SPAWNER_CONFIG["spawn_offset_z"][1])
        )
        spawn_pos = origin + spawn_offset
        # Ensure deep water limits
        if spawn_pos[2] > -1.0:
            spawn_pos[2] = -2.0

        # Create unique prim name
        uid = random.randint(1000, 9999)
        prim_path = f"/World/ProceduralFish/{species}_{stage_id}_{uid}"
        
        # Define Prim with reference to fish USD
        prim = stage.DefinePrim(prim_path, "Xform")
        prim.GetReferences().AddReference(usd_path)
        
        # Get base movements metrics from database
        swim_speed = 1.5
        if species in self.metadata and "life_stages" in self.metadata[species]:
            stage_meta = self.metadata[species]["life_stages"].get(stage_id, {})
            # Speed is scaled by length and level metrics
            length = stage_meta.get("length_meters", 1.0)
            speed_mod = stage_meta.get("speed_multiplier", 1.0)
            swim_speed = max(0.3, length * 0.15 * speed_mod)
            
        # Apply speed coefficient to slow fish down for easy photography and detection
        swim_speed *= SPAWNER_CONFIG["speed_coefficient"]
        
        # Random starting orientation (Y-forward, Z-Up)
        yaw = random.uniform(0, 2.0 * math.pi)
        
        # Initialize transformation attributes safely to prevent "op already exists" warnings in Pixar USD
        xform = UsdGeom.Xformable(prim)
        translate_op = None
        rotate_op = None
        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                translate_op = op
            elif op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
                rotate_op = op
                
        if translate_op is None:
            translate_op = xform.AddTranslateOp()
        if rotate_op is None:
            rotate_op = xform.AddRotateXYZOp()
        
        translate_op.Set(spawn_pos)
        rotate_op.Set(Gf.Vec3f(0.0, 0.0, math.degrees(yaw)))
        
        # Save fish state
        fish_data = {
            "prim_path": prim_path,
            "xform": xform,
            "translate_op": translate_op,
            "rotate_op": rotate_op,
            "position": spawn_pos,
            "yaw": yaw,
            "swim_speed": swim_speed,
            "base_speed": swim_speed,
            "avoidance_timer": 0.0,
            "radius": 4.0 if species == "whale" else 1.5,
            "escape_mode": False
        }
        
        self.fish_instances.append(fish_data)
        print(f"[FishSim] Spawned {fish_name} closely at position {spawn_pos} with speed {swim_speed:.2f} m/s")

    def update_fish_movement(self, fish, step_time: float, robot_position=None):
        """
        Updates coordinate translates and steering angles per simulation step.
        """
        current_pos = fish["position"]
        yaw = fish["yaw"]
        speed = fish["swim_speed"]
        
        # Determine center point of the bubble
        if robot_position is not None:
            center_x = float(robot_position[0])
            center_y = float(robot_position[1])
            center_z = float(robot_position[2])
        else:
            center_x, center_y, center_z = 0.0, 0.0, -15.0

        # Calculate distance to robot/center
        dx = current_pos[0] - center_x
        dy = current_pos[1] - center_y
        dz = current_pos[2] - center_z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # 1. Bubble Constraint Steering (Return-to-Center)
        # Keeps fish in a strict 5x5m sphere around active camera!
        if distance > SPAWNER_CONFIG["max_drift_distance"]:
            # Steer the fish straight back towards the robot center
            target_yaw = math.atan2(-dy, -dx)
            
            # Smooth yaw steering rotation towards center
            yaw_diff = (target_yaw - yaw) % (2 * math.pi)
            if yaw_diff > math.pi:
                yaw_diff -= 2 * math.pi
                
            max_turn = math.radians(SPAWNER_CONFIG["return_steer_speed"]) * step_time
            yaw += max(min(yaw_diff, max_turn), -max_turn)
            
            # Temporarily reduce speed or keep constant to orient clearly
            speed = fish["base_speed"]
            fish["escape_mode"] = False
            
        # 2. Proximity Avoidance Steering (Fleeing when robot gets too close)
        elif robot_position is not None and distance < SPAWNER_CONFIG["flee_trigger_distance"]:
            # Fish steering away from robot
            target_yaw = math.atan2(dy, dx)
            
            # Smooth yaw steering rotation towards safety angle
            yaw_diff = (target_yaw - yaw) % (2 * math.pi)
            if yaw_diff > math.pi:
                yaw_diff -= 2 * math.pi
            
            max_turn = math.radians(120.0) * step_time
            yaw += max(min(yaw_diff, max_turn), -max_turn)
            
            # Activate speed burst fleeing behavior
            fish["swim_speed"] = fish["base_speed"] * 2.0
            fish["escape_mode"] = True
            fish["avoidance_timer"] = 2.0  # stay excited for 2 seconds
            speed = fish["swim_speed"]
        else:
            if fish["escape_mode"]:
                fish["avoidance_timer"] -= step_time
                if fish["avoidance_timer"] <= 0:
                    fish["escape_mode"] = False
                    fish["swim_speed"] = fish["base_speed"]
            speed = fish["swim_speed"]
                        
        # Standard idle wander deviation if not fleeing and inside bounds
        if not fish["escape_mode"] and distance <= SPAWNER_CONFIG["max_drift_distance"]:
            # Drift direction slightly to simulate random wander
            yaw += random.uniform(-0.15, 0.15) * step_time * 6.0
            
        # 3. Translate coordinates along forward vector (Y is forward in USD export)
        # Note: direction components are cos(yaw) for X, sin(yaw) for Y axis
        move_dir_x = -math.sin(yaw)  # Matches orientation conversions
        move_dir_y = math.cos(yaw)
        
        new_pos = Gf.Vec3f(
            current_pos[0] + move_dir_x * speed * step_time,
            current_pos[1] + move_dir_y * speed * step_time,
            current_pos[2] + random.uniform(-0.06, 0.06) * speed * step_time # smooth drift depth
        )
        
        # Maintain vertical depth boundaries relative to bubble center
        min_depth = center_z - 3.0
        max_depth = min(center_z + 3.0, -1.5)
        if new_pos[2] < min_depth:
            new_pos[2] = min_depth
        elif new_pos[2] > max_depth:
            new_pos[2] = max_depth

        # Update transforms
        fish["position"] = new_pos
        fish["yaw"] = yaw
        
        fish["translate_op"].Set(new_pos)
        fish["rotate_op"].Set(Gf.Vec3f(0.0, 0.0, math.degrees(yaw)))
        
        # Prune fish ONLY if they somehow break physics logic and fly super far (e.g. > 35m)
        if distance > 35.0:
            return False
                
        return True

    def destroy_fish(self, fish):
        """
        Deletes the fish prim from the active stage when pruned.
        """
        stage = omni.usd.get_context().get_stage()
        if stage and is_prim_path_valid(fish["prim_path"]):
            stage.RemovePrim(fish["prim_path"])

    def clear_all(self):
        """
        Destroys all active fish instances (useful for teardowns).
        """
        for fish in self.fish_instances:
            self.destroy_fish(fish)
        self.fish_instances = []
