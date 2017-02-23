#!/bin/env python3

# json2xy.py
# Convert a JSON file of events into an xy file of epicenters for plotting
# Output is events.xy

import sys
import json

def getsize(mag):
  mag=float(mag)
  if mag<2:
      return 2
  if mag<3:
      return 4
  if mag<4:
      return 6
  if mag<5:
      return 8
  return 10

try:
  inputfile=sys.argv[1]
except:
  print('Usage: json2xy.py [inputfile]')
  exit()

print(inputfile)

o=open('events.xy','w')
with open(inputfile,'r') as f:
  events=json.load(f)
  print('Got events:',len(events))

  for event in events:
      evid=event['eventid']
      lat=event['lat']
      lon=event['lon']
      mag=event['mag']
      size=getsize(mag)

      line='%s %s %s' % (lon,lat,size)
      o.write(line+'\n')

    
