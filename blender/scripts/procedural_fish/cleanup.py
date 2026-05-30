import bpy

def bulk_cleanup(prefixes=("Fish_", "Rig_"), protected_names=("Default_Camera", "Default_Light")):
    """
    Cleans up old, temporary procedural objects, meshes, materials, and rigs from the active scene.
    Prevents duplicate accumulations and keeps memory use incredibly low.
    """
    # 1. Unlink and remove legacy objects
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(prefix) for prefix in prefixes) and obj.name not in protected_names:
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
            
    # 2. Remove isolated assemblies (meshes, materials, armature rigs, and textures)
    for collection in list(bpy.data.collections):
        if any(collection.name.startswith(prefix) for prefix in prefixes) and collection.name not in protected_names:
            bpy.data.collections.remove(collection, do_unlink=True)
            
    for mesh in list(bpy.data.meshes):
        if any(mesh.name.startswith(prefix) for prefix in prefixes) and mesh.name not in protected_names:
            bpy.data.meshes.remove(mesh, do_unlink=True)
            
    for mat in list(bpy.data.materials):
        if any(mat.name.startswith(prefix) for prefix in prefixes) and mat.name not in protected_names:
            bpy.data.materials.remove(mat, do_unlink=True)
            
    for arm in list(bpy.data.armatures):
        if any(arm.name.startswith(prefix) for prefix in prefixes) and arm.name not in protected_names:
            bpy.data.armatures.remove(arm, do_unlink=True)
            
    print("Sequential scene cleanup executed successfully!")
