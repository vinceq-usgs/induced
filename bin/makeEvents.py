#! /usr/bin/env python3

"""
makeEvents.py

Create the event portion of the DYFI Induced Events Database for the Oklahoma-Kansas region. You can specify a different polygon file and date range to make your own dataset.

By default, this will download data from a copy of the 
DYFI catalog, included in this repository. You may also specify another
list of events. If that file does not exist, this script will attempt
to create it using ComCat.

Run with the -h flag to see options.
"""

import os.path
import json
import shutil
import re
import copy
import datetime
import argparse

from modules.comcat import Events,Event,Product
from modules.filter import TimeFilter,SpaceFilter
from modules.collate import readCollateFile,collateEvents

def getEventFile(infile):

  ACCEPTED_KEYS=['eventid','mag','max_intensity','nresponses','lat','lon','loc','depth','eventlocaltime','eventdatetime']

  print('Opening file',infile)
  f=open(infile,'r')
  results=json.load(f)

  for event in results['features']:
    p=event['properties']
    allkeys=list(p.keys())
    for key in allkeys:
      if key not in ACCEPTED_KEYS:
        p.pop(key, None)

  print('Loaded',infile,'with',len(results['features']),'results.')
  return results


if __name__=='__main__':

  parser=argparse.ArgumentParser(description='Create a DYFI event dataset.')

  parser.add_argument('--output', type=str,
    default='../output/events.geojson',
    help='Output file, default ../output/events.geojson')

  parser.add_argument('--input',type=str,
    default='../input/dyfi.catalog.geojson',
    help='Specify JSON file of input events. If this file does not exist, populate it using ComCat')

  parser.add_argument('--polyfile', type=str,
    default='../input/polygon_is_14_ok_comb.txt',
    help='Polygon spatial boundary file')

  parser.add_argument('--start', type=str,
    default='2001-01-01',
    help='Start date, default 2001-01-01')

  parser.add_argument('--end', type=str,
    default='2017-01-01',
    help='End date, default 2017-01-01')

  parser.add_argument('--collate',type=str,
    default='../input/emm_c2_OK_KS.txt',
    help='none, or collate the results with another induced events file')

  args=parser.parse_args()
  startdate=args.start
  enddate=args.end
 
  # First, get the input list

  inputfile=args.input 
  if not os.path.isfile(inputfile):
    print('Reading ComCat catalog.')
    input=Events(startdate,enddate).events
    print('Got',len(input),'events.')

    print('Creating',inputfile)
    with open(inputfile,'w') as f:
      json.dump(input,f,indent=2)

  else:
    input=getEventFile(inputfile)

  if not input:
    print('Could not get any events from',inputfile)
    exit()

  # Then, filter the list in space and time

  polyfile=args.polyfile
  tFilter=TimeFilter(startdate,enddate)
  sFilter=SpaceFilter(polyfile)

  filteredresults=[]
  for event in input['features']:
    if not sFilter(event['geometry']['coordinates']):
      continue

    p=event['properties']
    if 'time' in p:
      eventTime=p['time']
    elif 'eventdatetime' in p:
      eventTime=datetime.datetime.strptime(p['eventdatetime'],'%Y-%m-%dT%H:%M:%S').timestamp()
      eventTime=int(eventTime)*1000
      p['time']=eventTime
    else:
      print('Could not find event time:')
      print(event)
      exit()

    if not tFilter(eventTime):
      continue

    filteredresults.append(event)
  print('Got',len(filteredresults),'events passed filter.') 

  # Then, collate with induced file

  collatefile=args.collate
  if collatefile!='none': 
    collatedata=readCollateFile(collatefile)
    collateEvents(filteredresults,collatedata)

  # Turn into proper geojson

  geojsonresults={
    'type':'FeatureCollection',
    'features':filteredresults
  }

  # Then, print output

  outputfile=args.output
  print('Output file',outputfile)
  with open(outputfile,'w') as f:
    json.dump(geojsonresults,f,indent=2)  

  exit()


