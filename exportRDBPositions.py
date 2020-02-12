# import the necessary modules we need
# in our case, blender's python API and python's os module
import collections
import json

import bpy
import math
import os
import re

# get the current selection
# selection = bpy.context.selected_objects

structure = [ob for ob in bpy.context.scene.objects if ob.layers[0]]
decoration = [ob for ob in bpy.context.scene.objects if ob.layers[1]]
flats = [ob for ob in bpy.context.scene.objects if ob.layers[2]]
lights = [ob for ob in bpy.context.scene.objects if ob.layers[3]]

layers = [structure, decoration, flats, lights]

# initialize a blank result variable
result = ""

rdbBlock = collections.OrderedDict()
modelReferenceList = []
objectRootList = []

index = 0

lightArchives = [101, 200, 210, 253]
lightIndexes = [
    [0, 2, 3, 5, 6, 7, 8, 9, 11, 12],
    [7, 8, 9, 10],
    [0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    [10, 17, 18, 19, 22, 49, 50, 51, 52, 75, 77]
]

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

        name = sel.name
        modelMatch = re.findall(r"model(\d+)\-.*", name)
        flatMatch = re.findall(r"(\d{3})-(\d+)-*", name)

        if len(flatMatch) == 0 and len(modelMatch) == 0:
            continue

        if len(flatMatch) > 0 or len(modelMatch) > 0:
            index += 1
            position = 10000 + positionCounter
            positionCounter += 1
            rdbObject = collections.OrderedDict()

            xPos = int(round(pos.x * 40))
            yPos = int(round(pos.z * -40))
            zPos = int(round(pos.y * 40))

            rdbObject["Position"] = position
            rdbObject["Index"] = index
            rdbObject["XPos"] = xPos
            rdbObject["YPos"] = yPos
            rdbObject["ZPos"] = zPos

            resources = collections.OrderedDict()

            if len(flatMatch) > 0:
                textureArchiveId = int(flatMatch[0][0])
                flatId = int(flatMatch[0][1])
                if textureArchiveId in lightArchives:
                    if flatId in lightIndexes[lightArchives.index(textureArchiveId)]:
                        light = collections.OrderedDict()
                        light["Index"] = index
                        light["XPos"] = xPos
                        light["YPos"] = yPos
                        light["ZPos"] = zPos
                        light["Type"] = "Light"
                        lightResources = collections.OrderedDict()
                        lightResource = collections.OrderedDict()
                        lightResource["Unknown1"] = 32
                        lightResource["Unknown2"] = 0
                        lightResource["Radius"] = 100
                        lightResources["LightResource"] = lightResource
                        light["Resources"] = lightResources

                        index += 1
                        rdbObject["Index"] = index
                        rdbObjects.append(light)

                rdbObject["Type"] = "Flat"

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

            elif len(modelMatch) > 0:
                modelId = modelMatch[0]
                if modelIndexes.count(modelId) < 1:
                    modelIndexes.append(modelId)
                    modelReferenceRecord = collections.OrderedDict()
                    modelReferenceRecord["ModelId"] = str(modelId)
                    modelReferenceRecord["ModelIdNum"] = int(modelId)
                    modelReferenceRecord["Description"] = "XXX"
                    modelReferenceList.append(modelReferenceRecord)

                rdbObject["Type"] = "Model"

                modelResource = collections.OrderedDict()

                modelResource["XRotation"] = 0
                modelResource["YRotation"] = int(yRotation)
                modelResource["ZRotation"] = 0
                modelResource["ModelIndex"] = modelIndexes.index(modelId)
                modelResource["SoundIndex"] = 0

                actionResource = collections.OrderedDict()
                actionResource["Position"] = int(position)
                actionResource["Axis"] = 0
                actionResource["Duration"] = 0
                actionResource["Magnitude"] = 0
                actionResource["NextObjectIndex"] = -1
                actionResource["Flags"] = 0

                modelResource["ActionResource"] = actionResource

                resources["ModelResource"] = modelResource

            rdbObject["Resources"] = resources
            rdbObjects.append(rdbObject)

    rdbObjectHolder["RdbObjects"] = rdbObjects
    objectRootList.append(rdbObjectHolder)
rdbBlock["ModelReferenceList"] = modelReferenceList
rdbBlock["ObjectRootList"] = objectRootList

jsonText = json.dumps(rdbBlock, indent=4)

filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file should be in the same folder as the .blend file you're running this script from
jsonFilePath = os.path.join(directory, "objectRDBPositions.json")
# open a file to write to
file = open(jsonFilePath, "w+")
# write the data to file
file.write(jsonText)
# close the file
file.close()
