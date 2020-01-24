# remove_SEM_scalebar
simple script to split tiff images in multiple smaller tiles

## standard automatical processing

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
# © 2020 Florian Kleiner, Max Patzelt                   #
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
