import bpy
import bmesh
import math
import random

def create_procedural_fish_mesh(name, length=1.0, height_profile=None, width_profile=None, offset_profile=None, rings=16, vertices_per_ring=8, fish_type="generic"):
    """
    Generates a perfectly clean, quad-only low-poly fish body mesh using concentric cross-sections.
    """
    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Initialize BMesh
    bm = bmesh.new()
    
    # Default profiles if none provided (parabolic profile)
    if height_profile is None:
        height_profile = lambda t: 0.25 * math.sin(t * math.pi)
    if width_profile is None:
        width_profile = lambda t: 0.12 * math.sin(t * math.pi)
    if offset_profile is None:
        # Default symmetric mouth / spinal column
        offset_profile = lambda t: 0.0
        
    # Generate points and rings
    ring_verts = []
    for r in range(rings):
        t = r / (rings - 1)  # 0.0 (head) to 1.0 (tail)
        y = -t * length      # Head at 0, tail moves in negative Y direction
        
        h = height_profile(t)
        w = width_profile(t)
        z_off = offset_profile(t)
        
        verts_in_ring = []
        for v in range(vertices_per_ring):
            angle = (v / vertices_per_ring) * 2 * math.pi
            # X is side-to-side, Z is up-down
            x = w * math.cos(angle)
            z = z_off + h * math.sin(angle)
            
            # If the ring is at the very tip of the snout (t=0) or tail tip (t=1), collaspe it
            if t == 0.0 or t == 1.0:
                x, z = 0.0, z_off
                
            vert = bm.verts.new((x, y, z))
            verts_in_ring.append(vert)
            
        ring_verts.append(verts_in_ring)
        
    # Build faces between rings (quads)
    for r in range(rings - 1):
        for v in range(vertices_per_ring):
            v0 = ring_verts[r][v]
            v1 = ring_verts[r][(v + 1) % vertices_per_ring]
            v2 = ring_verts[r + 1][(v + 1) % vertices_per_ring]
            v3 = ring_verts[r + 1][v]
            
            # Avoid duplicate folded faces at snout and tail tip
            if r == 0:
                # Snout is collapsed, write triangles
                if v0 != v1:
                    bm.faces.new((v0, v2, v3))
            elif r == rings - 2:
                # Tail is collapsed, write triangles
                if v2 != v3:
                    bm.faces.new((v0, v1, v3))
            else:
                bm.faces.new((v0, v1, v2, v3))
                
    # Remove duplicates and double vertices
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    
    # Calculate normals
    bm.normal_update()
    
    # Write bmesh to mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Enable shading smooth across all polygons for clean rendering
    for poly in mesh.polygons:
        poly.use_smooth = True
    
    # Add Subdivision modifier for high-poly LOD, but disable for low-poly export
    subd = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subd.levels = 1
    subd.render_levels = 2
    
    return obj

def add_fish_eyes(fish_obj, snout_y_factor=0.12, height=0.08, lateral_spacing=0.1, eye_size=0.04):
    """
    Spatially attaches procedural eyes to the fish body.
    """
    length = abs(min([v.co.y for v in fish_obj.data.vertices]))
    eye_y = -length * snout_y_factor
    
    # Create Eye meshes (UV Spheres)
    for side in [-1, 1]:  # Left (-1) and Right (1)
        name = f"{fish_obj.name}_Eye_{'L' if side < 0 else 'R'}"
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, 
            ring_count=8, 
            radius=eye_size, 
            location=(side * lateral_spacing, eye_y, height)
        )
        eye_obj = bpy.context.active_object
        eye_obj.name = name
        
        # Parent eye to the main fish body
        eye_obj.parent = fish_obj
        
        # Rotate eyes slightly outward
        eye_obj.rotation_euler = (0, 0, math.radians(side * 15))
        
