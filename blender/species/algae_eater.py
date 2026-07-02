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
    "base_behaviors": ["Bottom_Grazing", "Hiding", "Darting"],
    "features": [
        {"type": "eyes", "t": 0.14, "angle_deg": 40},
        {"type": "fin", "fin_type": "dorsal", "t": 0.45, "angle": math.pi / 2, "scale": 0.28},
        {"type": "custom", "name": "pelvic_brushes", "t": 0.30, "scale": 0.22},
        {"type": "fin", "fin_type": "caudal", "t": 0.98, "angle": math.pi / 2, "scale": 0.32}
    ]
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
