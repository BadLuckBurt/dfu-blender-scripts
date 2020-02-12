import bpy
import sys
import os
import re
import glob

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

folder_in = argv[0]
print(folder_in)
tmp = re.findall(r"(TEXTURE\.\d{3}).*", argv[0])
print(folder_in)
if len(tmp) > 0:
    tmp2 = re.findall(r"(\d+)", tmp[0])
    folder_in = folder_in.replace("\\.", "")
    fileSelector = folder_in + "\\"

    listing = glob.glob(fileSelector + "*.png")
    # print(listing)

    fileList = []
    for filename in listing:
        # name = filename.replace(fileSelector, "")
        fileList.append({'name': filename})

    # print(fileList)
    # print(fileSelector)
    blend_out = "D:\\flats\\" + tmp[0] + ".blend"

    bpy.ops.import_image.to_plane(shader='SHADELESS', files=fileList, texture_set=tmp2[0], offset=False)
    bpy.ops.wm.save_mainfile(filepath=blend_out)

# files = os.listdir(fileSelector)
# dir_root = bpy.path.abspath("//")
