import math
import os
import sys
import importlib

# Dynamic path resolution to locate the "species" directory
current_dir = os.path.dirname(os.path.abspath(__file__))
blender_dir = os.path.dirname(os.path.dirname(current_dir))
species_dir = os.path.join(blender_dir, "species")

if blender_dir not in sys.path:
    sys.path.insert(0, blender_dir)

# ==============================================================================
# SPECIES CONFIGURATION DATABASE
# ==============================================================================

SPECIES_TEMPLATES = {}
SPECIES_MODULES = {}

# List entries in species folder and dynamically load as modules
if os.path.exists(species_dir):
    for entry in os.listdir(species_dir):
        entry_path = os.path.join(species_dir, entry)
        if os.path.isdir(entry_path) and not entry.startswith("__"):
            init_file = os.path.join(entry_path, "__init__.py")
            if os.path.exists(init_file):
                try:
                    module_name = f"species.{entry}"
                    if module_name in sys.modules:
                        mod = importlib.reload(sys.modules[module_name])
                    else:
                        mod = importlib.import_module(module_name)
                    
                    SPECIES_MODULES[entry] = mod
                    if hasattr(mod, "TEMPLATE"):
                        SPECIES_TEMPLATES[entry] = mod.TEMPLATE
                except Exception as e:
                    print(f"Failed to dynamically load species module {entry}: {e}")

# ==============================================================================
# SPECIES ANATOMICAL SURFACE FUNCTIONS
# ==============================================================================

def get_body_vertex(species, t, angle, length):
    """
    Returns the (x, y, z) coordinate of a vertex on the body surface
    at longitudinal coordinate t (0=snout, 1=tail) and cross-section angle.
    """
    # 1. Try to delegate to species-specific module
    if species in SPECIES_MODULES and hasattr(SPECIES_MODULES[species], "get_body_vertex"):
        return SPECIES_MODULES[species].get_body_vertex(t, angle, length)
        
    # Default simple fish template (fallback)
    y = -t * length
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

