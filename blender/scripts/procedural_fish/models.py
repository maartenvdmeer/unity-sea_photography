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
    # DYNAMIC SURFACE ATTACHMENT OF EYES & FINS (MODULARIZED BY SPECIES)
    # ==============================================================================
    from .definitions import SPECIES_MODULES
    
    if species in SPECIES_MODULES and hasattr(SPECIES_MODULES[species], "create_features"):
        # Delegate feature creation cleanly to the dynamic species package
        components = SPECIES_MODULES[species].create_features(
            name, length, create_lowpoly_eye, create_lowpoly_fin
        )
    else:
        # Fallback to general generic fish templates if no module is loaded
        eye_t = 0.14
        eye_angle_left = math.radians(140)
        eye_angle_right = math.radians(40)
        eye_size = 0.045 * (length**0.75)
        
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
        
        # Default simple fin placement (Dorsal & Caudal)
        co_dorsal = definitions.get_body_vertex(species, 0.45, math.pi/2, length)
        dorsal = create_lowpoly_fin(f"{name}_Dorsal", "dorsal", size=length * 0.25)
        dorsal.location = co_dorsal
        components.append(dorsal)
        
        co_caudal = definitions.get_body_vertex(species, 0.98, math.pi/2, length)
        caudal = create_lowpoly_fin(f"{name}_Caudal", "caudal", size=length * 0.3)
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
