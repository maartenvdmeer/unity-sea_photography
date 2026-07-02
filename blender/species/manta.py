import math

TEMPLATE = {
    "name": "Giant Manta Ray",
    "scientific_name": "Mobula birostris",
    "description": "Gentle filter-feeding giants. Known for their graceful winged glides.",
    "base_length": 4.5,
    "base_color": (0.08, 0.08, 0.10, 1.0),  # Dark navy back
    "stripe_color": (0.9, 0.9, 0.95, 1.0),  # Ventral white
    "pattern": "plain",
    "preferred_depth": "shallow-medium",
    "diet": "Planktivore",
    "spawn_locations": ["Surface Waters", "Reef Crest", "Cleaning Station"],
    "spawn_months": [3, 4, 5, 9, 10, 11],
    "base_behaviors": ["Gliding", "Loop_De_Loop", "Curious"],
    "features": [
        {"type": "eyes", "t": 0.06, "angle_deg": 75},
        {"type": "custom", "name": "cephalic_horns", "t": 0.02, "scale": 0.08, "scale_xyz": (0.5, 1.8, 0.5)},
        {"type": "custom", "name": "whip_tail", "t": 0.98, "scale": 0.8, "scale_xyz": (0.1, 1.5, 0.1)}
    ]
}

def get_body_vertex(t, angle, length):
    # Extremely wide flat body with sweep-back wings
    h_center = 0.05 * math.sin(t * math.pi) * length
    # Diamond-wing shape
    w = 0.85 * math.sin(t * math.pi) * (1.0 - 0.4 * t) * length
    z_off = 0.0
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x = w * cos_a
    # Taper wing thickness dramatically at the tips (edges)
    z = z_off + h_center * sin_a * (1.1 - 0.9 * abs(cos_a))
    y = -t * length
    return x, y, z
