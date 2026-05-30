from . import definitions
from . import cleanup
from . import shading
from . import models
from . import rigging

# Expose package operations for unified orchestration calls
SPECIES_TEMPLATES = definitions.SPECIES_TEMPLATES
LIFE_STAGES = definitions.LIFE_STAGES
bulk_cleanup = cleanup.bulk_cleanup
apply_procedural_materials = shading.apply_procedural_materials
create_procedural_fish_mesh = models.create_procedural_fish_mesh
rig_and_animate_fish = rigging.rig_and_animate_fish
