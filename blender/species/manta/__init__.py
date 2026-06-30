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
    "base_behaviors": ["Gliding", "Loop_De_Loop", "Curious"]
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

def create_features(name, length, create_lowpoly_eye, create_lowpoly_fin):
    components = []
    
    # Place Eyes perfectly on the head skin
    eye_t = 0.06
    eye_angle_left = math.radians(105)
    eye_angle_right = math.radians(75)
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
    
    # Cephalic horns at the head mouth edges
    horn_size = length * 0.08
    for side in [-1, 1]:
        # Place horns at front mouth surface edges (using symmetric angle values)
        angle = math.radians(65) if side == 1 else math.radians(115)
        co_horn = get_body_vertex(0.02, angle, length)
        # Use UV sphere scaled as horn base
        horn = create_lowpoly_eye(f"{name}_Horn_{'R' if side == 1 else 'L'}", size=horn_size)
        horn.location = co_horn
        horn.scale = (0.5, 1.8, 0.5) # stretch into horn shapes
        horn.rotation_euler = (math.radians(90), 0, math.radians(side * 15))
        components.append(horn)
        
    # Long thin whip tail on the caudal stalk
    co_tail = get_body_vertex(0.98, math.pi/2, length)
    tail = create_lowpoly_fin(f"{name}_Whip", "pelvic", size=length * 0.8)
    tail.location = co_tail
    tail.scale = (0.1, 1.5, 0.1) # Extrude long and spindly
    components.append(tail)
    
    return components
