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
    "base_behaviors": ["Slow_Cruise", "Deep_Dive", "Singing"],
    "features": [
        {"type": "eyes", "t": 0.12, "angle_deg": 80, "size_factor": 0.08},
        {
            "type": "fin", 
            "fin_type": "dorsal", 
            "t": 0.68, 
            "angle": math.pi / 2, 
            "scale": 0.12,
            "scale_xyz": (0.5, 0.7, 0.2)
        },
        {
            "type": "fin", 
            "fin_type": "caudal", 
            "t": 0.98, 
            "angle": math.pi / 2, 
            "scale": 0.18,
            "rotation_euler": (0, 90, 0),
            "scale_xyz": (1.5, 1.0, 0.7)
        },
        {
            "type": "paired_fins", 
            "fin_type": "pectoral", 
            "t": 0.32, 
            "angle_deg": 0, 
            "scale": 0.16,
            "rotation_euler": (5, 35, -10)
        }
    ]
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
