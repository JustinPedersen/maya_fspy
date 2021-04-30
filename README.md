
# maya_fspy
Simple UI to import fSpy files into Autodesk Maya

# What is this?
This is the non-official importer for fspy json data into Autodesk Maya. [fSpy](https://github.com/stuffmatic/fSpy) is an open source, cross platform app for still image camera matching.  See [fspy.io](https://fspy.io/) for more info. If you have found this tool helpful in anyway please consider donating to the origional creators on the fspy.io website.

This is by no means a perfect import and some tweaks might be required but its sure as hell better than placing an image plane and camera by hand.

The below images show fSpy project (top) and a matching Maya camera created by the importer (bottom).
![Image of fspy](https://github.com/JustinPedersen/maya_fspy/blob/master/images/fspy.png)
![Image of maya](https://github.com/JustinPedersen/maya_fspy/blob/master/images/maya_01.png)
![Image of maya](https://github.com/JustinPedersen/maya_fspy/blob/master/images/maya_02.png)

# Installing and running
1. Download the zip file: [maya_fspy_v1.2.0.zip](https://github.com/JustinPedersen/maya_fspy/releases/download/v1.2.0/maya_fspy.zip)
2. Unzip it into your Maya scripts folder: `..\Documents\maya\<version>\scripts\maya_fspy`
3. Paste the following code into the Maya script editor in a Python tab and run, or create a button for easier use: 
```python
import maya_fspy.ui as mfspy_ui
mfspy_ui.maya_fspy_ui()
```

# Use
 ### FSPY Application
 1. You can find many tutorials online about how to use FSPY, just place the image and configure the perspective lines to your liking. 
 Make sure to configure the settings correctly. (More on this below)
 2. Export Camera settings as json from FSPY, making sure that the file you exported has the `.json` extension. The Maya importer does not accept `.fspy` files like the Blender plugin, it will only accept a `.json` file. 
 (File/Export/Camera parameters as JSON)
 
 ### Maya
 ![ui](https://github.com/JustinPedersen/maya_fspy/blob/master/images/ui.png)
 1. Click the json button and navigate to the json file exported from the fspy standalone application.
 2. Click the image button and navigate to the same image used within the fspy application. This image will be used in the image plane.
 3. Hit Import!
 4. A group with a new camera and image plane will be created. Note that you may need to reposition/scale this group depending on your needs. The camera's transforms are locked by default to prevent any accidental bumps but they can be safely unlocked and tweaked if needed.

## ⚠️IMPORTANT ⚠️:
Note that you will need to configure some settings within the fspy application so that the settings carry over into Maya correctly.
Vanishing points axes:  ***-Z , -X***
Reference distance: ***Along the y axis***

*See above screenshot of the standalone application if you are not sure.*

## Tested on Maya 2018 + 2019
If you are able to test on any other maya versions please let me know so I can update it here.

## Finally
Huge thanks to the peeps over at https://github.com/stuffmatic/fSpy for this kickass application! 
Also big thanks to Jascha Wohlkinger for helping me out with some of the matrix stuff on the Maya side!
