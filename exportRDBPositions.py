# import the necessary modules we need
# in our case, blender's python API and python's os module
import collections
import json
import bpy
import bmesh
import math
import os
import re


def coords(objname, space='GLOBAL'):
    # Store reference to the bpy.data.objects datablock
    obj = bpy.data.objects[objname]

    # Store reference to bpy.data.objects[].meshes datablock
    if obj.mode == 'EDIT':
        v = bmesh.from_edit_mesh(obj.data).verts
    elif obj.mode == 'OBJECT':
        v = obj.data.vertices

    if space == 'GLOBAL':
        # Return T * L as list of tuples
        return [(obj.matrix_world * v.co).to_tuple() for v in v]
    elif space == 'LOCAL':
        # Return L as list of tuples
        return [v.co.to_tuple() for v in v]


def scene_bounding_box():

    # Get names of all meshes
    mesh_names = [v.name for v in bpy.context.scene.objects if v.type == 'MESH']

    # Save an initial value
    # Save as list for single-entry modification
    co = coords(mesh_names[0])[0]
    bb_max = [co[0], co[1], co[2]]
    bb_min = [co[0], co[1], co[2]]

    # Test and store maxima and mimima
    for i in range(0, len(mesh_names)):
        co = coords(mesh_names[i])
        for j in range(0, len(co)):
            for k in range(0, 3):
                if co[j][k] > bb_max[k]:
                    bb_max[k] = co[j][k]
                if co[j][k] < bb_min[k]:
                    bb_min[k] = co[j][k]

    # Convert to tuples
    bb_max = (bb_max[0], bb_max[1], bb_max[2])
    bb_min = (bb_min[0], bb_min[1], bb_min[2])

    return [bb_min, bb_max]


# get the current selection
# selection = bpy.context.selected_objects

# build a list for all models, flats and lights (separated by layer)
structure = [ob for ob in bpy.context.scene.objects if ob.layers[0]]
decoration = [ob for ob in bpy.context.scene.objects if ob.layers[1]]
flats = [ob for ob in bpy.context.scene.objects if ob.layers[2]]
lights = [ob for ob in bpy.context.scene.objects if ob.layers[3]]

# merge the lists into one list of layers
layers = [structure, decoration, flats, lights]

# initialize a blank result variable, a dictionary and lists to hold the result data
result = ""
rdbBlock = collections.OrderedDict()
modelReferenceList = []
objectRootList = []

index = 0

