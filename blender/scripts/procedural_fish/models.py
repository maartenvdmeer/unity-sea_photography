import bpy
import bmesh
import math
import random
from . import definitions

def create_lowpoly_fin(name, fin_type="dorsal", size=1.0):
    """
    Creates a professionally sculpted, low-poly 3D fin geometry with thickness.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Coordinates of fin profile vertices
    # Profile goes from front-base, upward to tip, back-base, and returning
    verts = []
    if fin_type == "dorsal":
        # Swept backward shark-like dorsal
        verts_local = [
            (0.0, 0.0, 0.0),                     # 0: Front base
            (0.0, -size * 0.3, size * 0.45),     # 1: Mid leading edge
            (0.0, -size * 0.6, size * 0.8),      # 2: Tip
            (0.0, -size * 0.5, size * 0.35),     # 3: Trailing edge inside
            (0.0, -size * 0.45, 0.0),            # 4: Back base
        ]
    elif fin_type == "pectoral":
        # Wing-like pectoral fin
        verts_local = [
            (0.0, 0.0, 0.0),                     # 0: Joint base front
            (size * 0.65, -size * 0.3, -size * 0.1), # 1: Mid wing span
            (size * 1.1, -size * 0.6, -size * 0.2),  # 2: Outer wing tip
            (size * 0.7, -size * 0.4, -size * 0.15), # 3: Trimming edge
            (0.0, -size * 0.2, 0.0),             # 4: Joint base back
        ]
    elif fin_type == "caudal":
        # Elegant fork tail
        verts_local = [
            (0.0, 0.0, 0.0),                     # 0: Spine tip joint
            (0.0, -size * 0.25, size * 0.55),    # 1: Upper lobe mid
            (0.0, -size * 0.45, size * 0.9),     # 2: Upper tip
            (0.0, -size * 0.3, 0.0),             # 3: Fork notch inner
            (0.0, -size * 0.45, -size * 0.9),    # 4: Lower tip
            (0.0, -size * 0.25, -size * 0.55),   # 5: Lower lobe mid
        ]
    else: # Default pelvic/anal oval fin
        verts_local = [
            (0.0, 0.0, 0.0),
            (0.0, -size * 0.2, size * 0.3),
            (0.0, -size * 0.45, 0.0),
            (0.0, -size * 0.2, -size * 0.3),
        ]
        
    # Translate list of coords into 3D space and provide 3D thickness (X-extrusion)
    half_thickness = size * 0.02
    for v_co in verts_local:
        # Create left side vertex (-X)
        vl = bm.verts.new((-half_thickness, v_co[1], v_co[2]))
        # Create right side vertex (+X)
        vr = bm.verts.new((half_thickness, v_co[1], v_co[2]))
        verts.append((vl, vr))
        
    # Construct Faces (Quads along the side envelope, capped end faces)
    num_pts = len(verts_local)
    for i in range(num_pts - 1):
        v0_l, v0_r = verts[i]
        v1_l, v1_r = verts[i+1]
        
        # Left side face
        bm.faces.new((v0_l, v1_l, v1_r, v0_r)) # Bridge front
        
    # Back cap and front cap faces
    # Construct triangles or quads on Left lateral plane and Right lateral plane
    for s in [0, 1]: # s=0 for Left, s=1 for Right
        poly_verts = [verts[i][s] for i in range(num_pts)]
        if s == 0:
            poly_verts.reverse() # Secure correct counter-clockwise ordering for outer normal face
        bm.faces.new(poly_verts)
        
    # Smooth update normals
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    # Smooth shade
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_lowpoly_eye(name, size=0.04):
    """
    Creates a clean low-poly UV sphere eye.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=size)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_procedural_fish_mesh(name, length=1.0, species="generic"):
    """
    Creates a complete, realistic, beautifully integrated low-poly fish mesh.
    Computes body cross-sections and maps eyes and fins flawlessly.
    """
    # Create main body mesh and active object
    mesh = bpy.data.meshes.new(name + "_mesh")
    body_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(body_obj)
    
    # Initialize BMesh for the body
    bm = bmesh.new()
    
    rings = 18
    vertices_per_ring = 12
    ring_verts = []
    
    # Generate Concentric Rings using definitions surface equations
    for r in range(rings):
        t = r / (rings - 1) # Longitudinal coordinate (0.0 to 1.0)
        
        verts_in_ring = []
        for v in range(vertices_per_ring):
            angle = (v / vertices_per_ring) * 2 * math.pi
            
            # Map exact 3D coordinates based on anatomical profiles
            co = definitions.get_body_vertex(species, t, angle, length)
            vert = bm.verts.new(co)
            verts_in_ring.append(vert)
            
        ring_verts.append(verts_in_ring)
        
    # Build faces between rings (quads)
    for r in range(rings - 1):
        for v in range(vertices_per_ring):
            v0 = ring_verts[r][v]
            v1 = ring_verts[r][(v + 1) % vertices_per_ring]
            v2 = ring_verts[r + 1][(v + 1) % vertices_per_ring]
            v3 = ring_verts[r + 1][v]
            
            if r == 0:
                # Triangles at the front snout
                if v0 != v1:
                    bm.faces.new((v0, v2, v3))
            elif r == rings - 2:
                # Triangles at the rear tail
                if v2 != v3:
                    bm.faces.new((v0, v1, v3))
            else:
                bm.faces.new((v0, v1, v2, v3))
                
    # Remove duplicates and resolve mesh geometry
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    # Track all subcomponents to join
    components = []
    
    # ==============================================================================
    # DYNAMIC SURFACE ATTACHMENT OF EYES & FINS
    # ==============================================================================
    
    # 1. Place Eyes perfectly on the head skin
    if species == "manta":
        eye_t = 0.06
        eye_angle_left = math.radians(105)
        eye_angle_right = math.radians(75)
    elif species == "whale":
        eye_t = 0.12
        eye_angle_left = math.radians(100)
        eye_angle_right = math.radians(80)
    else: # shark, cichlid, algae_eater, generic
        eye_t = 0.14
        eye_angle_left = math.radians(140)
        eye_angle_right = math.radians(40)
    
    eye_size = 0.045 * (length**0.75) if species != "whale" else 0.12
    
    # Get exact surface coords on head
    co_eye_l = definitions.get_body_vertex(species, eye_t, eye_angle_left, length)
    co_eye_r = definitions.get_body_vertex(species, eye_t, eye_angle_right, length)
    
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
    
    # 2. Place Specialized Fins based on biological class
    if species == "shark":
        # Prominent Dorsal Fin
        co_dorsal = definitions.get_body_vertex(species, 0.44, math.pi/2, length)
        dorsal = create_lowpoly_fin(f"{name}_Dorsal", "dorsal", size=length * 0.32)
        dorsal.location = co_dorsal
        dorsal.rotation_euler = (math.radians(-10), 0, 0)
        components.append(dorsal)
        
        # Symmetrical Pectoral wing fins
        for side in [-1, 1]:
            co_pec = definitions.get_body_vertex(species, 0.30, 0 if side == 1 else math.pi, length)
            pec = create_lowpoly_fin(f"{name}_Pec_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.28)
            pec.location = co_pec
            # Rotates outward and backward
            pec.rotation_euler = (math.radians(15), math.radians(side * 40), math.radians(-side * 18))
            if side == -1:
                pec.scale.x = -1.0 # Mirror left side pectoral
            components.append(pec)
            
        # Large vertical caudal fin (centered on spinal channel)
        co_caudal = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        caudal = create_lowpoly_fin(f"{name}_Caudal", "caudal", size=length * 0.35)
        caudal.location = co_caudal
        components.append(caudal)
        
    elif species == "manta":
        # Manta rays have massive pectoral sweep wings as part of their body base mesh!
        # Let's add cephalic horns at the head mouth edges
        horn_size = length * 0.08
        for side in [-1, 1]:
            # Place horns at front mouth surface edges (using symmetric angle values)
            angle = math.radians(65) if side == 1 else math.radians(115)
            co_horn = definitions.get_body_vertex(species, 0.02, angle, length)
            horn = create_lowpoly_eye(f"{name}_Horn_{'R' if side == 1 else 'L'}", size=horn_size) # use UV sphere scaled as horn base
            horn.location = co_horn
            horn.scale = (0.5, 1.8, 0.5) # stretch into horn shapes
            horn.rotation_euler = (math.radians(90), 0, math.radians(side * 15))
            components.append(horn)
            
        # Long thin whip tail on the caudal stalk (centered on spinal channel)
        co_tail = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        tail = create_lowpoly_fin(f"{name}_Whip", "pelvic", size=length * 0.8)
        tail.location = co_tail
        tail.scale = (0.1, 1.5, 0.1) # Extrude long and spindly
        components.append(tail)
        
    elif species == "whale":
        # Small dorsal ridge
        co_dorsal = definitions.get_body_vertex(species, 0.68, math.pi/2, length)
        dorsal = create_lowpoly_fin(f"{name}_DorsalRidge", "dorsal", size=length * 0.12)
        dorsal.location = co_dorsal
        dorsal.scale = (0.5, 0.7, 0.2)
        components.append(dorsal)
        
        # Wide horizontal fluke centered on spinal channel
        co_caudal = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        fluke = create_lowpoly_fin(f"{name}_Fluke", "caudal", size=length * 0.18)
        fluke.location = co_caudal
        fluke.rotation_euler = (0, math.radians(90), 0) # Rotate caudal 90 deg around Y to make horizontal fluke!
        fluke.scale = (1.5, 1.0, 0.7)
        components.append(fluke)
        
        # Pectoral side flippers
        for side in [-1, 1]:
            co_pec = definitions.get_body_vertex(species, 0.32, 0 if side == 1 else math.pi, length)
            pec = create_lowpoly_fin(f"{name}_Flipper_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.16)
            pec.location = co_pec
            pec.rotation_euler = (math.radians(5), math.radians(side * 35), math.radians(-side * 10))
            if side == -1:
                pec.scale.x = -1.0
            components.append(pec)
            
    elif species == "cichlid":
        # Continuous thick dorsal fin spanning half the back
        co_dorsal = definitions.get_body_vertex(species, 0.50, math.pi/2, length)
        dorsal = create_lowpoly_fin(f"{name}_DorsalTall", "dorsal", size=length * 0.42)
        dorsal.location = co_dorsal
        dorsal.scale = (0.4, 1.4, 0.9) # stretch lengthwise
        components.append(dorsal)
        
        # Symmetrical pelvic/rib fin pair
        for side in [-1, 1]:
            co_pec = definitions.get_body_vertex(species, 0.32, 0 if side == 1 else math.pi, length)
            pec = create_lowpoly_fin(f"{name}_Pec_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.3)
            pec.location = co_pec
            pec.rotation_euler = (math.radians(10), math.radians(side * 15), math.radians(-side * 5))
            if side == -1:
                pec.scale.x = -1.0
            components.append(pec)
            
        # Large rounded fan-like tail (centered on spinal channel)
        co_caudal = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        caudal = create_lowpoly_fin(f"{name}_BroadTail", "caudal", size=length * 0.45)
        caudal.location = co_caudal
        caudal.scale = (0.5, 0.7, 1.2) # Make broad, vertical oval
        components.append(caudal)
        
    elif species == "algae_eater":
        # Humped back dorsal
        co_dorsal = definitions.get_body_vertex(species, 0.45, math.pi/2, length)
        dorsal = create_lowpoly_fin(f"{name}_Dorsal", "dorsal", size=length * 0.28)
        dorsal.location = co_dorsal
        components.append(dorsal)
        
        # Pelvic bottom brushes for scraping bottom walls
        for side in [-1, 1]:
            co_pec = definitions.get_body_vertex(species, 0.30, math.radians(-40) if side == 1 else math.radians(220), length)
            pec = create_lowpoly_fin(f"{name}_Pelvic_{'R' if side == 1 else 'L'}", "pectoral", size=length * 0.22)
            pec.location = co_pec
            # Angled down and slightly back
            pec.rotation_euler = (math.radians(-20), math.radians(side * 20), math.radians(-side * 45))
            if side == -1:
                pec.scale.x = -1.0
            components.append(pec)
            
        # Swept backward tail (centered on spinal channel)
        co_caudal = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        caudal = create_lowpoly_fin(f"{name}_ForkTail", "caudal", size=length * 0.32)
        caudal.location = co_caudal
        components.append(caudal)
        
    # ==============================================================================
    # THE CRITICAL WORKFLOW FIX: UNIFIED MESH JOIN & DOUBLE WELDING
    # ==============================================================================
    # Deselect all, then select main body and all procedural components
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    for comp in components:
        comp.select_set(True)
        
    # Set main body as the master active context object
    bpy.context.view_layer.objects.active = body_obj
    
    # Weld and Join separate elements into 1 single solid master mesh!
    bpy.ops.object.join()
    
    # Run absolute vertices double welding inside BMesh to complete watertight skin joins
    bm = bmesh.new()
    bm.from_mesh(body_obj.data)
    # Remove overlapping double vertices (threshold matches joint spacing)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.005)
    bm.to_mesh(body_obj.data)
    bm.free()
    
    # Recalculate smooth normals for clean low-poly surface shading
    body_obj.data.update()
    
    # Add Subdivision level LOD modifier (deactivated for gaming, enabled for rendering)
    subd = body_obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subd.levels = 1
    subd.render_levels = 2
    
    return body_obj
