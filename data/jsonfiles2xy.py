#!/bin/env python3

# jsonfiles2xy.py
# Read all JSON individual entry files and convert into an xy file
# Output is entries.xy

import os
import os.path
import sys
import json

try:
  inputdir=sys.argv[1]
except:
  print('Usage: jsonfiles2xy.py [inputdir]')
  exit()

if not os.path.isdir(inputdir):
  print('inputdir must be a directory')
  exit()

print('Checking directory',inputdir)
nread=0
ngood=0
nskip=0
unsorted=[]
for filename in os.listdir(inputdir):
    fullname=inputdir+'/'+filename
    with open(fullname,'r') as f:
      entries=json.load(f)

      for entry in entries:
          nread+=1
          try:
            evid=entry['eventid']
            lat=entry['latitude']
            lon=entry['longitude']
            cdi=entry['user_cdi']
            line='%s %s %s' % (lon,lat,cdi)
            unsorted.append([cdi,line])
            ngood+=1
          except:
            nskip+=1
          if not (nread % 10000):
              print('Got',ngood,'lines so far, skipped',nskip)

print('Got',len(unsorted),'lines.')

sortedentries=sorted(unsorted,key=lambda entry: float(entry[0]))
with open('entries.xy','w') as o:
  for entry in sortedentries:
    o.write(entry[1]+'\n')

    
