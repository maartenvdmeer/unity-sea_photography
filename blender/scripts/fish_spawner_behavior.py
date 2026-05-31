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

class IsaacFishSimulationManager:
    """
    Manages dynamic spawning of fish USD instances, updates their translations
    forward in space, and drives avoidance steering behaviors when robots/sensors are near.
    """
    def __init__(self, assets_directory=None, fish_metadata=None):
        self.fish_instances = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.5  # Spawn a fish every 1.5 seconds (configurable)
        self.max_fish_count = 35
        
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

        spawn_offset = Gf.Vec3f(
            random.uniform(-35.0, 35.0),
            random.uniform(-35.0, 35.0),
            random.uniform(-15.0, 3.0)  # depth limits
        )
        spawn_pos = origin + spawn_offset
        # Ensure deep water limits
        if spawn_pos[2] > -2.0:
            spawn_pos[2] = -5.0

        # Create unique prim name
        uid = random.randint(1000, 9999)
        prim_path = f"/World/ProceduralFish/{species}_{stage_id}_{uid}"
        
        # Define Prim with reference to fish USD
        prim = stage.DefinePrim(prim_path, "Xform")
        prim.GetReferences().AddReference(usd_path)
        
        # Get base movements metrics from database
        swim_speed = 2.0
        if species in self.metadata and "life_stages" in self.metadata[species]:
            stage_meta = self.metadata[species]["life_stages"].get(stage_id, {})
            # Speed is scaled by length and level metrics
            length = stage_meta.get("length_meters", 1.0)
            speed_mod = stage_meta.get("speed_multiplier", 1.0)
            swim_speed = max(0.5, length * 0.18 * speed_mod)
        
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
        print(f"[FishSim] Spawned {fish_name} at position {spawn_pos} with speed {swim_speed:.2f} m/s")

    def update_fish_movement(self, fish, step_time: float, robot_position=None):
        """
        Updates coordinate translates and steering angles per simulation step.
        """
        current_pos = fish["position"]
        yaw = fish["yaw"]
        speed = fish["swim_speed"]
        
        # 1. Proximity Avoidance Steering
        if robot_position is not None:
            dx = current_pos[0] - float(robot_position[0])
            dy = current_pos[1] - float(robot_position[1])
            dz = current_pos[2] - float(robot_position[2])
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Avoidance triggers inside a 15-meter bubble
            avoidance_trigger_radius = 16.0 if fish["radius"] > 2.0 else 10.0
            if distance < avoidance_trigger_radius:
                # Fish steering away from robot
                target_yaw = math.atan2(dy, dx)
                
                # Smooth yaw steering rotation towards safety angle
                yaw_diff = (target_yaw - yaw) % (2 * math.pi)
                if yaw_diff > math.pi:
                    yaw_diff -= 2 * math.pi
                
                # Turn up to 120 degrees per second
                max_turn = math.radians(120.0) * step_time
                yaw += math.clamp(yaw_diff, -max_turn, max_turn)
                
                # Activate speed burst fleeing behavior
                fish["swim_speed"] = fish["base_speed"] * 2.5
                fish["escape_mode"] = True
                fish["avoidance_timer"] = 3.0 # stay excited for 3 seconds
            else:
                if fish["escape_mode"]:
                    fish["avoidance_timer"] -= step_time
                    if fish["avoidance_timer"] <= 0:
                        fish["escape_mode"] = False
                        fish["swim_speed"] = fish["base_speed"]
                        
        # Standard idle wander deviation if not fleeing
        if not fish["escape_mode"]:
            # Drift direction slightly to simulate random wander
            yaw += random.uniform(-0.15, 0.15) * step_time * 6.0
            
        # 2. Translate coordinates along forward vector (Y is forward in USD export)
        # Note: direction components are cos(yaw) for X, sin(yaw) for Y axis
        move_dir_x = -math.sin(yaw)  # Matches orientation conversions
        move_dir_y = math.cos(yaw)
        
        new_pos = Gf.Vec3f(
            current_pos[0] + move_dir_x * speed * step_time,
            current_pos[1] + move_dir_y * speed * step_time,
            current_pos[2] + random.uniform(-0.1, 0.1) * speed * step_time # smooth drift depth
        )
        
        # Maintain depth bounds
        if new_pos[2] < -35.0:
            new_pos[2] = -35.0
        elif new_pos[2] > -2.0:
            new_pos[2] = -2.0

        # Update transforms
        fish["position"] = new_pos
        fish["yaw"] = yaw
        
        fish["translate_op"].Set(new_pos)
        fish["rotate_op"].Set(Gf.Vec3f(0.0, 0.0, math.degrees(yaw)))
        
        # 3. Handle maximum drift boundaries
        if robot_position is not None:
            dist_from_robot = math.sqrt(
                (new_pos[0]-float(robot_position[0]))**2 + 
                (new_pos[1]-float(robot_position[1]))**2 + 
                (new_pos[2]-float(robot_position[2]))**2
            )
            # Prune fish that swim too far away (e.g. > 80m)
            if dist_from_robot > 85.0:
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
