import math

# ==============================================================================
# SPECIES ANATOMICAL PROFILES (HEIGHT / WIDTH / SPINAL OFFSET ALONG Y AXIS)
# "t" goes from 0.0 (snout) to 1.0 (tail end)
# ==============================================================================

def get_shark_profiles():
    # Streamlined fusiform shape, slightly thicker in first third
    height_profile = lambda t: 0.16 * math.sin(t**0.7 * math.pi)
    width_profile = lambda t: 0.10 * math.sin(math.sqrt(t) * math.pi)
    offset_profile = lambda t: -0.02 * t  # Slightly sloping down
    return height_profile, width_profile, offset_profile

def get_manta_profiles():
    # extremely wide flat body (wings are procedural pectoral structures)
    height_profile = lambda t: 0.05 * math.sin(t * math.pi)
    width_profile = lambda t: 0.95 * math.sin(t * math.pi)  # massive wide pectoral wings
    offset_profile = lambda t: 0.0
    return height_profile, width_profile, offset_profile

def get_whale_profiles():
    # Gigantic stocky bulk
    height_profile = lambda t: 0.28 * math.sin(t**0.5 * math.pi)
    width_profile = lambda t: 0.24 * math.sin(t**0.5 * math.pi)
    offset_profile = lambda t: 0.02 * math.sin(t * math.pi)
    return height_profile, width_profile, offset_profile

def get_cichlid_profiles():
    # Oval, tall & compressed side-to-side
    height_profile = lambda t: 0.40 * math.sin(t**0.8 * math.pi)
    width_profile = lambda t: 0.08 * math.sin(t * math.pi)  # Very laterally thin
    offset_profile = lambda t: 0.0
    return height_profile, width_profile, offset_profile

def get_algae_eater_profiles():
    # Flat underside (ventral), humped back, sucker mouth
    height_profile = lambda t: 0.12 * math.sin(t**1.4 * math.pi)
    width_profile = lambda t: 0.14 * math.sin(t * math.pi)
    # Negative offset to flatten the bottom of the fish
    offset_profile = lambda t: -0.06 * (1.0 - t)
    return height_profile, width_profile, offset_profile

# ==============================================================================
# SPECIES MASTER METADATA AND PROCEDURAL SETTINGS
# ==============================================================================

SPECIES_TEMPLATES = {
    "shark": {
        "name": "Reef Shark",
        "scientific_name": "Carcharhinus perezi",
        "description": "An active marine predator often found patrolling coral reefs. Fast swimmer.",
        "profile_func": get_shark_profiles,
        "base_length": 2.2,  # meters
        "base_color": (0.35, 0.42, 0.48, 1.0),  # Steel gray
        "stripe_color": (0.2, 0.23, 0.26, 1.0),
        "pattern": "plain",
        "preferred_depth": "medium-deep",
        "diet": "Carnivore",
        "spawn_locations": ["Reef Wall", "Deep Ocean", "Open Waters"],
        "spawn_months": [12, 1, 2, 6, 7, 8],  # Migration season
        "base_behaviors": ["Patrolling", "Investigative", "Schooling"]
    },
    "manta": {
        "name": "Giant Manta Ray",
        "scientific_name": "Mobula birostris",
        "description": "Gentle filter-feeding giants. Known for their graceful winged glides.",
        "profile_func": get_manta_profiles,
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
        "profile_func": get_whale_profiles,
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
        "profile_func": get_cichlid_profiles,
        "base_length": 0.12,  # cm-scale
        "base_color": (0.95, 0.45, 0.05, 1.0),  # Neon orange
        "stripe_color": (0.05, 1.0, 0.95, 1.0), # Electric cyan highlights
        "pattern": "striped",
        "preferred_depth": "shallow",
        "diet": "Herbivore / Algae Grater",
        "spawn_locations": ["Rocky Reefs", "Sandy Bays"],
        "spawn_months": [3, 4, 5, 6, 7, 8, 9],  # Spring and Summer breeding
        "base_behaviors": ["Territorial", "Nest_Digging", "Shy"]
    },
    "algae_eater": {
        "name": "Siamese Algae Eater",
        "scientific_name": "Crossocheilus oblongus",
        "description": "Equipped with a sucker mouth to scrape algae off rocky riverbeds and sea-bottom structures.",
        "profile_func": get_algae_eater_profiles,
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
# LIFE STAGE MORPHOLOGY ADJUSTER FOR GAME BALANCING AND VISUALS
# ==============================================================================

LIFE_STAGES = {
    "fry": {
        "scale_mod": 0.15,
        "speed_factor": 2.2,     # High-frequency fast swimming
        "eye_scale_mod": 1.5,    # Cute baby proportions (larger eyes relative to body)
        "behavior_mods": ["Cautious", "High_Schooling"],
        "social_cohesion": 0.9,  # Very tight groups
        "reactivity_multiplier": 2.0  # Runs away very fast when flashed
    },
    "juvenile": {
        "scale_mod": 0.45,
        "speed_factor": 1.4,
        "eye_scale_mod": 1.25,
        "behavior_mods": ["Playful", "Inquisitive"],
        "social_cohesion": 0.6,
        "reactivity_multiplier": 1.5
    },
    "mature_male": {
        "scale_mod": 1.0,
        "speed_factor": 1.0,
        "eye_scale_mod": 1.0,
        "behavior_mods": ["Territorial", "Displaying"],
        "social_cohesion": 0.1,  # Solitary or aggressive
        "reactivity_multiplier": 0.7  # Bold, stands ground
    },
    "mature_female": {
        "scale_mod": 1.1,        # Slightly robust body size for egg-carrying
        "speed_factor": 0.9,
        "eye_scale_mod": 1.0,
        "behavior_mods": ["Nesting", "Foraging"],
        "social_cohesion": 0.5,
        "reactivity_multiplier": 0.8
    }
}
