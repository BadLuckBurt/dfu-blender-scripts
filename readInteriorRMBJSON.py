import json
import bpy
import os
from pprint import pprint
from math import radians

filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file should be in the same folder as the .blend file you're running this script from
rmbName = str.upper(input("Please enter the name of the RMB block you wish to load\n"))
jsonFilePath = os.path.join(directory, rmbName + ".RMB.json")

with open(jsonFilePath) as data_file:
    data = json.load(data_file)

# Uncomment the for loop and indent the lines below it to loop through all the interiors
# Maybe models could be loaded to separate layers?
# for i, subrecord in enumerate(data['RmbBlock']['SubRecords']):

# just picking a single subrecord for the moment
subrecord = data['RmbBlock']['SubRecords'][1]

# Load in, position and rotate all the interior models
for index, objectRecord in enumerate(subrecord['Interior']['Block3dObjectRecords']):
    XPos = (objectRecord['XPos'] / 40)  # X coordinate
    # YPos is inverted (* -1) because Daggerfall uses reversed coordinates for height position
    YPos = (objectRecord['YPos'] / 40) * -1  # YPos = Z coordinate in Blender
    ZPos = (objectRecord['ZPos'] / 40)  # ZPos = Y coordinate in Blender
    YRotation = objectRecord['YRotation'] / 5.68888888888889  # YRotation = Z rotation in Blender

    # Prepare append parameters
    modelId = objectRecord['ModelId']
    blendfile = "D:/scaled/" + modelId + ".dae.blend"
    section = "\\Object\\"
    object = "model" + modelId + '-node'

    filepath = blendfile + section + object
    directory = blendfile + section
    filename = object

    # Load in the model object from the .dae.blend file
    bpy.ops.wm.append(
        filepath=filepath,
        filename=filename,
        directory=directory)

    # Furniture and decoration needs to be offset by half their height or they won't be in the proper position
    if objectRecord['ObjectType'] == 3:
        obj = bpy.context.scene.objects[object]
        YPos = YPos + (obj.dimensions[1] / 2)

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
