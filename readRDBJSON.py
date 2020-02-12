import json
import bpy
import os
from pprint import pprint
from math import radians

filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file should be in the same folder as the .blend file you're running this script from
rmbName = str.upper(input("Please enter the name of the RDB block you wish to load\n"))
jsonFilePath = os.path.join(directory, rmbName + ".RMB.json")

with open(
        jsonFilePath) as data_file:
    data = json.load(data_file)

# Max offsets for dungeon block data, only maxZ is used because layout is bottom to top
maxX = 51.2
maxZ = 51.2


modelReference = data['RdbBlock']['ModelReferenceList']
for h, obj_list in enumerate(data['RdbBlock']['ObjectRootList']):
    objects = obj_list['RdbObjects']
    if objects is None:
        continue
    # Only load in 3D models, not the flats etc.
    for i, model in enumerate(objects):

        if 'ModelResource' in model['Resources']:
            index = model['Resources']['ModelResource']['ModelIndex']
            modelId = str(modelReference[index]['ModelIdNum'])

            XPos = (model['XPos'] / 40)  # X coordinate
            YPos = (model['YPos'] / 40) * -1  # Daggerfall YPos = Z coordinate in Blender
            ZPos = (model['ZPos'] / 40)  # Daggerfall ZPos = Y coordinate in Blender
            YRotation = model['Resources']['ModelResource'][
                            'YRotation'] / 5.68888888888889  # Dagger YRotation = Z rotation in Blender

            blendfile = "D:/scaled/" + modelId + ".dae.blend"
            section = "\\Object\\"
            obj = "model" + modelId + '-node'

            filepath = blendfile + section + obj
            directory = blendfile + section
            filename = obj
        elif 'FlatResource' in model['Resources']:
            index = model['Index']

            textureArchive = model['Resources']['FlatResource']['TextureArchive']
            textureArchive = str(textureArchive).zfill(3)
            textureRecord = model['Resources']['FlatResource']['TextureRecord']

            XPos = (model['XPos'] / 40)  # X coordinate
            YPos = (model['YPos'] / 40) * -1  # Daggerfall YPos = Z coordinate in Blender
            ZPos = (model['ZPos'] / 40)  # Daggerfall ZPos = Y coordinate in Blender
            YRotation = 0

            blendfile = "D:/flats/TEXTURE." + textureArchive + ".blend"
            section = "\\Object\\"
            obj = textureArchive + "-" + str(textureRecord) + "-0"

            filepath = blendfile + section + obj
            directory = blendfile + section
            filename = obj
        else:
            continue

        # Load in the model object from the .dae.blend file
        bpy.ops.wm.append(
            filepath=filepath,
            filename=filename,
            directory=directory)

        # Position and rotate the model
        bpy.ops.transform.translate(value=(XPos, ZPos, YPos), constraint_axis=(False, False, False),
                                    constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                    proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                                    snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                    snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                    remove_on_cancel=False, release_confirm=False)
        bpy.ops.transform.rotate(value=radians(YRotation), axis=(0.0, 0.0, 1.0), constraint_axis=(False, False, True),
                                 constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                 proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                                 snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                 snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, release_confirm=False)
