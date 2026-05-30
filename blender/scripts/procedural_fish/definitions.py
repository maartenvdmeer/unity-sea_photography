import math

# ==============================================================================
# SPECIES ANATOMICAL SURFACE FUNCTIONS
# ==============================================================================

def get_body_vertex(species, t, angle, length):
    """
    Returns the (x, y, z) coordinate of a vertex on the body surface
    at longitudinal coordinate t (0=snout, 1=tail) and cross-section angle.
    """
    y = -t * length
    
    if species == "shark":
        # Streamlined fusiform shape
        h = 0.16 * math.sin(t**0.75 * math.pi) * length
        w = 0.12 * math.sin(t**0.75 * math.pi) * length
        z_off = -0.012 * t * length
        
        # Ellipse-based cross-section with slightly flattened belly
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        x = w * cos_a
        z = z_off + h * sin_a * (1.0 if sin_a >= 0 else 0.8)
        
    elif species == "manta":
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
        
    elif species == "whale":
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
            
    elif species == "cichlid":
        # Lateral compressed, tall oval
        h = 0.34 * math.sin(t**0.8 * math.pi) * length
        w = 0.075 * math.sin(t * math.pi) * length
        z_off = 0.0
        
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        x = w * cos_a
        z = z_off + h * sin_a
        
    elif species == "algae_eater":
        # Flat bottom with sucker mouth alignment
        h = 0.10 * math.sin(t**1.1 * math.pi) * length
        w = 0.13 * math.sin(t**0.85 * math.pi) * length
        z_off = -h * 0.3
        
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        x = w * cos_a
        # Flatten belly
        z = z_off + h * sin_a * (1.0 if sin_a >= 0 else 0.25)
        
    else:
        # Default simple fish template
        h = 0.18 * math.sin(t * math.pi) * length
        w = 0.09 * math.sin(t * math.pi) * length
        z_off = 0.0
        x = w * math.cos(angle)
        z = z_off + h * math.sin(angle)
        
    # Collapse tips to perfect clean single vertex coordinates
    if t <= 0.001:
        return 0.0, 0.0, z_off
    if t >= 0.999:
        return 0.0, -length, z_off
        
    return x, y, z

# ==============================================================================
# SPECIES CONFIGURATION DATABASE
# ==============================================================================

SPECIES_TEMPLATES = {
    "shark": {
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
    },
    "manta": {
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
    },
    "whale": {
        "name": "Blue Whale",
        "scientific_name": "Balaenoptera musculus",
        "description": "The largest creature to inhabit Earth. Moves slowly and makes massive sound calls.",
        "base_length": 15.0,
        "base_color": (0.24, 0.32, 0.40, 1.0),  # Mottled blue-gray
        "stripe_color": (0.42, 0.50, 0.58, 1.0),
        "pattern": "spotted",
        "preferred_depth": "deep",
        "diet": "Planktivore",
        "spawn_locations": ["Abyssal Trench", "Open Waters"],
        "spawn_months": [1, 2, 7, 8],
        "base_behaviors": ["Slow_Cruise", "Deep_Dive", "Singing"]
    },
    "cichlid": {
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
    },
    "algae_eater": {
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
}

# ==============================================================================
# LIFE STAGE MORPHOLOGY
# ==============================================================================

LIFE_STAGES = {
    "fry": {
        "scale_mod": 0.15,
        "speed_factor": 2.2,
        "eye_scale_mod": 1.6,
        "behavior_mods": ["Cautious", "High_Schooling"],
        "social_cohesion": 0.9,
        "reactivity_multiplier": 2.0
    },
    "juvenile": {
        "scale_mod": 0.45,
        "speed_factor": 1.4,
        "eye_scale_mod": 1.3,
        "behavior_mods": ["Playful", "Inquisitive"],
        "social_cohesion": 0.6,
        "reactivity_multiplier": 1.5
    },
    "mature_male": {
        "scale_mod": 1.0,
        "speed_factor": 1.0,
        "eye_scale_mod": 1.0,
        "behavior_mods": ["Territorial", "Displaying"],
        "social_cohesion": 0.1,
        "reactivity_multiplier": 0.7
    },
    "mature_female": {
        "scale_mod": 1.1,
        "speed_factor": 0.9,
        "eye_scale_mod": 1.0,
        "behavior_mods": ["Nesting", "Foraging"],
        "social_cohesion": 0.5,
        "reactivity_multiplier": 0.8
    }
}
