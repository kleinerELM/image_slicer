# -*- coding: utf-8 -*-
import csv
import os, sys, getopt
import tifffile as tiff
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000 # prevent decompressionbomb warning for typical images
import tkinter as tk
from tkinter import filedialog

def programInfo():
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

def getBaseSettings():
    settings = {
        "showDebuggingOutput" : False,
        "home_dir"            : os.path.dirname(os.path.realpath(__file__)),
        "workingDirectory"    : "",
        "outputDirectory"     : "cut",
        "createFolderPerImage": False,
        "col_count"           : 2,
        "row_count"           : 2
    }
    return settings

#### process given command line arguments
def processArguments():    
    settings = getBaseSettings()
    col_changed = False
    row_changed = False
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
            print( '-x,                  : amount of slices in x direction [{}]'.format(settings["col_count"]) )
            print( '-y,                  : amount of slices in y direction [{}]'.format(settings["row_count"]) )
            print( '-o,                  : setting output directory name [{}]'.format(settings["outputDirectory"]) )
            print( '-c                   : creating subfolders for each image [./' + settings["outputDirectory"] + '/FILENAME/]'.format(settings["outputDirectory"]) )
            print( '-d                   : show debug output' )
            print( '' )
            sys.exit()
        elif opt in ("-o"):
            settings["outputDirectory"] = arg
            print( 'changed output directory to ' + settings["outputDirectory"] )
        elif opt in ("-c"):
            settings["createFolderPerImage"] = True
            print( 'creating subfolders for images' )
        elif opt in ("-x"):
            settings["col_count"] = int( arg )
            col_changed = True
            print( 'changed amount of slices in x direction to {}'.format(settings["col_count"]) )
        elif opt in ("-y"):
            settings["row_count"] = int( arg )
            row_changed = True
            print( 'changed amount of slices in y direction to {}'.format(settings["row_count"]) )
        elif opt in ("-d"):
            print( 'show debugging output' )
            settings["showDebuggingOutput"] = True
    # alway expecting the same values for row/col if not defined explicitly        
    if col_changed and not row_changed:
        settings["row_count"] = settings["col_count"]
        print( 'changed amount of slices in y direction also to ' + str( settings["row_count"] ) )
    elif row_changed and not col_changed:
        settings["col_count"] = settings["row_count"]
        print( 'changed amount of slices in x direction also to ' + str( settings["col_count"] ) )
    print( '' )
    return settings

def sliceImage( settings, file_name, file_extension ):
    src_file = settings["workingDirectory"] + os.sep + file_name + file_extension
    if ( file_extension.lower() == '.tif'):
        img = tiff.imread( src_file )
        height, width = img.shape[:2]
    if ( file_extension.lower() == '.png'):
        img = Image.open( src_file )
        width, height = img.size

    #cropping
    crop_height = int(height/settings["row_count"])
    crop_width = int(width/settings["col_count"])
    targetDirectory = settings["workingDirectory"] + os.sep + settings["outputDirectory"] + os.sep
    for i in range(settings["row_count"]): # start at i = 0 to row_count-1
        for j in range(settings["col_count"]): # start at j = 0 to col_count-1
            if ( settings["createFolderPerImage"] ):
                targetDirectory = settings["workingDirectory"] + os.sep + settings["outputDirectory"] + os.sep + file_name + os.sep
                ## create output directory if it does not exist
                if not os.path.exists( targetDirectory ):
                    os.makedirs( targetDirectory )

            fileij = file_name + "_" + str( i ) + "_" + str( j ) + file_extension
            print( "   - " + fileij + ":" )
            cropped_filename = targetDirectory + fileij
            if ( file_extension.lower() == '.tif'):
                cropped = img[(i*crop_height):((i+1)*crop_height), j*crop_width:((j+1)*crop_width)]
                tiff.imwrite( cropped_filename, cropped ) #, photometric='rgb'
            if ( file_extension.lower() == '.png'):
                img.crop( ((j*crop_width), (i*crop_height), ((j+1)*crop_width), ((i+1)*crop_height)) ).save( cropped_filename )
            
    img=None
    cropped=None


### actual program start
if __name__ == '__main__':
    #remove root windows
    root = tk.Tk()
    root.withdraw()

    settings = processArguments()
    if ( settings["showDebuggingOutput"] ) : print( "I am living in '{}'".format(settings["home_dir"] ) ) 
    settings["workingDirectory"] = filedialog.askdirectory(title='Please select the working directory')
    if ( settings["showDebuggingOutput"] ) : print( "Selected working directory: " + settings["workingDirectory"] )

    allowed_file_extensions = [ '.tif', '.png' ]

    count = 0
    position = 0
    ## count files
    if os.path.isdir( settings["workingDirectory"] ) :
        targetDirectory = settings["workingDirectory"] + os.sep + settings["outputDirectory"] + os.sep
        ## create output directory if it does not exist
        if not os.path.exists( targetDirectory ):
            os.makedirs( targetDirectory )

        for file in os.listdir(settings["workingDirectory"]):
            file_name, file_extension = os.path.splitext( file )
            if ( file_extension.lower() in allowed_file_extensions ):
                count = count + 1
        print( str( count ) + " images found!" )
        ## processing files
        for file in os.listdir( settings["workingDirectory"] ):
            file_name, file_extension = os.path.splitext( file )
            if ( file_extension.lower() in allowed_file_extensions ):
                # filename = os.fsdecode(file)
                position = position + 1
                print( " Analysing {} ({}/{}) :".format(file_name + file_extension, position, count) )
                sliceImage( settings, file_name, file_extension )

    print( "Script DONE!" )