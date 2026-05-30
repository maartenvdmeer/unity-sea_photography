import bpy

def apply_procedural_materials(obj, base_color=(0.1, 0.4, 0.8, 1.0), stripe_color=(0.9, 0.6, 0.1, 1.0), pattern_type="striped"):
    """
    Constructs high-fidelity procedural Blender shaders with color ramp bands or 
    voronoi patterns to render beautiful details without any external image textures.
    """
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
        
    # Input coordinates and mapping
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-200, 0)
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    
    # Color mixing node
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (150, 0)
    mix_rgb.inputs['Color1'].default_value = base_color
    mix_rgb.inputs['Color2'].default_value = stripe_color
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Apply selected dynamic pattern mask
    if pattern_type == "striped":
        # Wave texture generates clean vertical stripes along Y-axis
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (0, 100)
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'Y'
        wave.inputs['Scale'].default_value = 14.0
        wave.inputs['Distortion'].default_value = 1.5
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        
        # ColorRamp to sharpen the mask boundaries
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (0, -150)
        color_ramp.color_ramp.elements[0].position = 0.38
        color_ramp.color_ramp.elements[1].position = 0.58
        links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs['Fac'])
        
    elif pattern_type == "spotted":
        # Voronoi texture generates beautiful polka dot/leopard pattern spots
        voro = nodes.new(type='ShaderNodeTexVoronoi')
        voro.location = (0, 100)
        voro.voronoi_dimensions = '3D'
        voro.feature = 'F1'
        voro.distance = 'EUCLIDEAN'
        voro.inputs['Scale'].default_value = 18.0
        links.new(mapping.outputs['Vector'], voro.inputs['Vector'])
        
        # Sharpen spots
        math_node = nodes.new(type='ShaderNodeMath')
        math_node.location = (0, -150)
        math_node.operation = 'LESS_THAN'
        math_node.inputs[1].default_value = 0.38
        links.new(voro.outputs['Distance'], math_node.inputs[0])
        links.new(math_node.outputs['Value'], mix_rgb.inputs['Fac'])
        
    else: # Countershading / plain
        # Dark top back, light bottom belly shading (marine survival countershading)
        sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
        sep_xyz.location = (0, 0)
        links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])
        links.new(sep_xyz.outputs['Z'], mix_rgb.inputs['Fac'])
        
    # Assign compiled material to the mesh
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
        
    return mat