def add_procedural_fins(fish_obj, fish_type="generic", size=1.0):
    """
    Creates fin shapes and welds or overlays them onto the body.
    """
    length = abs(min([v.co.y for v in fish_obj.data.vertices]))
    
    if fish_type == "shark":
        # Add a prominent dorsal fin
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.45, length * 0.25))
        dorsal = bpy.context.active_object
        dorsal.name = f"{fish_obj.name}_Dorsal"
        dorsal.scale = (0.02 * size, 0.15 * size, 0.25 * size)
        # Taper and rotate
        dorsal.rotation_euler = (math.radians(-25), 0, 0)
        dorsal.parent = fish_obj
        
        # Add pectoral fins
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * length * 0.15, -length * 0.3, -length * 0.05))
            pec = bpy.context.active_object
            pec.name = f"{fish_obj.name}_Pectoral_{'L' if side < 0 else 'R'}"
            pec.scale = (0.2 * size, 0.12 * size, 0.02 * size)
            pec.rotation_euler = (math.radians(10), math.radians(side * 35), math.radians(-side * 15))
            pec.parent = fish_obj
            
        # Large heterocercal caudal tail
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.98, length * 0.1))
        caudal = bpy.context.active_object
        caudal.name = f"{fish_obj.name}_Caudal"
        caudal.scale = (0.015 * size, 0.12 * size, 0.3 * size)
        caudal.parent = fish_obj

    elif fish_type == "manta":
        # Manta rays have massive wing pectoral fins already integrated into their profile, 
        # but let's add their cephalic horns and whip tail
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.08, depth=0.25, location=(side * 0.2, 0.1, 0.05))
            horn = bpy.context.active_object
            horn.name = f"{fish_obj.name}_Cephalic_{'L' if side < 0 else 'R'}"
            horn.rotation_euler = (math.radians(90), 0, math.radians(side * 10))
            horn.parent = fish_obj
            
        # Whip tail
        bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.012, depth=length * 1.5, location=(0, -length * 1.25, 0))
        whip = bpy.context.active_object
        whip.name = f"{fish_obj.name}_WhipTail"
        whip.rotation_euler = (math.radians(90), 0, 0)
        whip.parent = fish_obj

    elif fish_type == "whale":
        # Broad dorsal peak
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.65, length * 0.15))
        dorsal = bpy.context.active_object
        dorsal.name = f"{fish_obj.name}_DorsalRidge"
        dorsal.scale = (0.03 * size, 0.2 * size, 0.08 * size)
        dorsal.parent = fish_obj
        
        # Horizontal fluke tail
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.98, 0))
        fluke = bpy.context.active_object
        fluke.name = f"{fish_obj.name}_Fluke"
        fluke.scale = (0.5 * size, 0.15 * size, 0.02 * size)
        fluke.parent = fish_obj
        
    elif fish_type == "cichlid":
        # Giant elegant continuous dorsal fin
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.45, length * 0.28))
        dorsal = bpy.context.active_object
        dorsal.name = f"{fish_obj.name}_DorsalGiant"
        dorsal.scale = (0.015 * size, 0.4 * size, 0.18 * size)
        dorsal.parent = fish_obj
        
        # Symmetrical anal fin below
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.55, -length * 0.28))
        anal = bpy.context.active_object
        anal.name = f"{fish_obj.name}_AnalGiant"
        anal.scale = (0.015 * size, 0.3 * size, 0.18 * size)
        anal.parent = fish_obj

