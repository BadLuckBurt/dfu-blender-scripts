# import the necessary modules we need
# in our case, blender's python API and python's os module
import bpy, os, re, math
import json, collections
# get the current selection
# selection = bpy.context.selected_objects

structure = [ob for ob in bpy.context.scene.objects if ob.layers[0]]
decoration = [ob for ob in bpy.context.scene.objects if ob.layers[1]]
flats = [ob for ob in bpy.context.scene.objects if ob.layers[2]]

layers = [structure, decoration, flats]

# initialize a blank result variable
result = ""

Interior = collections.OrderedDict()
Header = collections.OrderedDict()

Header["Num3dObjectRecords"] = 0
Header["NumFlatObjectRecords"] = 0
Header["NumSection3Records"] = 0
Header["NumPeopleRecords"] = 0
Header["NumDoorRecords"] = 0

Block3dObjectRecords = []
BlockFlatObjectRecords = []
BlockSection3Records = []
BlockPeopleRecords = []
BlockDoorRecords = []

modelReferenceList = []
objectRootList = []

index = 0

positionCounter = 0
layerIndex = 0
# iterate through the selected objects
for layer in layers:
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

            # rmbObject["Position"] = position
            # rmbObject["Index"] = index
            xPos = int(round(pos.x * 40))
            yPos = int(round(pos.z * -40))
            zPos = int(round(pos.y * 40))

            if len(flatMatch) > 0:
                textureSetId = int(flatMatch[0][0])
                flatId = int(flatMatch[0][1])

                flat = collections.OrderedDict()

                flat["Position"] = position
                flat["XPos"] = xPos
                flat["YPos"] = yPos
                flat["ZPos"] = zPos
                flat["TextureArchive"] = textureSetId
                flat["TextureRecord"] = flatId
                flat["FactionID"] = 0
                flat["Flags"] = 0

                if layerIndex == 1:  # regular flats
                    BlockFlatObjectRecords.append(flat)
                    Header["NumFlatObjectRecords"] += 1
                elif layerIndex == 3:  # people flats
                    # TODO: Add extra logic for factions etc
                    BlockPeopleRecords.append(flat)
                    Header["NumPeopleRecords"] += 1
            elif len(modelMatch) > 0:
                modelId = modelMatch[0]
                model = collections.OrderedDict()
                model["ModelId"] = str(modelId)
                model["ModelIdNum"] = int(modelId)
                if layerIndex == 0:
                    model["ObjectType"] = 13    # structure
                elif layerIndex == 1:
                    model["ObjectType"] = 3     # decoration / furniture / clutter

                model["XPos"] = xPos
                model["YPos"] = yPos
                model["ZPos"] = zPos

                model["XRotation"] = 0
                model["YRotation"] = int(yRotation)
                model["ZRotation"] = 0

                if layerIndex == 0 or layerIndex == 1:  # structure / furniture / clutter models
                    Block3dObjectRecords.append(model)
                    Header["Num3dObjectRecords"] += 1
                elif layerIndex == 4: # door models
                    BlockDoorRecords.append(model)
                    Header["NumDoorRecords"] += 1

Interior["Header"] = Header
Interior["Block3dObjectRecords"] = Block3dObjectRecords
Interior["BlockFlatObjectRecords"] = BlockFlatObjectRecords
Interior["BlockSection3Records"] = BlockSection3Records
Interior["BlockPeopleRecords"] = BlockPeopleRecords
Interior["BlockDoorRecords"] = BlockDoorRecords

jsonText = json.dumps(Interior, indent=4)

filepath = bpy.data.filepath
directory = os.path.dirname(filepath)

# JSON file should be in the same folder as the .blend file you're running this script from
jsonFilePath = os.path.join(directory, "objectRMBInteriorPositions.json")
# open a file to write to
file = open(jsonFilePath, "w+")
# write the data to file
file.write(jsonText)
# close the file
file.close()
