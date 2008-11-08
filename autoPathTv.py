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
config['target_path'] = "/Volumes/ionDrive/video/tv/%(file_showname)s/season %(seasno)s/"


##############################################
# Regex configs

# Import shared filename pattern config
from filename_config import tv_regex

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

class ProgressBar:
    """From http://code.activestate.com/recipes/168639/"""
    def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string

    def updateAmount(self, newAmount = 0):
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = round(percentDone)
        percentDone = int(percentDone)

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # build a progress bar with hashes and spaces
        self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone)) 
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = (self.progBar[0:percentPlace] + percentString
                        + self.progBar[percentPlace+len(percentString):])

    def __str__(self):
        return str(self.progBar)

def copy_with_prog(src_file, dest_file, overwrite = False, block_size = 512):
    if not overwrite:
        if os.path.isfile(dest_file):
            raise IOError("File exists, not overwriting")
    
    # Open src and dest files, get src file size
    src = open(src_file, "rb")
    dest = open(dest_file, "wb")

    src_size = os.stat(src_file).st_size
    
    # Set progress bar
    prgb = ProgressBar(totalWidth = 79, maxValue = src_size)
    
    # Start copying file
    cur_block_pos = 0 # a running total of current position
    while True:
        cur_block = src.read(block_size)
        
        # Update progress bar
        prgb.updateAmount(cur_block_pos)
        cur_block_pos += block_size
        
        sys.stdout.write(
            '\r%s\r' % str(prgb)
        )
        
        # If it's the end of file
        if not cur_block:
            # ..write new line to prevent messing up terminal
            print # print line break to clear progress bar
            break
        else:
            # ..if not, write the block and continue
            dest.write(cur_block)
    #end while

    # Close files
    src.close()
    dest.close()

    # Check output file is same size as input one!
    dest_size = os.stat(dest_file).st_size

    if dest_size != src_size:
        raise IOError(
            "New file-size does not match original (src: %s, dest: %s)" % (
            src_size, dest_size)
        )


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
    Takes list of names, runs them though the tv_regex['with_ep_name'] regexs
    """
    allEps = []
    for f in names:
        filepath, filename = os.path.split( f )
        filename, ext = os.path.splitext( filename )
        
        # Remove leading . from extension
        ext = ext.replace(".", "", 1)
        
        for r in tv_regex['with_ep_name']:
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
        print "y/n/a/q?",
        ans = raw_input()
        if ans.lower() in ["y", "yes"]:
            return True
        elif ans.lower() in ["n", "no"]:
            return False
        elif ans.lower() in ["a", "always"]:
            return "always"
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
    
def same_partition(f1, f2):
    return os.stat(f1).st_dev == os.stat(f2).st_dev

###########################


def main():
    parser = OptionParser(usage="%prog [options] <file or directories>")
    parser.add_option("-a", "--always", dest = "always",
        action="store_true", default = False, 
        help="Do not ask for confirmation before copying")
    
    opts, args = parser.parse_args()
    
    files = findFiles(args)
    files = processNames(files)

    # Warn if no files are found, then exit
    if len(files) == 0:
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
        if ans == "always": opts.always = True
        
        if ans or opts.always:
            make_path(newpath)
            file_exists = does_file_exist(newfile)
            if file_exists:
                print "[!] File already exists, not copying"
            else:
                if same_partition(oldfile, newpath):
                    print "[*] Moving file"
                    try:
                        shutil.move(oldfile, newpath)
                    except Exception, errormsg:
                        print "[!] Error moving file! %s" % (errormsg)
                    #end try
                else:
                    print "[*] Copying file"
                    try:
                        copy_with_prog(oldfile, newfile)
                    except Exception, errormsg:
                        print "[!] Error copying file! %s" % (errormsg)
                    else:
                        print "[*] ..done"
                    #end try
                #end if same_partition
            #end if not file_exists
        else:
            print "Skipping file"
        #end if ans
    #end for name in files
#end main

if __name__ == '__main__':
    main()
