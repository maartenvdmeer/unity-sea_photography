import math

TEMPLATE = {
    "name": "Siamese Algae Eater",
    "scientific_name": "Crossocheilus oblongus",
    "description": "Equipped with a sucker mouth to scrape algae off rocky riverbeds and sea-bottom structures.",
    "base_length": 0.16,
    "base_color": (0.45, 0.38, 0.28, 1.0),  # Earthy brownish-green
    "stripe_color": (0.1, 0.1, 0.1, 1.0),   # Black stripe
    "pattern": "striped",
    "preferred_depth": "bottom",
    "diet": "Algivore / Detritivore",
    "spawn_locations": ["Riverbeds", "Sea Bottom", "Cave Openings"],
    "spawn_months": [4, 5, 10, 11],
    "base_behaviors": ["Bottom_Grazing", "Hiding", "Darting"]
}

def get_body_vertex(t, angle, length):
    y = -t * length
    # Flat bottom with sucker mouth alignment
    h = 0.10 * math.sin(t**1.1 * math.pi) * length
    w = 0.13 * math.sin(t**0.85 * math.pi) * length
    z_off = -h * 0.3
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = w * cos_a
    # Flatten belly
    z = z_off + h * sin_a * (1.0 if sin_a >= 0 else 0.25)
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
    
    # Humped back dorsal
    co_dorsal = get_body_vertex(0.45, math.pi/2, length)
    dorsal = create_lowpoly_fin(f"{name}_Dorsal", "dorsal", size=length * 0.28)
    dorsal.location = co_dorsal
    components.append(dorsal)
    
    # Pelvic bottom brushes for scraping bottom walls
    for side in [-1, 1]:
        co_pec = get_body_vertex(0.30, math.radians(-40) if side == 1 else math.radians(220), length)
        pec = create_lowpoly_fin(f"{name}_Pelvic_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.22)
        pec.location = co_pec
        # Angled down and slightly back
        pec.rotation_euler = (math.radians(-20), math.radians(side * 20), math.radians(-side * 45))
        if side == -1:
            pec.scale.x = -1.0
        components.append(pec)
        
    # Swept backward tail
    co_caudal = get_body_vertex(0.98, math.pi/2, length)
    caudal = create_lowpoly_fin(f"{name}_ForkTail", "caudal", size=length * 0.32)
    caudal.location = co_caudal
    components.append(caudal)
    
    return components
