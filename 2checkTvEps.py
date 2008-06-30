#!/usr/bin/env python
#encoding:utf-8
import os,re,sys

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
# Configs
###################################

# Error-code to error-description mapping
errors = {
    1:'malformed name',
    2:'missing epsiode name',
    3:'path is incorrect'
}

# Regex configs
regex_config={}

# Character class for valid episode/show names.
# Example: [a-zA-Z0-9\-'\ ]
regex_config['valid_in_names'] = "[\w\(\).'\ \-]"

# Location to process
loc = "." # Runs from the current path

###################################
# Name regexs
###################################
# Valid filenames, with episode name
# Should return 4 groups:
# Series name.
# Season number.
# Episode number.
# Episode name.
# Ignore filetype extension.
#
# If there are 3 groups, they are treated as:
# Series name, epiosde number, episode name. Season number is defaulted to "1"
#
# Show name - [01x01-02] - The Episode Name (Part 1)
# Show name - [01x23] - The Episode Name (Part 1)
# Show name - [01x23] - The Episode Name
# Show name - [01xExtra01] - DVD Extra Feature 1
# Show name - [01xSpecial01] - Special Episode 1
# Show name - [01] - First episode

r_with_ep_name = [
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2})\] - (%(valid_in_names)s+)" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2}-\d{2})\] - (%(valid_in_names)s+)" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Special\d{1,2})\] - (%(valid_in_names)s+)" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})xExtra(\d{1,2})\] - (%(valid_in_names)s+)" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})] - (%(valid_in_names)s+)$" % (regex_config)),
]

###################################
# Valid filenames, but missing episode name
#
# Show name - [04x01]
# Show name - [04x01-02]
# Show name - [04xSpecial01]
# Show name - [04xExtra01]
r_missing_ep_name = [
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2}-\d{2})\]"% (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Special\d{1,2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Extra\d{1,2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Extra\d{1,2})\]" % (regex_config))
]

# Valid path names
r_valid_path = [
    re.compile("/(.+?)/season (\d{1,2})$"),
    re.compile("/(.+?)/season (\d{1,2})/extras$"),
    re.compile(".+?/Misc")
]

###################################
# Regex to match valid, but not-to-be-processed files (dot-files, folder.jpg artwork)
###################################
decrappify = [
    re.compile("(?=^[.]{1}.*)"),
    re.compile("folder.jpg"),
]

# Location to process
loc = "." # Runs from the current path

###################################
# Find all valid files
###################################
allfiles=[]
for (path,dirs,files) in os.walk(loc):
    for file in files:
        filename = os.path.join(path,file)
        allfiles.append( str(filename) )
#end for f

files = [x for x in allfiles if os.path.isfile(x)] # only get files, not folders

# Strip out dotfiles/folder.jpg
for current_file in allfiles:
    current_file_path,current_file_name = os.path.split(current_file)
    for cur_decrap in decrappify:
        if cur_decrap.match(current_file_name):
            files.remove(current_file)
#end for current_file

files = [os.path.join(loc,x) for x in files] # append path to file name

# Warn if no files are found, then exit
if files.__len__() == 0:
    print colour('No files found','red')
    sys.exit(1)


errors = {
    1:'malformed name',
    2:'missing epsiode name',
    3:'path is incorrect'
}


###################################
# Validate filenames
###################################

valid   = []
invalid = []

for cur in files:
    cpath,cfile = os.path.split(cur)
    cfile,cext = os.path.splitext(cfile)

    for cur_checker in r_valid_path:
        # Check if path is valid
        check = cur_checker.findall(cpath)
        if check:
            break
    else:
        print "invalid path",cpath
        invalid.append({'errorno':3, 'path':cpath,'filename':cfile,
                        'cext':cext})
    #end for cur_checker

    for cur_checker in r_with_ep_name:
        # Check if filename is valid (with ep name)
        check = cur_checker.findall(cfile)
        if check:
            # Valid file name
            valid.append({'path':cpath,'filename':cfile,
                            'cext':cext, 'match':check[0]})
            break # Found valid episode, skip to the next one
        #end if
    else:
        for cur_checker in r_missing_ep_name:
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
if len(invalid) > 0:
    print colour('WARNING', 'red'), ': Invalid file-names found'
    
    for errorno,errordescr in errors.items():
        errors = getError(invalid,errorno)
        if len(errors) == 0: continue
        
        errormsg = "# %s (error code %d)" % (errordescr, errorno)
        print "#"*len(errormsg)
        print errormsg
        print "#"*len(errormsg)
    
        for c in errors:
            print c['filename']
