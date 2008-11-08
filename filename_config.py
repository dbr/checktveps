#!/usr/bin/env python
#encoding:utf-8

import re

# Regex configs
regex_config={}

# Character class for valid episode/show names.
# Example: [a-zA-Z0-9\-'\ ]
regex_config['valid_in_names'] = "[\w\(\).,\[\]'\ \-?!#]"


tv_regex = {}

###################################
# TV Filename Regexs
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

tv_regex['with_ep_name'] = [
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(\d{2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(\d{2}-\d{2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})x(Special\d{1,2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})xExtra(\d{1,2})\] - (%(valid_in_names)s+)$" % (regex_config)),
    re.compile("^(%(valid_in_names)s+) - \[(\d{2})] - (%(valid_in_names)s+)$" % (regex_config)),
]

###################################
# Valid filenames, but missing episode name
#
# Show name - [04x01]
# Show name - [04x01-02]
# Show name - [04xSpecial01]
# Show name - [04xExtra01]
tv_regex['missing_ep_name'] = [
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(\d{2}-\d{2})\]"% (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Special\d{1,2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Extra\d{1,2})\]" % (regex_config)),
    re.compile("(%(valid_in_names)s+) - \[(\d{2})x(Extra\d{1,2})\]" % (regex_config))
]

# Valid path names
tv_regex['valid_path'] = [
    re.compile("/./(.+?)/season (\d{1,2})$"),
    re.compile("/./(.+?)/season (\d{1,2}) \[720p\]$"),
    re.compile("/./(.+?)/season (\d{1,2})/extras$"),
    re.compile(".+?/Misc")
]

###################################
# Regex to match valid, but not-to-be-processed files (dot-files, folder.jpg artwork)
###################################
tv_regex['decrappify'] = [
    re.compile("^Icon.{1}$"),
    re.compile("(?=^[.]{1}.*)"),
    re.compile("^folder.jpg$"),
]



film_regex = {}
###################################
# Film Filename Regexs
###################################
# Valid filenames
# Should return 2 groups:
# Film name.
# Year.
#
# Ignore filetype extension
#
# The Film [2004]
film_regex['with_year'] = [
    re.compile("(%(valid_in_names)s+) \[(\d{4})\]$" % (regex_config))
]


###################################
# Valid filenames, but missing year
#
# The Film
film_regex['missing_year'] = [
    re.compile("(%(valid_in_names)s+)$" % (regex_config)),
]

###################################
# Valid paths
#
# ./
# 

film_regex['valid_path'] = [
    re.compile(".*?/video/films$"),
    re.compile(".*?/video/films/Short Films(/.*?)?")
]

###################################
# Regex to match valid, but not-to-be-processed files (dot-files, Icon)
###################################
film_regex['decrappify'] = [
    re.compile("^Icon.{1}$"),
    re.compile("(?=^[.]{1}.*)")
]