# These archives and indexes are used to identify light flats and place Unity light objects next to them
lightArchives = [101, 200, 210, 253]
lightIndexes = [
    [0, 2, 3, 5, 6, 7, 8, 9, 11, 12],
    [7, 8, 9, 10],
    [0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    [10, 17, 18, 19, 22, 49, 50, 51, 52, 75, 77]
]

sceneBoundingBox = scene_bounding_box()

# List to keep track of model indexes to be
modelIndexes = []
positionCounter = 0
# iterate through the selected objects
for layer in layers:
    rdbObjectHolder = collections.OrderedDict()
    rdbObjects = []
    for sel in layer:
        # for sel in itertools.chain(structure, decoration):
        # get the current object's dimensions
        pos = sel.location
        rot = sel.rotation_euler

        yRotation = round(math.degrees(rot[2]))
        if yRotation > 360:
            yRotation -= 360

        if yRotation == 360:
            yRotation = 0

        yRotation = round(yRotation * 5.68888888888889)

        # match current object name to identify model / flat
        name = sel.name
        modelMatch = re.findall(r"model(\d+)\-.*", name)
        flatMatch = re.findall(r"(\d{3})-(\d+)-*", name)

        # ignore anything that isn't a model or a flat
        if len(flatMatch) == 0 and len(modelMatch) == 0:
            continue

        # process model / flat
        if len(flatMatch) > 0 or len(modelMatch) > 0:
            position = 10000 + positionCounter
            positionCounter += 1

            # create a new rdbObject dictionary
            rdbObject = collections.OrderedDict()

            # convert blender coordinates to DFU coordinates - swap Z & Y coordinates and make the Y and Z negative
            xPos = int(round(pos.x * 40))
            yPos = int(round(pos.z * -40))
            zPos = int(round((pos.y - sceneBoundingBox[1][1]) * 40))

            # set object position
            rdbObject["Position"] = position
            rdbObject["Index"] = index
            index += 1
            rdbObject["XPos"] = xPos
            rdbObject["YPos"] = yPos
            rdbObject["ZPos"] = zPos

            # resources for the current object
            resources = collections.OrderedDict()

            # process flat
            if len(flatMatch) > 0:
                # check if flat belongs to light texture flats
                textureArchiveId = int(flatMatch[0][0])
                flatId = int(flatMatch[0][1])
                if textureArchiveId in lightArchives:
                    if flatId in lightIndexes[lightArchives.index(textureArchiveId)]:
                        # create Unity light object
                        light = collections.OrderedDict()
                        light["Index"] = index
                        light["XPos"] = xPos
                        light["YPos"] = yPos
                        light["ZPos"] = zPos
                        light["Type"] = "Light"

                        # set and store light properties as resource
                        lightResources = collections.OrderedDict()
                        lightResource = collections.OrderedDict()
                        lightResource["Unknown1"] = 32  # sel.get("unknown1", 32)
                        lightResource["Unknown2"] = 0  # sel.get("unknown2", 0)
                        lightResource["Radius"] = sel["radius"]
                        lightResources["LightResource"] = lightResource
                        light["Resources"] = lightResources

                        # set light's object index and store in rdbObjects list
                        index += 1
                        rdbObject["Index"] = index
                        rdbObjects.append(light)

                # set object type
                rdbObject["Type"] = "Flat"

                # set flat object properties
                flatResource = collections.OrderedDict()
                flatResource["Position"] = int(position)
                flatResource["TextureArchive"] = int(textureArchiveId)
                flatResource["TextureRecord"] = int(flatId)
                flatResource["Flags"] = 0
                flatResource["Magnitude"] = 0
                flatResource["SoundIndex"] = 0
                flatResource["FactionOrMobileId"] = 0
                flatResource["NextObjectOffset"] = 0
                flatResource["Action"] = 0

                resources["FlatResource"] = flatResource

            # process model
            elif len(modelMatch) > 0:

                # get the matched model id
                modelId = modelMatch[0]

                # check if model id already exists in modelIndexes
                if modelIndexes.count(modelId) < 1:

                    # add model id to modelIndexes and modelReferenceList if not found
                    modelIndexes.append(modelId)
                    modelReferenceRecord = collections.OrderedDict()
                    modelReferenceRecord["ModelId"] = str(modelId)
                    modelReferenceRecord["ModelIdNum"] = int(modelId)
                    modelReferenceRecord["Description"] = "XXX"
                    modelReferenceList.append(modelReferenceRecord)

                # set object type
                rdbObject["Type"] = "Model"

                # set model object properties
                modelResource = collections.OrderedDict()

                modelResource["XRotation"] = 0
                modelResource["YRotation"] = int(yRotation)
                modelResource["ZRotation"] = 0
                modelResource["ModelIndex"] = modelIndexes.index(modelId)
                modelResource["SoundIndex"] = 0

                if "soundindex" in sel:
                    modelResource["SoundIndex"] = sel["soundindex"]

                actionResource = collections.OrderedDict()
                actionResource["Position"] = int(position)
                actionResource["Axis"] = 0
                actionResource["Duration"] = 0
                actionResource["Magnitude"] = 0
                actionResource["NextObjectIndex"] = -1
                actionResource["Flags"] = 0
                if "action" in sel:
                    actionResource["Flags"] = sel["action"]

                modelResource["ActionResource"] = actionResource

                resources["ModelResource"] = modelResource

            # store data as rdbObject and append to the rdbObjects list
            rdbObject["Resources"] = resources
            rdbObjects.append(rdbObject)

    # append rdbObjects to the holder and append holder to objectRootList (to create the proper DFU data structure)
    rdbObjectHolder["RdbObjects"] = rdbObjects
    objectRootList.append(rdbObjectHolder)

# store the modelReferenceList and objectRootList
rdbBlock["ModelReferenceList"] = modelReferenceList
rdbBlock["ObjectRootList"] = objectRootList

# dump the resulting data set as a JSON text string
jsonText = json.dumps(rdbBlock, indent=4)

# get the path to the current .blend file
filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file will be created in the same folder as the .blend file you're running this script from
jsonFilePath = os.path.join(directory, "objectRDBPositions.json")
# open a file to write to
file = open(jsonFilePath, "w+")
# write the data to file
file.write(jsonText)
# close the file
file.close()
