#!/usr/bin/env python
#encoding:utf-8
import os,re,sys

###################################
# Configs
###################################

# Import shared filename pattern config
from filename_config import film_regex

# Location to process
loc = "." # Runs from the current path

###################################
# Helper functions
###################################

def colour(text,colour="red"):
    nocolour=False
    if nocolour: # Colour no supported, return plain text
        return text
    #end if

    c = {'red':'[31m',
         'green':'[32m',
         'blue':'[34m',
        }
    CLR=chr(27)+'[0m'
    if not colour in c.keys():
        raise ValueError("Invalid colour")
    else:
        return chr(27)+c[colour] + text + CLR
    #end if
#end colour

def getError(invalid,errorno):
    """Gets all invalid files with supplied error number"""
    ret = []
    for cur in invalid:
        if cur['errorno'] == errorno:
            ret.append(cur)
    return ret
#end searchError

###################################
# Find all valid files
###################################
allfiles=[]
for (path,dirs,files) in os.walk(loc):
    for file in files:
        filename = os.path.join(os.path.abspath(path),file)
        allfiles.append( str(filename) )
#end for f

# Strip out dotfiles/folder.jpg
for current_file in allfiles:
    current_file_path,current_file_name = os.path.split(current_file)
    for cur_decrap in film_regex['decrappify']:
        if cur_decrap.match(current_file_name):
            allfiles.remove(current_file)
#end for file

# Warn if no files are found, then exit
if allfiles.__len__() == 0:
    print colour('No files found','red')
    sys.exit(0)


errors = {
    1:'malformed name',
    2:'missing year',
    3:'path is incorrect'
}
###################################
# Validate filenames
###################################

valid   = []
invalid = []

for cur in allfiles:
    cpath,cfile = os.path.split(cur)
    cfile,cext = os.path.splitext(cfile)

    for cur_checker in film_regex['valid_path']:
        # Check if path is valid
        check = cur_checker.findall(cpath)
        if check:
            break
    else:
        print cpath, "doesnt match"
        invalid.append({'errorno':3, 'path':cpath,'filename':cfile,
                        'cext':cext})
    #end for cur_checker

    for cur_checker in film_regex['with_year']:
        # Check if filename is valid (with ep name)
        check = cur_checker.findall(cfile)
        if check:
            # Valid file name
            valid.append({'path':cpath,'filename':cfile,
                            'cext':cext})
            break # Found valid episode, skip to the next one
        #end if
    else:
        for cur_checker in film_regex['missing_year']:
            # Check for valid name with missing episode name
            check = cur_checker.findall(cfile)
            if check:
                invalid.append({'errorno':2, 'path':cpath,'filename':cfile,
                                'cext':cext})
                break
            #end if check
        else:
            # Doesn't match valid-name or missing-ep-name regexs, it's invalid
            invalid.append({'errorno':1, 'path':cpath,'filename':cfile,
                            'cext':cext})
        #end for cur_checker
    #end for cur_checker
#end for

###################################
# Show invalid names
###################################
for errorno,errordescr in errors.items():
    errors = getError(invalid,errorno)
    if len(errors) == 0: continue

    errmsg = "# %s (error code: %s)" % (errordescr,errorno)

    print
    print "#"*len(errmsg)
    print errmsg
    print "#"*len(errmsg)

    for c in errors:
        print c['filename']
