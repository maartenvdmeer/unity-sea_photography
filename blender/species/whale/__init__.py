import math

TEMPLATE = {
    "name": "Blue Whale",
    "scientific_name": "Balaenoptera musculus",
    "description": "The largest creature to inhabit Earth. Moves slowly and makes massive sound calls.",
    "base_length": 15.0,
    "base_color": (0.24, 0.32, 0.40, 1.0),  # Mottled blue-gray
    "stripe_color": (0.85, 0.90, 0.95, 1.0), # High-contrast white/light spots for robotics computer vision
    "pattern": "spotted",
    "preferred_depth": "deep",
    "diet": "Planktivore",
    "spawn_locations": ["Abyssal Trench", "Open Waters"],
    "spawn_months": [1, 2, 7, 8],
    "base_behaviors": ["Slow_Cruise", "Deep_Dive", "Singing"]
}

ANIMATION_AXIS = "pitch"
NUM_SPOTS = 55
SPOT_RADIUS_FACTOR = 0.024

def get_body_vertex(t, angle, length):
    y = -t * length
    # Massive stocky blueprint
    h = 0.18 * math.sin(t**0.45 * math.pi) * length
    w = 0.20 * math.sin(t**0.45 * math.pi) * length
    # Taper head flat on top for blowhole
    z_off = 0.0
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = w * cos_a
    z = h * sin_a
    if t < 0.25 and sin_a > 0:
        # Flatten top blowhole area
        z *= (1.0 - 0.35 * (0.25 - t) / 0.25)
    return x, y, z

def create_features(name, length, create_lowpoly_eye, create_lowpoly_fin):
    components = []
    
    # Place Eyes
    eye_t = 0.12
    eye_angle_left = math.radians(100)
    eye_angle_right = math.radians(80)
    eye_size = 0.12
    
    co_eye_l = get_body_vertex(eye_t, eye_angle_left, length)
    co_eye_r = get_body_vertex(eye_t, eye_angle_right, length)
    
    # Left Eye
    eye_l = create_lowpoly_eye(f"{name}_EyeL", size=eye_size)
    eye_l.location = co_eye_l
    eye_l.rotation_euler = (0, 0, math.radians(65))
    components.append(eye_l)
    
    # Right Eye
    eye_r = create_lowpoly_eye(f"{name}_EyeR", size=eye_size)
    eye_r.location = co_eye_r
    eye_r.rotation_euler = (0, 0, math.radians(-65))
    components.append(eye_r)
    
    # Small dorsal ridge
    co_dorsal = get_body_vertex(0.68, math.pi/2, length)
    dorsal = create_lowpoly_fin(f"{name}_DorsalRidge", "dorsal", size=length * 0.12)
    dorsal.location = co_dorsal
    dorsal.scale = (0.5, 0.7, 0.2)
    components.append(dorsal)
    
    # Wide horizontal fluke centered on spinal channel
    co_caudal = get_body_vertex(0.98, math.pi/2, length)
    fluke = create_lowpoly_fin(f"{name}_Fluke", "caudal", size=length * 0.18)
    fluke.location = co_caudal
    fluke.rotation_euler = (0, math.radians(90), 0) # Rotate caudal 90 deg around Y to make horizontal fluke!
    fluke.scale = (1.5, 1.0, 0.7)
    components.append(fluke)
    
    # Pectoral side flippers
    for side in [-1, 1]:
        co_pec = get_body_vertex(0.32, 0 if side == 1 else math.pi, length)
        pec = create_lowpoly_fin(f"{name}_Flipper_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.16)
        pec.location = co_pec
        pec.rotation_euler = (math.radians(5), math.radians(side * 35), math.radians(-side * 10))
        if side == -1:
            pec.scale.x = -1.0
        components.append(pec)
        
    return components
