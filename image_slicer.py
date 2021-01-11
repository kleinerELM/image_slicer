# -*- coding: utf-8 -*-
import csv
import os, sys, getopt
import tifffile as tiff
from PIL import Image
Image.MAX_IMAGE_PIXELS = 10000000000 # prevent decompressionbomb warning for typical images
import tkinter as tk
from tkinter import filedialog

def programInfo():
    print("#########################################################")
    print("# Automatically slice TIFF images using a defined grid  #")
    print("# in a selected folder.                                 #")
    print("#                                                       #")
    print("# © 2021 Florian Kleiner, Max Patzelt                   #")
    print("#   Bauhaus-Universität Weimar                          #")
    print("#   Finger-Institut für Baustoffkunde                   #")
    print("#                                                       #")
    print("#########################################################")
    print()

# import other libaries by kleinerELM
home_dir = os.path.dirname(os.path.realpath(__file__))

ts_path = os.path.dirname( home_dir ) + os.sep + 'tiff_scaling' + os.sep
ts_file = 'set_tiff_scaling'
if ( os.path.isdir( ts_path ) and os.path.isfile( ts_path + ts_file + '.py' ) or os.path.isfile( home_dir + ts_file + '.py' ) ):
    if ( os.path.isdir( ts_path ) ): sys.path.insert( 1, ts_path )
    import set_tiff_scaling as ts
    import extract_tiff_scaling as es
else:
    programInfo()
    print( 'missing ' + ts_path + ts_file + '.py!' )
    print( 'download from https://github.com/kleinerELM/tiff_scaling' )
    sys.exit()

rsb_file = 'remove_SEM_scalebar'
rsb_path = os.path.dirname( home_dir ) + os.sep + 'remove_SEM_scalebar' + os.sep
if ( os.path.isdir( rsb_path ) and os.path.isfile( rsb_path +rsb_file + '.py' ) or os.path.isfile( home_dir + rsb_file + '.py' ) ):
    if ( os.path.isdir( rsb_path ) ): sys.path.insert( 1, rsb_path )
    import remove_SEM_scalebar as rsb
else:
    programInfo()
    print( 'missing ' + rsb_path + rsb_file + '.py!' )
    print( 'download from https://github.com/kleinerELM/remove_SEM_scalebar' )
    sys.exit()

# Initial function to load the settings
def getBaseSettings():
    settings = {
        "showDebuggingOutput" : False,
        "home_dir"            : os.path.dirname(os.path.realpath(__file__)),
        "workingDirectory"    : "",
        "outputDirectory"     : "cut",
        "createFolderPerImage": False,
        "col_count"           : 2,
        "row_count"           : 2,
        "overwrite_existing"  : False
    }
    return settings

#### process given command line arguments
def processArguments():
    settings = getBaseSettings()
    col_changed = False
    row_changed = False
    argv = sys.argv[1:]
    usage = sys.argv[0] + " [-h] [-x] [-y] [-r][-o] [-c] [-d]"
    try:
        opts, args = getopt.getopt(argv,"hcx:y:od",[])
    except getopt.GetoptError:
        print( usage )
    for opt, arg in opts:
        if opt == '-h':
            print( 'usage: ' + usage )
            print( '-h,                  : show this help' )
            print( '-x,                  : amount of slices in x direction [{}]'.format(settings["col_count"]) )
            print( '-y,                  : amount of slices in y direction [{}]'.format(settings["row_count"]) )
            print( '-o,                  : setting output directory name [{}]'.format(settings["outputDirectory"]) )
            print( '-r,                  : remove existing slices in target directory [OFF]' )
            print( '-c                   : creating subfolders for each image [./{}/FILENAME/]'.format(settings["outputDirectory"]) )
            print( '-d                   : show debug output' )
            print( '' )
            sys.exit()
        elif opt in ("-o"):
            settings["outputDirectory"] = arg
            print( 'changed output directory to {}'.format(settings["outputDirectory"]) )
        elif opt in ("-r"):
            settings["overwrite_existing"] = True
            print( 'will overwrite existing slices' )
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

def getTargetFolder(settings, file_name):
    targetDirectory = settings["workingDirectory"] + os.sep + settings["outputDirectory"] + os.sep
    if settings["createFolderPerImage"]:
        targetDirectory += file_name + os.sep
    ## create output directory if it does not exist
    if not os.path.exists( targetDirectory ):
        os.makedirs( targetDirectory )
    return targetDirectory

# slice the source image to smaller tiles, saves it in the defined output folder and returns the scaling if available
def sliceImage( settings, file_name, file_extension=False, verbose=False ):
    # process file name
    if not file_extension == False:
        filename = file_name + file_extension
    else:
        filename = file_name
        file_name, file_extension = os.path.splitext( filename )
    if verbose: print( "  read scaling" )

    # get scaling
    scaling = es.getFEIScaling( filename, settings["workingDirectory"], verbose=verbose )
    if not scaling == False:
        noScaleBarDirectory = settings["workingDirectory"] + os.sep + 'no_scale_bar' + os.sep
        rsb.removeScaleBarPIL( settings["workingDirectory"], filename, noScaleBarDirectory, scaling=scaling )
        src_file = noScaleBarDirectory + filename
    else:
        scaling = es.autodetectScaling( filename, settings["workingDirectory"] )
        src_file = settings["workingDirectory"] + os.sep + filename

    # open image and get width/height
    if verbose: print( "  slicing file" )
    img = Image.open( src_file )
    width, height = img.size
    
    #cropping width / height
    crop_height = int(height/settings["row_count"])
    crop_width = int(width/settings["col_count"])

    slice_name=file_name + "_{}_{}"+ file_extension
    targetDirectory = getTargetFolder(settings, file_name)
    sclices_already_exists = True
    if not settings["overwrite_existing"]:
        for i in range(settings["row_count"]): # start at i = 0 to row_count-1
            for j in range(settings["col_count"]): # start at j = 0 to col_count-1
                fileij = slice_name.format(i, j)
                if not os.path.isfile( targetDirectory + fileij ):
                    sclices_already_exists = False
    else:
        sclices_already_exists = False

    if sclices_already_exists:
        print("  The expected sliced images already exists! Doing nothing...")
    else:
        for file_old in os.listdir(targetDirectory):
            if ( file_old.endswith( file_extension ) ):
                #if verbose: print("remove {}".formaT(targetDirectory + file_old))
                os.remove(targetDirectory + file_old)

        for i in range(settings["row_count"]): # start at i = 0 to row_count-1
            for j in range(settings["col_count"]): # start at j = 0 to col_count-1
                fileij = slice_name.format(i,j)
                if verbose: print( "   - " + fileij + ":" )
                cropped_filename = targetDirectory + fileij
                img.crop( ((j*crop_width), (i*crop_height), ((j+1)*crop_width), ((i+1)*crop_height)) ).save( cropped_filename, tiffinfo = ts.setImageJScaling( scaling ) )
    
    img=None
    return scaling

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
                sliceImage( settings, file_name, file_extension, verbose=settings["showDebuggingOutput"] )

    print( "Script DONE!" )