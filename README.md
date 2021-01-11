# image_slicer

Simple script to split tiff images in a selected folder into multiple smaller tiles 
written for Python 3.x
Auto detects scaling of an image and removes scale bar if it exists

## required packages

### third party

- tkinter
- PIL
- tifffile

### own packages

- https://github.com/kleinerELM/tiff_scaling
- https://github.com/kleinerELM/remove_scalebar
These packages have to exist in the parent folder of the image_slicer script-folder!

## Standard automatic processing

run 
```bash
python .\image_slicer.py -x 3 -y 3
```
to split the image to 3 x 3 = 9 sub tiles

Help output of the python script:

```
#########################################################
# Automatically slice TIFF images using a defined grid  #
# in a selected folder.                                 #
#                                                       #
# © 2021 Florian Kleiner, Max Patzelt                   #
#   Bauhaus-Universität Weimar                          #
#   Finger-Institut für Baustoffkunde                   #
#                                                       #
#########################################################

usage: D:\Nextcloud\Uni\WdB\REM\Fiji Plugins & Macros\Selbstgeschrieben\image_slicer\image_slicer.py [-h] [-x] [-y] [-d]
-h,                  : show this help
-x,                  : amount of slices in x direction [2]
-y,                  : amount of slices in y direction [2]
-o,                  : setting output directory name [cut]
-c                   : creating subfolders for each image [./cut/FILENAME/]
-d                   : show debug output
```

## output

The output files can be found in the subfolder `cut`. They will be named in the following way, if the input file was named example.tif:

```
example_[x]_[y].tif
```