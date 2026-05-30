import bpy
import math

def rig_and_animate_fish(fish_obj, num_bones=5):
    """
    Procedurally builds a longitudinal spine bone-chain armature, skins the entire mesh
    (including the integrated eyes and fins!) with soft falloff weights, and bakes
    a clean cyclical side-to-side swimming motion.
    """
    # Create armature and object
    arm_data = bpy.data.armatures.new(f"{fish_obj.name}_Armature")
    arm_obj = bpy.data.objects.new(f"{fish_obj.name}_Rig", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    
    # Enter Edit Mode for bone scaffolding
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Determine absolute length along longitudinal axis Y (min Y is the tail tip)
    length = abs(min([v.co.y for v in fish_obj.data.vertices]))
    bone_length = length / num_bones
    
    bones = []
    for i in range(num_bones):
        bone_name = f"Spine.{i+1:03d}"
        bone = arm_data.edit_bones.new(name=bone_name)
        
        # Bones stretch along the negative Y axis path
        bone.head = (0, -i * bone_length, 0)
        bone.tail = (0, -(i + 1) * bone_length, 0)
        
        # Sockets
        if i > 0:
            bone.parent = bones[i-1]
            bone.use_connect = True
        bones.append(bone)
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # ==============================================================================
    # DYNAMIC SKIN WEIGHTING OF THE UNIFIED MESH (BODY + EYES + FINS)
    # ==============================================================================
    # Since eyes and fins are now completely joined and welded inside fish_obj,
    # we can skin all vertices in one single soft distance falloff pass!
    for i in range(num_bones):
        group_name = f"Spine.{i+1:03d}"
        v_group = fish_obj.vertex_groups.new(name=group_name)
        
        # Center of current bone segment along Y axis
        y_start = -i * bone_length
        y_end = -(i + 1) * bone_length
        bone_center = (y_start + y_end) / 2
        
        # Assign weights based on vertex closeness along Y axis
        for vert in fish_obj.data.vertices:
            vy = vert.co.y
            dist = abs(vy - bone_center)
            
            # Simple parabolic falloff weighting
            weight = max(0.0, 1.0 - (dist / (bone_length * 1.2)))
            if weight > 0.02:
                v_group.add([vert.index], weight, 'ADD')
                
    # Link mesh to the spine rigs
    arm_modifier = fish_obj.modifiers.new(name="Armature", type='ARMATURE')
    arm_modifier.object = arm_obj
    fish_obj.parent = arm_obj
    
    # ==============================================================================
    # PROCEDURAL ANIMATION BAKING
    # ==============================================================================
    # Initialize animation tracks
    arm_obj.animation_data_create()
    action = bpy.data.actions.new(name=f"{fish_obj.name}_SwimIdle")
    arm_obj.animation_data.action = action
    
    # Animate Pose Bones with side-to-side sin waves
    # We delay the phase down the spine to create a realistic organic ripple!
    for i in range(num_bones):
        bone_name = f"Spine.{i+1:03d}"
        pose_bone = arm_obj.pose.bones[bone_name]
        pose_bone.rotation_mode = 'XYZ'
        
        for frame in range(1, 41, 2): # 40-frame loop, step 2 for compact curves
            phase = (frame / 40) * 2 * math.pi
            
            # Sin swaying. Head (bone 0) rotates very little, tail (last bone) rotates the most!
            amplitude = (i / (num_bones - 1)) * 0.28 if num_bones > 1 else 0.15
            # Phase shift: delays sway along body for undulating rippling waves
            phase_delay = i * 0.65
            angle = amplitude * math.sin(phase - phase_delay)
            
            pose_bone.rotation_euler = (0, 0, angle)
            pose_bone.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
            
    print(f"Rigging completed successfully: Rigged and keyframed {num_bones} spine bones on {fish_obj.name}")
    return arm_obj
