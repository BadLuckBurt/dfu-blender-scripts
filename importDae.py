import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

dae_in = argv[0]
blend_out = argv[1]

bpy.ops.wm.collada_import(filepath=dae_in)
# bpy.ops.render.render()
bpy.ops.wm.save_mainfile(filepath=blend_out)
