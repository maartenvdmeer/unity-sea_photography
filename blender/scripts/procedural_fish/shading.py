import bpy
import math
import random
from . import definitions

def assign_mesh_vertex_colors(obj, base_color, stripe_color, pattern_type, species, length):
    """
    Procedurally paints vertex colors (displayColor) onto the welded low-poly mesh,
    delivering instant high-contrast visual markings in BOTH Unity and Omniverse/Isaac Sim!
    """
    mesh = obj.data
    
    # 1. Clean existing color layers
    if hasattr(mesh, "color_attributes"):
        while mesh.color_attributes:
            mesh.color_attributes.remove(mesh.color_attributes[0])
    if hasattr(mesh, "vertex_colors"):
        while mesh.vertex_colors:
            mesh.vertex_colors.remove(mesh.vertex_colors[0])
            
    # Deterministic spots generation
    spots_centers = []
    if pattern_type == "spotted":
        rand = random.Random(12345)
        
        # Default spots config (with fallback to hardcoded whale values if module not present)
        num_spots = 55 if species == "whale" else 25
        spot_radius = length * 0.024 if species == "whale" else length * 0.05
        
        # Check custom configuration from species-specific module
        from .definitions import SPECIES_MODULES
        if species in SPECIES_MODULES:
            mod = SPECIES_MODULES[species]
            if hasattr(mod, "NUM_SPOTS"):
                num_spots = mod.NUM_SPOTS
            if hasattr(mod, "SPOT_RADIUS_FACTOR"):
                spot_radius = length * mod.SPOT_RADIUS_FACTOR
        
        for _ in range(num_spots):
            t = rand.uniform(0.12, 0.88)
            angle = rand.uniform(-math.pi * 0.72, math.pi * 0.72)
            co = definitions.get_body_vertex(species, t, angle, length)
            spots_centers.append((co, spot_radius))
            
    stripe_freq = 15.0 / length if length > 0 else 15.0
    
    # Map vertex colors to all vertices
    vert_colors = []
    for idx, vert in enumerate(mesh.vertices):
        co = vert.co
        color = list(base_color)
        
        if pattern_type == "striped":
            val = math.sin(-co.y * stripe_freq + 2.0 * math.sin(co.x * 2.5))
            if val > 0.05:
                color = list(stripe_color)
        elif pattern_type == "spotted":
            in_spot = False
            for spot_co, rad in spots_centers:
                dx = co.x - spot_co[0]
                dy = co.y - spot_co[1]
                dz = co.z - spot_co[2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist < rad:
                    in_spot = True
                    break
            if in_spot:
                color = list(stripe_color)
        else: # Countershading for plain
            # Map Z height to a smooth color blend (dark on top, light on bottom)
            factor = 1.0 / (1.0 + math.exp(-co.z * 12.0 / length)) if length > 0 else 0.5
            color = [base_color[s] * factor + stripe_color[s] * (1.0 - factor) for s in range(4)]
            
        vert_colors.append(color)

    # Apply colors via Blender 3.2+ Color Attributes API
    if hasattr(mesh, "color_attributes"):
        try:
            color_layer = mesh.color_attributes.new(
                name="displayColor", # standard USD / Omniverse display color layer name
                type='FLOAT_COLOR',
                domain='POINT'
            )
            for idx, color in enumerate(vert_colors):
                color_layer.data[idx].color = color
            return
        except Exception:
            pass
            
    # Fallback to Loop-based vertex colors for older APIs
    try:
        color_layer = mesh.vertex_colors.new(name="displayColor")
        for loop in mesh.loops:
            color_layer.data[loop.index].color = vert_colors[loop.vertex_index]
    except Exception as ex:
        print(f"Vertex color painting failed: {ex}")

def apply_procedural_materials(obj, base_color=(0.1, 0.4, 0.8, 1.0), stripe_color=(0.9, 0.6, 0.1, 1.0), pattern_type="striped", species="generic", length=1.0):
    """
    Constructs high-fidelity shaders linked to vertex color attributes,
    ensuring beautiful markings on body models in both export formats (USD, FBX) and Blender.
    """
    # 1. Paint Vertex Colors directly onto the mesh for USD/FBX export compatibility
    assign_mesh_vertex_colors(obj, base_color, stripe_color, pattern_type, species, length)

    mat = bpy.data.materials.new(name=f"{obj.name}_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create Principled BSDF & Material Output
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Slippery glossy marine surface settings
    bsdf.inputs['Roughness'].default_value = 0.12
    if hasattr(bsdf.inputs, 'Specular'):
        bsdf.inputs['Specular'].default_value = 0.85
        
    # Standard: Link Painted Vertex Colors to BSDF Base Color!
    color_attr = None
    for node_type in ['ShaderNodeVertexColor', 'ShaderNodeColorAttribute', 'ShaderNodeAttribute']:
        try:
            color_attr = nodes.new(type=node_type)
            if node_type == 'ShaderNodeAttribute':
                color_attr.attribute_name = "displayColor"
            else:
                color_attr.layer_name = "displayColor"
            break
        except RuntimeError:
            continue
            
    if color_attr is not None:
        color_attr.location = (150, 0)
        links.new(color_attr.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        # Absolute fallback if no attribute node is available
        bsdf.inputs['Base Color'].default_value = base_color
    
    # Assign compiled material to the mesh
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
        
    return mat
