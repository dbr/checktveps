#!/usr/bin/env python
#encoding:utf-8
import os,re,sys
###################################
# Colourized output helper
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

###################################
# Valid-name regex.
###################################
# Should return 4 groups:
# Series name.
# Season number.
# Episode number#
# Episode name. (can be empty)
#
# Valid episode names:
# Show name - [01x01-02] - The Episode Name (Part 1)
# Show name - [01x23] - The Episode Name (Part 1)
# Show name - [01x23] - The Episode Name
# Show name - [04x01]
tv_ep_name = re.compile("([-\w ]+) - \[(\d{2})x(\d{2}|\d{2}-\d{2})\](?= - ([\w\(\) ]+))?")

###################################
# Regex to match valid, but not-to-be-processed files (dot-files, folder.jpg artwork)
###################################
decrappify = re.compile("(?=^[.]{1}.*|folder.jpg)")

# Location to process
loc = "." # Runs from the current path

###################################
# Find all valid files
###################################
#TODO: Use os.path.walk() so no external dependancies!
#TODO: Array of valid extensions (not just .avi)
import path
d = path.path(loc)
list=[]
for f in d.walkfiles("*.avi"):
	list.append( str(f) )

#Old, non-recursive version (that doesn't need the path.py module): 
#list = os.listdir(loc) # list dir

list = [x for x in list if decrappify.match(x)] # Strip out dotfiles/folder.jpg
list = [os.path.join(loc,x) for x in list] # append path to file name
files = [x for x in list if os.path.isfile(x)] # only get files, not folders

# Warn if no files are found, then exit
if files.__len__() == 0:
	print colour('No files found','red')
	sys.exit(0)

###################################
# Validate filenames
###################################

valid   = []
invalid = []

for cur in files:
	check = tv_ep_name.findall(cur)
	if check:
		# Valid file name
		valid.append(check)
	else:
		# Invalid name
		invalid.append(cur)
	#end if
#end for

###################################
# Show invalid names
###################################

if invalid.__len__() > 0:
	print colour('WARNING','red')
	print '[!] Invalid file-names found:'
	print '\n'.join(invalid)

	print "-" * 28
	print

###################################
# Show valid names
###################################

if valid.__len__() > 0:
	print '[?] Valid file-names found:'
	allepisodes = {}
	
	# Make a dict of shows, each show contains an array of episode-info. 
	# Example:
	# { 'showname': [ [1,24,'Title'], ], 
	#   'another': [ [4,12,'More'], [4,13,'Stuff'], ]
	# }
	# This could(/should) change into something more managable.
	
	for x in valid:
		showname,season,epno,title = x[0] # Put regex-groups into named vars
		
		if allepisodes.has_key(showname): # Does the show exist in allepisodes?
			allepisodes[showname].append([season,epno,title]) # yes, append episode
		else:
			allepisodes[showname] = [[season,epno,title]] # no, init episodes array
	#end for x
	
	# Now we have a nice dict of all shows, output them as:
	# Showname
	#     Season 01
	#         Episodes 01, 02, 03
	#     Season 01
	#         Episodes 01, 02
	
	for showname,alleps in allepisodes.items():
		print colour(showname,'green')
		
		# Make a dict for the current show,
		# an index for each season, containing an array of episodes.
		# Example:
		# { '02' : [20,21,22,23],
		#   '03' : [01,02,03]
		# }
		# This is for ease-of-output. It'd be possible to work
		# directly of the allepisodes dict, but a lot messier..
		curshow={}
		for curep in alleps:
			season,epno,title = curep
			try:
				season = int(season)
			except ValueError:
				print "Error: Season number not integer. Check naming or tv_ep_name regex."
			#end try
			try:
				epno = int(epno)
			except:
				# deal with episode numbered like - [01x01-02]
				# TODO: Currently very hackish, improve the handling of [01x01-02] names
				split_two_eps = epno.split("-")
				if len(split_two_eps) == 2:
					p1,p2 = split_two_eps
					epno,ep2 = int(p1),int(p2)
					
					# Add the second part, then add the first as usual. Messy, but works
					if curshow.has_key(season):
						curshow[season].append(ep2)
					else:
						curshow[season]=[ep2]
					#end if curshow
				else:
					print "Error: Episode number not integer, or two integers (01-02)"
			#end try
			
			if curshow.has_key(season):
				curshow[season].append(epno)
			else:
				curshow[season]=[epno]
		#end for curep
		
		for seas,eps in curshow.items():
			# Check for missing episodes (by looking for gaps in sequence)
			mi,ma=int(min(eps)),int(max(eps))
			missing_eps=[]
			for x in range(1,int(ma)+1):
				try:
					if not x in [int(y) for y in eps]:
						missing_eps.append(x)
				except ValueError:
					pass # start value is 01-02 probably.
				#end try
			#end for x
				
			# if we are missing an episode, "season 01" title becomes red.
			if missing_eps.__len__() == 0:
				cur_colour = "blue"
			else:
				cur_colour = "blue"
			
			# Print season title in above colour.
			print "\t",colour("Season " + str(seas),colour=cur_colour)
			# And list episodes
			print "\t\t", "Episodes:", ", ".join([str(e) for e in eps])
			# And if there is missing episodes, list them.
			if missing_eps.__len__() != 0:
				print "\t\t","Missing:", ", ".join([str(m) for m in missing_eps])
		#end for seas,eps
