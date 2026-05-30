import bpy
import math

def create_bezier_curve(name, points, closed=False):
    """
    Creates a 3D bezier curve in the scene from a list of 3D coordinates.
    """
    # Create curve data
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12

    # Create new spline
    spline = curve_data.splines.new(type='BEZIER')
    spline.use_cyclic_u = closed

    # Allocate bezier points
    spline.bezier_points.add(len(points) - 1)

    # Set point coordinates and handles
    for i, pt in enumerate(points):
        bezier_point = spline.bezier_points[i]
        # Coordinates must be 3-tuples
        coord = (pt[0], pt[1], pt[2] if len(pt) > 2 else 0.0)
        bezier_point.co = coord
        # Set handle type to automatic for smooth curves
        bezier_point.handle_left_type = 'AUTO'
        bezier_point.handle_right_type = 'AUTO'

    # Create object
    curve_obj = bpy.data.objects.new(name + "_obj", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    return curve_obj

def generate_profile_curve(name, length=1.0, mid_height=0.3, width=0.15):
    """
    Generates a standard fish body silhouette profile.
    From nose (0,0) to tail (length, 0), with a belly and back curve.
    """
    # Create top curve points (back)
    back_points = [
        (0.0, 0.0, 0.0),
        (length * 0.1, width * 0.5, mid_height * 0.3),
        (length * 0.4, width, mid_height),
        (length * 0.7, width * 0.6, mid_height * 0.5),
        (length, 0.0, 0.0)
    ]
    
    # Create bottom curve points (belly)
    belly_points = [
        (0.0, 0.0, -0.0),
        (length * 0.15, width * 0.5, -mid_height * 0.4),
        (length * 0.45, width, -mid_height * 0.9),
        (length * 0.75, width * 0.4, -mid_height * 0.3),
        (length, 0.0, -0.0)
    ]
    
    back_curve = create_bezier_curve(name + "_back", back_points)
    belly_curve = create_bezier_curve(name + "_belly", belly_points)
    
    return back_curve, belly_curve

def create_fin_bezier(name, fin_type="dorsal", size=1.0):
    """
    Creates specialized bezier curves to serve as profiles for different fin shapes.
    """
    points = []
    if fin_type == "dorsal":
        # Shark-like tall swept-back dorsal fin
        points = [
            (0.0, 0.0, 0.0),
            (size * 0.2, 0.0, size * 0.6),
            (size * 0.5, 0.0, size * 1.0),
            (size * 0.4, 0.0, size * 0.4),
            (size * 0.7, 0.0, 0.0)
        ]
    elif fin_type == "pectoral":
        # Triangular wing-like pectoral fin
        points = [
            (0.0, 0.0, 0.0),
            (size * 0.6, size * -0.8, size * -0.2),
            (size * 1.0, size * -1.2, size * -0.4),
            (size * 0.7, size * -0.6, size * -0.3),
            (size * 0.4, size * -0.2, 0.0)
        ]
    elif fin_type == "caudal":
        # Forked classic tail-fin (cichlid/shark back tail)
        points = [
            (0.0, 0.0, 0.0),
            (size * 0.4, 0.0, size * 0.5),
            (size * 0.6, 0.0, size * 0.8),
            (size * 0.3, 0.0, 0.0),
            (size * 0.6, 0.0, -size * 0.8),
            (size * 0.4, 0.0, -size * 0.5),
            (0.0, 0.0, 0.0)
        ]
    else: # Default oval fin
        points = [
            (0.0, 0.0, 0.0),
            (size * 0.3, 0.0, size * 0.4),
            (size * 0.6, 0.0, 0.0),
            (size * 0.3, 0.0, -size * 0.4),
            (0.0, 0.0, 0.0)
        ]
        
    fin_curve = create_bezier_curve(name + "_" + fin_type, points, closed=True)
    return fin_curve
