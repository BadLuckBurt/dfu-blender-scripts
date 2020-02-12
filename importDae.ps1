$files = @(Get-ChildItem d:\*.dae)
foreach ($file in $files) {

    $CMD = "Z:\blender-2.79b-windows64\blender-2.79b-windows64\blender.exe"
    $arg1 = "' --background'"
    $arg2 = "' --python D:\python\importDae.py'"
    $arg3 = "' -- " + $file.FullName + " " + $file.FullName + ".blend'"

    $CMD + $arg1 + $arg2 + $arg3
}