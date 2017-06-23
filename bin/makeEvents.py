#! /usr/bin/env python3

descriptiontext='''

makeEvents.py

Create the event portion of the DYFI Induced Events Database for the 
Oklahoma-Kansas region. You can specify a different polygon file and 
date range to make your own dataset. Data will be downloaded from the
ComCat catalog. Alternatively, you can provide your own GeoJSON formatted
catalog as a base; for example, see the file 'input/catalog.json'.

'''

import os.path
import json
import geojson
import shutil
import re
import copy
import datetime
import argparse

from modules.comcat import Events,Event,Product
from modules.filter import TimeFilter,SpaceFilter
from modules.collate import readCollateFile,collateEvents

DEFAULT_CATALOG_FILE='../input/catalog.geojson'
DEFAULT_COLLATE_FILE='../input/emm_c2_OK_KS.txt'
DEFAULT_POLY_FILE='../input/polygon_is_14_ok_comb.txt'
DEFAULT_OUT_FILE='../output/dyfi.inducedevents.geojson'

def parseArgs():
  parser=argparse.ArgumentParser(
    description=descriptiontext,
    formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('--output', type=argparse.FileType('w'),
    default=DEFAULT_OUT_FILE,
    help='Output file, default is '+DEFAULT_OUT_FILE)

  parser.add_argument('--polyfile', type=argparse.FileType('r'),
    default=DEFAULT_POLY_FILE,
    help='Polygon spatial boundary file, default is '+DEFAULT_POLY_FILE)

  parser.add_argument('--start', type=str,
    default='2001-01-01',
    help='Start date, default 2001-01-01')

  parser.add_argument('--end', type=str,
    default='2003-01-01',
    help='End date, default 2017-01-01')

  parser.add_argument('--collate',type=argparse.FileType('r'),
    nargs='?',
    const=DEFAULT_COLLATE_FILE,
    help='collate the results with another induced events file, default is '+DEFAULT_COLLATE_FILE)

  parser.add_argument('--catalog',type=argparse.FileType('r'),
    nargs='?',
    const=DEFAULT_CATALOG_FILE,
    help='use a custom GeoJSON catalog file; without this flag, use ComCat instead. Default is '+DEFAULT_CATALOG_FILE)

  parser.add_argument('--savecatalog',type=argparse.FileType('w'),
    nargs='?',
    const=DEFAULT_CATALOG_FILE,
    help='save a custom GeoJSON catalog file from ComCat data, using the provided dates. Default is '+DEFAULT_CATALOG_FILE+'. Implies --catalog')

  print(parser.parse_args())
  return parser.parse_args()


def loadComCat(startdate,enddate):
  '''

    Read the online ComCat catalog for events in the selected timespan
    then process it into a GeoJSON file.

  '''

  raw=Events(startdate,enddate).events

  print('Loaded catalog with',len(raw),'results.')
  return geojson.FeatureCollection(raw)


if __name__=='__main__':

  args=parseArgs()
  startdate=args.start
  enddate=args.end
  input={}

  # First, get the input list, either from ComCat or from provided
  # catalog

  if args.catalog:
    print('Loading catalog file',args.catalog.name)
    input=json.load(args.catalog)

  else:
    print('Reading ComCat catalog.')
    input=loadComCat(startdate,enddate)

  if args.savecatalog:
    print('Saving ComCat catalog to',args.savecatalog.name)
    json.dump(input,args.savecatalog,indent=2)

  print('Got',len(input['features']),'events.')

  # Then, set up the two filters: spatial (from the polygon file), and time

  timeFilter=TimeFilter(startdate,enddate)
  spaceFilter=SpaceFilter(args.polyfile)

  # Loop through each event and check the filters

  filteredresults=[]
  for event in input['features']:
    if not spaceFilter(event['geometry']['coordinates']):
      continue

    p=event['properties']

    if 'time' in p:
      eventTime=p['time']
    elif 'eventdatetime' in p:
      eventTime=datetime.datetime.strptime(p['eventdatetime'],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=tz).timestamp()
      eventTime=int(eventTime)*1000
      p['time']=eventTime
    else:
      print('ERROR: Could not find event time:')
      print(event)
      print('Possible malformed input catalog, aborting.')
      exit()

    if not timeFilter(eventTime):
      continue

    # At this point, this event passed both filters
    filteredresults.append(event)

  print('Got',len(filteredresults),'events passed filters.') 

  # Then, collate with induced file

  collatefile=args.collate
  if collatefile:
    print('Collating with',collatefile.name)
    collatedata=readCollateFile(collatefile)
    collateEvents(filteredresults,collatedata)

  # Turn into proper geojson

  geojsonresults={
    'type':'FeatureCollection',
    'features':filteredresults
  }

  # Then, print output

  print('Output file',args.output.name)
  json.dump(geojsonresults,args.output,indent=2)  

  exit()


