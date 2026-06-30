import math

TEMPLATE = {
    "name": "African Cichlid",
    "scientific_name": "Metriaclima estherae",
    "description": "Extremely vibrant, colorful family of freshwater fish found in rift lakes.",
    "base_length": 0.12,  # cm-scale
    "base_color": (0.95, 0.45, 0.05, 1.0),  # Neon orange
    "stripe_color": (0.05, 1.0, 0.95, 1.0), # Electric cyan highlights
    "pattern": "striped",
    "preferred_depth": "shallow",
    "diet": "Herbivore / Algae Grater",
    "spawn_locations": ["Rocky Reefs", "Sandy Bays"],
    "spawn_months": [3, 4, 5, 6, 7, 8, 9],
    "base_behaviors": ["Territorial", "Nest_Digging", "Shy"]
}

def get_body_vertex(t, angle, length):
    y = -t * length
    # Lateral compressed, tall oval
    h = 0.34 * math.sin(t**0.8 * math.pi) * length
    w = 0.075 * math.sin(t * math.pi) * length
    z_off = 0.0
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = w * cos_a
    z = z_off + h * sin_a
    return x, y, z

def create_features(name, length, create_lowpoly_eye, create_lowpoly_fin):
    components = []
    
    # Place Eyes
    eye_t = 0.14
    eye_angle_left = math.radians(140)
    eye_angle_right = math.radians(40)
    eye_size = 0.045 * (length**0.75)
    
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
    
    # Continuous thick dorsal fin spanning half the back
    co_dorsal = get_body_vertex(0.50, math.pi/2, length)
    dorsal = create_lowpoly_fin(f"{name}_DorsalTall", "dorsal", size=length * 0.42)
    dorsal.location = co_dorsal
    dorsal.scale = (0.4, 1.4, 0.9)
    components.append(dorsal)
    
    # Symmetrical pelvic/rib fin pair
    for side in [-1, 1]:
        co_pec = get_body_vertex(0.32, 0 if side == 1 else math.pi, length)
        pec = create_lowpoly_fin(f"{name}_Pec_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.3)
        pec.location = co_pec
        pec.rotation_euler = (math.radians(10), math.radians(side * 15), math.radians(-side * 5))
        if side == -1:
            pec.scale.x = -1.0
        components.append(pec)
        
    # Large rounded fan-like tail
    co_caudal = get_body_vertex(0.98, math.pi/2, length)
    caudal = create_lowpoly_fin(f"{name}_BroadTail", "caudal", size=length * 0.45)
    caudal.location = co_caudal
    caudal.scale = (0.5, 0.7, 1.2)
    components.append(caudal)
    
    return components
