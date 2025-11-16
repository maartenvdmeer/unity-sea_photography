import bpy

def bulk_cleanup(prefixes=(), protected_names=()):
    # Accept a tuple of names to protect from deletion
    #protected_names = set(bulk_cleanup.protected_names) if hasattr(bulk_cleanup, 'protected_names') else set()

    # Only delete objects with specified prefixes, unless protected
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(prefix) for prefix in prefixes) and obj.name not in protected_names:
            # Unlink from all collections first
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)

    # Only remove collections with specified prefixes, unless protected
    for collection in list(bpy.data.collections):
        if any(collection.name.startswith(prefix) for prefix in prefixes) and collection.name not in protected_names:
            bpy.data.collections.remove(collection)

    # Only remove meshes, materials, textures, images with specified prefixes, unless protected
    for datablock in (bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images):
        for block in list(datablock):
            if any(block.name.startswith(prefix) for prefix in prefixes) and block.name not in protected_names:
                datablock.remove(block)

    # Remove node groups with specified prefixes, unless protected
    for ng in list(bpy.data.node_groups):
        if any(ng.name.startswith(prefix) for prefix in prefixes) and ng.name not in protected_names:
            bpy.data.node_groups.remove(ng, do_unlink=True)

    # Purge orphaned data blocks (gentle, only once)
    # bpy.ops.outliner.orphans_purge(do_recursive=True)

    print("Gentle cleanup complete")
