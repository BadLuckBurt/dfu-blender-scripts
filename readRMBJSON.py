import json
import bpy
import os
from pprint import pprint
from math import radians


def import_model(object_record, x_pos, z_pos, y_pos, y_rotation):
    # Prepare append parameters
    model_id = object_record['ModelId']
    blendfile = "D:/scaled/" + model_id + ".dae.blend"
    section = "\\Object\\"
    obj = "model" + model_id + '-node'

    blend_filepath = blendfile + section + obj
    blend_directory = blendfile + section
    blend_filename = obj

    # Load in the model object from the .dae.blend file
    bpy.ops.wm.append(
        filepath=blend_filepath,
        filename=blend_filename,
        directory=blend_directory)

    # Position and rotate the model
    bpy.ops.transform.rotate(value=radians(y_rotation), axis=(0.0, 0.0, 0.0), constraint_axis=(False, False, True),
                             constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                             proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                             snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                             snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, release_confirm=False)
    bpy.ops.transform.translate(value=(x_pos, z_pos, y_pos), constraint_axis=(False, False, False),
                                constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                                proportional_edit_falloff='SMOOTH', proportional_size=1.0, snap=False,
                                snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                remove_on_cancel=False, release_confirm=False)


filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file should be in the same folder as the .blend file you're running this script from
rmbName = str.upper(input("Please enter the name of the RMB block you wish to load\n"))
jsonFilePath = os.path.join(directory, rmbName + ".RMB.json")

with open(
        jsonFilePath) as data_file:
    data = json.load(data_file)

# Max offsets for exterior data, only maxZ is used because layout is bottom to top
maxX = 102.4
maxZ = 102.4

for i, sub_record in enumerate(data['RmbBlock']['SubRecords']):
    XPos = sub_record['XPos']  # X coordinate
    ZPos = sub_record['ZPos']  # Daggerfall ZPos = Y coordinate in Blender
    YRotation = sub_record['YRotation'] / 5.68888888888889  # Dagger YRotation = Z rotation in Blender

    for index, obj_record in enumerate(sub_record['Exterior']['Block3dObjectRecords']):
        x = 0
        z = 0
        y = 0
        if round(YRotation, 0) == 0:
            x = (XPos / 40) + (obj_record['XPos'] / 40)
            z = maxZ - ((ZPos / 40) - (obj_record['ZPos'] / 40))
        elif round(YRotation, 0) == 90:
            x = (XPos / 40) - (obj_record['ZPos'] / 40)
            z = maxZ - ((ZPos / 40) - (obj_record['XPos'] / 40))
        elif round(YRotation, 0) == 180:
            x = (XPos / 40) - (obj_record['XPos'] / 40)
            z = maxZ - ((ZPos / 40) + (obj_record['ZPos'] / 40))
        elif round(YRotation, 0) == 270:
            x = (XPos / 40) + (obj_record['ZPos'] / 40)
            z = maxZ - ((ZPos / 40) + (obj_record['XPos'] / 40))

        import_model(obj_record, x, z, y, YRotation)

for index, obj_rec in enumerate(data['RmbBlock']['Misc3dObjectRecords']):
    pos_x = (obj_rec['XPos'] / 40)  # X coordinate
    pos_y = (obj_rec['YPos'] / 40) * -1  # Y coordinate
    pos_z = maxZ - ((obj_rec['ZPos'] / 40) * -1)  # Daggerfall ZPos = Y coordinate in Blender
    rot_y = obj_rec['YRotation'] / 5.68888888888889  # Dagger YRotation = Z rotation in Blender
    import_model(obj_rec, pos_x, pos_z, pos_y, rot_y)
