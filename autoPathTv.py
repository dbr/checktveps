#!/usr/bin/env python
#encoding:utf-8
"""
autoPathTv.py
Use at your own risk. "It works for me".

This parses "Show Name - [01x23] - Episode Name.avi"
filenames and automatically copies them to
/Volumes/aodDrive/video/tv/Show Name/season 1/

(obviously the path is changable, as is in the input 
format if you change the reges)
"""
import os, sys, re
from optparse import OptionParser
import shutil


config = {}
regex_config={}

##############################################
# Path configs

# Where to move the files
config['target_path'] = "/Volumes/aodDrive/video/tv/%(file_showname)s/season %(seasno)s/"


##############################################
# Regex configs

# Character class for valid episode/show names.
# Example: [a-zA-Z0-9\-'\ ]
regex_config['valid_in_names'] = "[\w\(\).,\[\]'\ \-?]"

config['name_parse'] = [
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(\d{2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(\d{2}-\d{2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(Special\d{1,2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})xExtra(\d{1,2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})] - (%(valid_in_names)s+)$" % (regex_config)),
]
# end configs
##############################################

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

def findFiles(args):
    """
    Takes a list of files/folders, grabs files inside them. Does not recurse
    more than one level (if a folder is supplied, it will list files within)
    """
    allfiles = []
    for cfile in args:
        if os.path.isdir(cfile):
            for sf in os.listdir(cfile):
                newpath = os.path.join(cfile, sf)
                if os.path.isfile(newpath):
                    allfiles.append(newpath)
                #end if isfile
            #end for sf
        elif os.path.isfile(cfile):
            allfiles.append(cfile)
        #end if isdir
    #end for cfile
    return allfiles
#end findFiles

def processNames(names, verbose=False):
    """
    Takes list of names, runs them though the config['name_parse'] regexs
    """
    allEps = []
    for f in names:
        filepath, filename = os.path.split( f )
        filename, ext = os.path.splitext( filename )
        
        # Remove leading . from extension
        ext = ext.replace(".", "", 1)
        
        for r in config['name_parse']:
            match = r.match(filename)
            if match:
                showname, seasno, epno, epname = match.groups()
                
                #remove ._- characters from name (- removed only if next to end of line)
                showname = re.sub("[\._]|\-(?=$)", " ", showname).strip()
                
                seasno, epno = int(seasno), int(epno)
                
                if verbose:
                    print "*"*20
                    print "File:", filename
                    print "Pattern:", r.pattern
                    print "Showname:", showname
                    print "Seas:", seasno
                    print "Ep:", epno
                    print "*"*20
                
                allEps.append({ 'file_showname':showname,
                                'seasno':seasno,
                                'epno':epno,
                                'filepath':filepath,
                                'filename':filename,
                                'ext':ext
                             })
                break # Matched - to the next file!
        else:
            print "Invalid name: %s" % (f)
        #end for r
    #end for f
    
    return allEps
#end processNames

def confirm(question="Rename files?"):
    ans = None
    while ans not in ["q", "quit"]:
        print "y/n/q?",
        ans = raw_input()
        if ans.lower() in ["y", "yes"]:
            return True
        elif ans.lower() in ["n", "no"]:
            return False
    else:
        sys.exit(1)
#end confirm

def make_path(path):
    try:
        os.makedirs(path)
    except OSError:
        print "Couldn't make path"
#end make_path

def does_file_exist(path):
    try:
        os.stat(path)
    except OSError:
        file_exists = False
    else:
        file_exists = True
    return file_exists
    

###########################


def main():
    
    parser = OptionParser(usage="%prog [options] <file or directories>")
    opts, args = parser.parse_args()
    
    files = findFiles(args)
    files = processNames(files)

    # Warn if no files are found, then exit
    if files.__len__() == 0:
        print colour('No files found','red')
        sys.exit(1)
    #end if files == 0

    for name in files:
        oldfile = os.path.join(name['filepath'], name['filename']) + "." + name['ext']
        newpath = config['target_path'] % name
        newfile = os.path.join(newpath, name['filename']) + "." + name['ext']
    
        print "Old path:", oldfile
        print "New path:", newfile
        ans=confirm()
        if ans:
            make_path(newpath)
            file_exists = does_file_exist(newfile)
            if file_exists:
                print "[!] File already exists, not copying"
            else:
                print "[*] Copying file"
                try:
                    shutil.copy(oldfile, newpath)
                except Exception, errormsg:
                    print "[!] Error copying file! %s" % (errormsg)
                else:
                    print "[*] ..done"
                #end try
            #end if not file_exists
        else:
            print "Skipping file"
        #end if ans
    #end for name in files
#end main

if __name__ == '__main__':
    main()
