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
    "base_behaviors": ["Patrolling", "Investigative", "Schooling"],
    "features": [
        {"type": "eyes", "t": 0.14, "angle_deg": 40},
        {
            "type": "fin", 
            "fin_type": "dorsal", 
            "t": 0.44, 
            "angle": math.pi / 2, 
            "scale": 0.32,
            "rotation_euler": (-10, 0, 0)
        },
        {
            "type": "paired_fins", 
            "fin_type": "pectoral", 
            "t": 0.30, 
            "angle_deg": 0, 
            "scale": 0.28,
            "rotation_euler": (15, 40, -18)
        },
        {"type": "fin", "fin_type": "caudal", "t": 0.98, "angle": math.pi / 2, "scale": 0.35}
    ]
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
