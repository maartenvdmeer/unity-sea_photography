import math

TEMPLATE = {
    "name": "Reef Shark",
    "scientific_name": "Carcharhinus perezi",
    "description": "An active marine predator often found patrolling coral reefs. Fast swimmer.",
    "base_length": 2.2,  # meters
    "base_color": (0.35, 0.42, 0.48, 1.0),  # Steel gray
    "stripe_color": (0.2, 0.23, 0.26, 1.0),
    "pattern": "plain",
    "preferred_depth": "medium-deep",
    "diet": "Carnivore",
    "spawn_locations": ["Reef Wall", "Deep Ocean", "Open Waters"],
    "spawn_months": [12, 1, 2, 6, 7, 8],
    "base_behaviors": ["Patrolling", "Investigative", "Schooling"]
}

def get_body_vertex(t, angle, length):
    y = -t * length
    # Streamlined fusiform shape
    h = 0.16 * math.sin(t**0.75 * math.pi) * length
    w = 0.12 * math.sin(t**0.75 * math.pi) * length
    z_off = -0.012 * t * length
    
    # Ellipse-based cross-section with slightly flattened belly
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = w * cos_a
    z = z_off + h * sin_a * (1.0 if sin_a >= 0 else 0.8)
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
    
    # Prominent Dorsal Fin
    co_dorsal = get_body_vertex(0.44, math.pi/2, length)
    dorsal = create_lowpoly_fin(f"{name}_Dorsal", "dorsal", size=length * 0.32)
    dorsal.location = co_dorsal
    dorsal.rotation_euler = (math.radians(-10), 0, 0)
    components.append(dorsal)
    
    # Symmetrical Pectoral wing fins
    for side in [-1, 1]:
        co_pec = get_body_vertex(0.30, 0 if side == 1 else math.pi, length)
        pec = create_lowpoly_fin(f"{name}_Pec_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.28)
        pec.location = co_pec
        pec.rotation_euler = (math.radians(15), math.radians(side * 40), math.radians(-side * 18))
        if side == -1:
            pec.scale.x = -1.0
        components.append(pec)
        
    # Large vertical caudal fin
    co_caudal = get_body_vertex(0.98, math.pi/2, length)
    caudal = create_lowpoly_fin(f"{name}_Caudal", "caudal", size=length * 0.35)
    caudal.location = co_caudal
    components.append(caudal)
    
    return components
