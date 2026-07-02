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
    "base_behaviors": ["Territorial", "Nest_Digging", "Shy"],
    "features": [
        {"type": "eyes", "t": 0.14, "angle_deg": 40},
        {
            "type": "fin", 
            "fin_type": "dorsal", 
            "t": 0.50, 
            "angle": math.pi / 2, 
            "scale": 0.42,
            "scale_xyz": (0.4, 1.4, 0.9)
        },
        {
            "type": "paired_fins", 
            "fin_type": "pectoral", 
            "t": 0.32, 
            "angle_deg": 0, 
            "scale": 0.3,
            "rotation_euler": (10, 15, -5)
        },
        {
            "type": "fin", 
            "fin_type": "caudal", 
            "t": 0.98, 
            "angle": math.pi / 2, 
            "scale": 0.45,
            "scale_xyz": (0.5, 0.7, 1.2)
        }
    ]
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
