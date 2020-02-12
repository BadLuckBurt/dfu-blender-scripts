FOR /R "D:\PNG\" %%G in (.) DO (
 Z:\blender-2.79b-windows64\blender-2.79b-windows64\blender.exe --background --python d:\scripts\importFlats.py -- "%%G"
)