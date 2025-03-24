# Umodel-Addon

Blender Addon for Integrating UModel ```.pskx``` and ```.png``` Exports.

## Description

This is a Blender addon that allows you to easily integrate ```.pskx``` models and ```.png``` textures exported from UModel (UE Viewer).

## How to Use

* Import your ```.pskx``` model into Blender
* Press the ```N key``` to open the UI panel
* Select your unpacked root directory
* Select the models you want to process (multi-selection is supported)
* Click ```Apply Materials``` to automatically apply textures to the models

### Supported Blender Version

* Tested and developed for Blender ```2.83.6```

### Notes

* This addon relies on the ```.props.txt``` file.
* Ambient Occlusion is only supported in Blender ```4.2``` and above.
    * Currently, the import of RMH (Roughness, Metallic, Ambient Occlusion) materials is disabled in this version of the addon.
If you want to enable it, simply edit the addon script and uncomment the related lines.

## Version History

* ```1.0```
    * Initial Release
