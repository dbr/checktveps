#!/usr/bin/env python
#encoding:utf-8
import os, sys

# Import shared filename pattern config
from filename_config import tv_regex

def colour(text, colour="red"):
    nocolour = False
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
# Output-helper to convert array of 
# numbers (episode numbers) to human-readable string
###################################

def seq_display(x):
    """
    Takes an array of numbers, returns a more readable string representation of them
    
    >>> seq_display( [1,2,3, 5,6,7, 10, 20,21,22] )
    '1->3, 5->7, 10, 20->22'
    """
    is_int=[]
    non_int=[]
    for cur_x in x:
        if cur_x.find("-") != -1:
            for tmp_split in cur_x.split("-"):
                try:
                    tmp_conv = int(tmp_split)
                    is_int.append(tmp_conv)
                except ValueError:
                    non_int.append(cur_x)
                #end try
            #end for tmp_split
        try:
            tmp_conv = int(cur_x)
            is_int.append(tmp_conv)
        except ValueError:
            non_int.append(cur_x)
        #end try
    #end for cur_x
    
    if len(is_int) == 0: return x # return original input, no numbers!
    
    start = min(is_int)
    end = max(is_int)
    
    if end == start: return start
    if end - start > 999: return ", ".join([str(y) for y in x]) # too long, return list

    break_start = False

    out = ""

    for i in xrange(start, end + 1):
        try:
            is_int.index(i)
            if not break_start:
                break_start = i
        except ValueError:
            if break_start:
                if break_start == i - 1:  # start and end are same, its one number
                    out += "%d, " % (break_start)
                else:
                    out += "%d->%d, " % (break_start, i - 1)
                break_start = False
        #end try
    if break_start == i:
        out += "%d" % (break_start)
    else:
        out += "%d->%d" % (break_start, i) # last value

    return out
#end seq_display


###################################
# Classes to abstract show data
###################################
class ShowContainer:
    def __init__(self):
        self.shows = {}
    #end __init__
    
    def __getitem__(self, show_name):
        if not self.shows.has_key(show_name):
            self.shows[show_name] = Show(show_name)
        return dict.__getitem__(self.shows, show_name)
    #end __getitem__
    
    def __str__(self):
        out=""
        for current_show_name, current_show in sorted( self.shows.items() ):
            out += str(current_show) + "\n"
        return out
        
class Show:
    def __init__(self, name):
        self.show_name = name
        self.seasons = {}
    #end __init__
    
    def __getitem__(self,season_number):
        if not self.seasons.has_key(season_number):
            self.seasons[season_number] = Season(season_number)
        
        return dict.__getitem__(self.seasons, season_number)
    #end __getattr__
    
    def __setitem__(self,season_number, season):
        if not self.seasons.has_key(season_number):
            self.seasons[season_number] = Season(season_number)
        
        self.seasons[season_number] = season
    #end __setitem__
    
    def __str__(self):
        out = self.show_name + "\n"
        for cur_season_no, cur_season in sorted( self.seasons.items() ):
            out += str(cur_season) + "\n"
        return out
    #end __str__
#end Show

class Season:
    def __init__(self, number):
        self.season_number = number
        self.episodes = {}
    #end __init__
    
    def __getitem__(self, episode_number):
        if not self.episodes.has_key(episode_number):
            self.episodes[episode_number] = Episode(number = episode_number)
        
        return dict.__getitem__(self.episodes, episode_number)
    #end __getitem__
    
    def __setitem__(self,episode_number, episode):
        if not self.episodes.has_key(episode_number):
            self.episodes[episode_number] = Episode()
        
        self.episodes[episode_number] = episode
    #end __setitem__
    
    def __str__(self):
        out = "\tSeason %s\n" % (self.season_number)
        out += "\t\t"
        all_ep_nums = [cur_ep_num for cur_ep_num in self.episodes.keys() ]
        out += "Episodes " + str(seq_display(all_ep_nums))
        return out
    #end __str__
#end Season

class Episode:
    def __init__(self, number):
        self.episode_number = number
        self.episode={}
    #end __init__
    
    def __getitem__(self,attr):
        return dict.__getitem__(self.episode, attr)
    #end __getitem__
    
    def __setitem__(self,attr,name):
        dict.__setitem__(self.episode, attr, name)
    #end __setitem__
#end Episode


def find_files(loc):
    """Recursivly finds files in a directory
    """
    allfiles=[]
    for (path,dirs,files) in os.walk(loc):
        for file in files:
            filename = os.path.join(os.path.abspath(path), file)
            allfiles.append( str(filename) )
    return allfiles
#end find_files
   
 

def main():
    # Error-code to error-description mapping
    errors = {
        1:'malformed name',
        2:'missing epsiode name',
        3:'path is incorrect'
    }

    # Location to process
    loc = "." # Runs from the current path
    
    ###################################
    # Find all valid files
    ###################################
    allfiles = find_files(loc)
    
    # Strip out dotfiles/folder.jpg
    decrappified = []
    for current_file in allfiles:
        current_file_path,current_file_name = os.path.split(current_file)
        crappy = False
        for cur_decrap in tv_regex['decrappify']:
            if cur_decrap.match(current_file_name):
                crappy = True
                break
        if not crappy: decrappified.append(current_file)
    #end for current_file
    allfiles = decrappified

    # Warn if no files are found, then exit
    if len(allfiles) == 0:
        print colour('No files found','red')
        sys.exit(1)

    ###################################
    # Validate filenames
    ###################################

    valid   = []
    invalid = []

    for cur in allfiles:
        cpath,cfile = os.path.split(cur)
        cfile,cext = os.path.splitext(cfile)

        for cur_checker in tv_regex['valid_path']:
            # Check if path is valid
            check = cur_checker.findall(cpath)
            if check:
                break
        else:
            invalid.append({'errorno':3, 'path':cpath,'filename':cfile,
                            'cext':cext})
        #end for cur_checker

        for cur_checker in tv_regex['with_ep_name']:
            # Check if filename is valid (with ep name)
            check = cur_checker.findall(cfile)
            if check:
                # Valid file name
                valid.append({'path':cpath,'filename':cfile,
                                'cext':cext, 'match':check[0]})
                break # Found valid episode, skip to the next one
            #end if
        else:
            for cur_checker in tv_regex['missing_ep_name']:
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
        
            errormsg = "# %s (error code %d) #" % (errordescr, errorno)
            print "#"*len(errormsg)
            print errormsg
            print "#"*len(errormsg)
    
            for c in errors:
                cur_path = os.path.join(c['path'], c['filename'] + c['cext'])
                print cur_path

    ###################################
    # Show valid names
    ###################################
    if len(valid) > 0:
        print colour('INFO','green'), ': Valid file-names found:'
        allepisodes = ShowContainer()
    
        for cur in valid:
            if len(cur['match']) == 4:
                showname,seasno,epno,title = cur['match']
            elif len(cur['match']) == 3:
                seasno = 1
                showname,epno,title = cur['match']
        
            allepisodes[showname][seasno][epno]['name'] = title
        #end for cur in valid
        print allepisodes

if __name__ == '__main__':
    main()