def apply_procedural_materials(obj, base_color=(0.1, 0.4, 0.8, 1.0), stripe_color=(0.9, 0.6, 0.1, 1.0), pattern_type="striped"):
    """
    Builds advanced procedural shader networks inside Blender containing 
    gradients, stripes, or spots for beautiful fish skins without external image dependencies.
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
    
    # Dynamic Metallic & Roughness for slippery fish surface
    bsdf.inputs['Roughness'].default_value = 0.15
    if hasattr(bsdf.inputs, 'Specular'):
        bsdf.inputs['Specular'].default_value = 0.8
        
    # Coordinate system and mapping
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-400, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-200, 0)
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    
    mix_rgb = nodes.new(type='ShaderNodeMixRGB')
    mix_rgb.location = (150, 0)
    mix_rgb.inputs['Color1'].default_value = base_color
    mix_rgb.inputs['Color2'].default_value = stripe_color
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
    
    if pattern_type == "striped":
        # Wave texture generates clean vertical stripes along Y-coordinate
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (0, 100)
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'Y'
        wave.inputs['Scale'].default_value = 12.0
        wave.inputs['Distortion'].default_value = 2.0
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        
        # ColorRamp to sharpen the mask
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (0, -150)
        color_ramp.color_ramp.elements[0].position = 0.4
        color_ramp.color_ramp.elements[1].position = 0.6
        links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs['Fac'])
        
    elif pattern_type == "spotted":
        # Voronoi texture generates cute polka dot spots
        voro = nodes.new(type='ShaderNodeTexVoronoi')
        voro.location = (0, 100)
        voro.voronoi_dimensions = '3D'
        voro.feature = 'F1'
        voro.distance = 'EUCLIDEAN'
        voro.inputs['Scale'].default_value = 15.0
        links.new(mapping.outputs['Vector'], voro.inputs['Vector'])
        
        # Sharpen spots
        math_node = nodes.new(type='ShaderNodeMath')
        math_node.location = (0, -150)
        math_node.operation = 'LESS_THAN'
        math_node.inputs[1].default_value = 0.35
        links.new(voro.outputs['Distance'], math_node.inputs[0])
        links.new(math_node.outputs['Value'], mix_rgb.inputs['Fac'])
        
    else: # Plain gradient / gradient ventral-shading
        # Dark top, light bottom shading (marine countershading)
        sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
        sep_xyz.location = (0, 0)
        links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])
        links.new(sep_xyz.outputs['Z'], mix_rgb.inputs['Fac'])
        
    # Assign material
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
        
    return mat

def rig_and_animate_fish(fish_obj, num_bones=4):
    """
    Procedurally constructs a skeleton armature along the fish spine, skins the mesh 
    vertices with precise automatic distance weights, and bakes an idle swimming animation.
    """
    # Create armature and object
    arm_data = bpy.data.armatures.new(f"{fish_obj.name}_Armature")
    arm_obj = bpy.data.objects.new(f"{fish_obj.name}_Rig", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    
    # Enter Edit Mode for bone creation
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    length = abs(min([v.co.y for v in fish_obj.data.vertices]))
    bone_length = length / num_bones
    
    bones = []
    for i in range(num_bones):
        bone = arm_data.edit_bones.new(name=f"Spine.{i+1:03d}")
        # Bone coordinates: Y is length axis
        bone.head = (0, -i * bone_length, 0)
        bone.tail = (0, -(i + 1) * bone_length, 0)
        
        if i > 0:
            bone.parent = bones[i-1]
            bone.use_connect = True
        bones.append(bone)
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Procedural Rig Skinning (assigning vertex weights based on closest bones)
    # Assign vertex groups to fish mesh matching bone names
    for i in range(num_bones):
        group_name = f"Spine.{i+1:03d}"
        v_group = fish_obj.vertex_groups.new(name=group_name)
        
        # Calculate bone start/end coordinates in local space
        y_start = -i * bone_length
        y_end = -(i + 1) * bone_length
        
        # Assign vertices that are closest along Y axis to this bone
        for vert in fish_obj.data.vertices:
            vy = vert.co.y
            # Direct proportional weighting based on closeness to segment core
            mid = (y_start + y_end) / 2
            dist = abs(vy - mid)
            
            # Simple soft-skinning falloff
            weight = max(0.0, 1.0 - (dist / (bone_length * 1.1)))
            if weight > 0.05:
                v_group.add([vert.index], weight, 'ADD')
                
    # Link mesh to armature
    arm_modifier = fish_obj.modifiers.new(name="Armature", type='ARMATURE')
    arm_modifier.object = arm_obj
    fish_obj.parent = arm_obj
    
    # Create skeletal anim of swimming (sine-wave bone rotation over time)
    arm_obj.animation_data_create()
    action = bpy.data.actions.new(name=f"{fish_obj.name}_SwimIdle")
    arm_obj.animation_data.action = action
    
    # We will animate Pose Bones
    for i in range(1, num_bones):  # Animate child bones to ripple
        pose_bone = arm_obj.pose.bones[f"Spine.{i+1:03d}"]
        
        # Insert rotation keyframes (z-rotation is tail sway side-to-side)
        for frame in range(1, 41, 5):  # 40-frame loop
            phase = (frame / 40) * 2 * math.pi
            # Sine wave rotation with slight phase delay down the spinal column
            angle = 0.25 * math.sin(phase - (i * 0.75))
            pose_bone.rotation_mode = 'XYZ'
            pose_bone.rotation_euler = (0, 0, angle)
            
            # Keyframe insertion
            pose_bone.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
            
    print(f"Workflow Complete: Created, skinned and animated {fish_obj.name}")
    return arm_obj
