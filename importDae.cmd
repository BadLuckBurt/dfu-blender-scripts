for %%f in (d:\*.dae) do (
	Z:\blender-2.79b-windows64\blender-2.79b-windows64\blender.exe --background --python d:\python\importDae.py -- %%f %%f.blend
)
pause