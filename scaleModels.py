import bpy, os
import bmesh
import math
import mathutils


def clear_objects():
    for obj in bpy.data.objects:
        bpy.context.scene.objects.unlink(obj)
        obj.user_clear()
        bpy.data.objects.remove(obj)
    for me in bpy.data.meshes:
        me.user_clear()
        bpy.data.meshes.remove(me)

    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)

    for texture in bpy.data.textures:
        if not texture.users:
            bpy.data.textures.remove(texture)


def save_scaled_objects(dir_source, dir_target, dir_fbx, scale=1.0):
    dir_root = bpy.path.abspath("//")
    path_origin = bpy.data.filepath

    d_source = os.path.join(dir_root, dir_source)
    d_target = os.path.join(dir_root, dir_target)
    d_fbx = os.path.join(dir_root, dir_fbx)

    files = os.listdir(dir_source)

    scn = bpy.context.scene

    for f in files:
        input_filepath = os.path.join(d_source, f)
        output_filepath = os.path.join(d_target, f)

        # output_fbx = os.path.join(d_fbx, os.path.splitext(f)[0] + ".fbx")
        # print("DIR", output_fbx)

        # append object data block
        with bpy.data.libraries.load(input_filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        # link all objects to current scene
        for obj in data_to.objects:
            if obj is not None:
                scn.objects.link(obj)
                if obj.type == 'MESH':
                    # scale the objects data
                    # scale = 0.025
                    for v in obj.data.vertices:
                        v.co *= scale
        print(output_filepath)
        # saves the file
        bpy.ops.wm.save_mainfile(filepath=output_filepath)
        # export to fbx
        # bpy.ops.export_scene.fbx(filepath = output_fbx)

        clear_objects()
    # on completion of all saves, restore the original path of this file
    # bpy.ops.wm.save_mainfile(filepath=path_origin)


source_dir = "original"
target_dir = "scaled"
fbx_dir = "fbx_export"
obj_scale = 0.025
save_scaled_objects(source_dir, target_dir, fbx_dir, obj_scale)
