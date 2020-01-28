# -*- coding: utf-8 -*-
import csv
import os, sys, getopt
import tifffile as tiff
import tkinter as tk
from tkinter import filedialog
#remove root windows
root = tk.Tk()
root.withdraw()

print("#########################################################")
print("# Automatically slice TIFF images using a defined grid  #")
print("# in a selected folder.                                 #")
print("#                                                       #")
print("# © 2020 Florian Kleiner, Max Patzelt                   #")
print("#   Bauhaus-Universität Weimar                          #")
print("#   Finger-Institut für Baustoffkunde                   #")
print("#                                                       #")
print("#########################################################")
print()

#### directory definitions
home_dir = os.path.dirname( os.path.realpath(__file__) )

#### global var definitions
col_count = 2
row_count = 2
outputDirName = "cut"
createFolderPerImage = False
showDebuggingOutput = False

#### process given command line arguments
def processArguments():
    global col_count
    global row_count
    global outputDirName
    global showDebuggingOutput
    global createFolderPerImage
    argv = sys.argv[1:]
    usage = sys.argv[0] + " [-h] [-x] [-y] [-d]"
    try:
        opts, args = getopt.getopt(argv,"hcx:y:d",[])
    except getopt.GetoptError:
        print( usage )
    for opt, arg in opts:
        if opt == '-h':
            print( 'usage: ' + usage )
            print( '-h,                  : show this help' )
            print( '-x,                  : amount of slices in x direction [' + str( col_count ) + ']' )
            print( '-y,                  : amount of slices in y direction [' + str( row_count ) + ']' )
            print( '-o,                  : setting output directory name [' + outputDirName + ']' )
            print( '-c                   : creating subfolders for each image [./' + outputDirName + '/FILENAME/]' )
            print( '-d                   : show debug output' )
            print( '' )
            sys.exit()
        elif opt in ("-o"):
            outputDirName = arg
            print( 'changed output directory to ' + outputDirName )
        elif opt in ("-c"):
            createFolderPerImage = True
            print( 'creating subfolders for images' )
        elif opt in ("-x"):
            col_count = int( arg )
            print( 'changed amount of slices in x direction to ' + str( col_count ) )
        elif opt in ("-y"):
            row_count = int( arg )
            print( 'changed amount of slices in y direction to ' + str( row_count ) )
        elif opt in ("-d"):
            print( 'show debugging output' )
            showDebuggingOutput = True
    print( '' )


def sliceImage( workingDirectory, filename ):
    global col_count
    global row_count
    global outputDirName
    global showDebuggingOutput
    global createFolderPerImage
    namePrefix = filename.split( '.' )
    image = tiff.imread( workingDirectory + '/' + filename )
    height, width = image.shape[:2]

    #cropping
    crop_height = int(height/row_count)
    crop_width = int(width/col_count)
    targetDirectory = workingDirectory + '/' + outputDirName + '/'
    for i in range(row_count): # start at i = 0 to row_count-1
        for j in range(col_count): # start at j = 0 to col_count-1
            if ( createFolderPerImage ):
                targetDirectory = workingDirectory + '/' + outputDirName + '/' + namePrefix[0] + '/'
                ## create output directory if it does not exist
                if not os.path.exists( targetDirectory ):
                    os.makedirs( targetDirectory )

            fileij = namePrefix[0] + "_" + str( i ) + "_" + str( j ) + ".tif"
            print( "   - " + fileij + ":" )
            cropped = image[(i*crop_height):((i+1)*crop_height), j*crop_height:((j+1)*crop_width)]
            cropped_filename = targetDirectory + fileij
            tiff.imwrite( cropped_filename, cropped ) #, photometric='rgb'
    image=None
    cropped=None


### actual program start
processArguments()
if ( showDebuggingOutput ) : print( "I am living in '" + home_dir + "'" )
workingDirectory = filedialog.askdirectory(title='Please select the image / working directory')
if ( showDebuggingOutput ) : print( "Selected working directory: " + workingDirectory )

count = 0
position = 0
## count files
if os.path.isdir( workingDirectory ) :
    targetDirectory = workingDirectory + '/' + outputDirName + '/'
    ## create output directory if it does not exist
    if not os.path.exists( targetDirectory ):
        os.makedirs( targetDirectory )

    for file in os.listdir(workingDirectory):
        if ( file.endswith( ".tif" ) or file.endswith( ".TIF" ) ):
            count = count + 1
print( str( count ) + " Tiffs found!" )
## run actual code
if os.path.isdir( workingDirectory ) :
    ## processing files
    for file in os.listdir( workingDirectory ):
        if ( file.endswith( ".tif" ) or file.endswith( ".TIF" ) ):
            filename = os.fsdecode(file)
            position = position + 1
            print( " Analysing " + filename + " (" + str(position) + "/" + str(count) + ") :" )
            sliceImage( workingDirectory, filename )

print( "Script DONE!" )