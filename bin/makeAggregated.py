#! /usr/bin/env python3

descriptiontext="""
makeAggregated.py

This script will recreate the aggregated intensity portion of the 
DYFI Induced Events Database. It requires a list of events 
(default 'output/dyfi.inducedevents.geojson').

It will then poll the ComCat database for the data for each event
to produce its output.

"""

import os.path
import json
import shutil
import re
import copy
import datetime
import argparse

from modules.comcat import Event,Product

entryfiletemplate='entries/raw.%s.json'

DEFAULT_1KM_DIR='../aggregated_1km'
DEFAULT_10KM_DIR='../aggregated_10km'
DEFAULT_CATALOG='../output/dyfi.inducedevents.geojson'

def parseArgs():
  parser=argparse.ArgumentParser(
    description=descriptiontext,
    formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('--output_1km', type=str,
    default=DEFAULT_1KM_DIR,
    help='Output directory. Default '+DEFAULT_1KM_DIR)

  parser.add_argument('--output_10km', type=str,
    default=DEFAULT_10KM_DIR,
    help='Output directory. Default '+DEFAULT_10KM_DIR)

  parser.add_argument('--input',type=argparse.FileType('r'),
    default=DEFAULT_CATALOG,
    help='Specify GeoJSON event catalog. Default '+DEFAULT_CATALOG)

  parser.add_argument('--entries',type=str,
    help='Specify directory of raw entry files. If not specified, download aggregated data from ComCat instead.')

  parser.add_argument('--redo',action='store_true',
    help='Overwrite preexisting data')

  return parser.parse_args()


if __name__=='__main__':

  args=parseArgs()
  redo=args.redo

  if args.entries:
    print('--entries flag not yet implemented.')
    exit()

  # First read the catalog to get a list of events to extract

  try:
    eventgeojson=json.load(args.input)
    eventlist=eventgeojson['features']
  except:
    print('Could not read event catalog',args.input.name)
    print('Possible malformed JSON, aborting.')
    exit()

  print('Got',len(eventlist),'events from',args.input.name)

  # For each event, download the geocoded data (if needed)

  n=0
  nloaded=0
  for event in eventlist:
    n+=1
    evid=event['id'] 
    if event['properties']['felt']<1:
      continue

    outfiles={
      'dyfi_geo_1km.geojson':'%s/%s.%s.geojson' % (args.output_1km,evid,'dyfi_geo_1km'),
      'dyfi_geo_10km.geojson':'%s/%s.%s.geojson' % (args.output_10km,evid,'dyfi_geo_10km')
    }

    redo=False
    for whichproduct in outfiles.keys():
      outfile=outfiles[whichproduct] 
      if (not redo) and os.path.isfile(outfile):
        # File already exists, don't download again
        continue

      else:
        redo=True
        break

    if not redo:
      continue

    # From this point, we know we need to download this event from ComCat

    try:
      event=Event(evid)
    except:
      print('Could not get event information from',evid)
      exit()

    products=event.getProducts('dyfi')
    if not products:
      print('No product found (bad JSON?) for',evid)
      continue

    for whichproduct in outfiles.keys():
      if whichproduct in products:
        if event.saveFile(whichproduct,outfile):
          nloaded+=1
          continue
 
      # If we reach this point then something is wrong
 
      dyficode=event.code
      print('WARNING: Event',evid,'has no product',whichproduct)
      print('Operator needs to rerun DYFI for event',dyficode)
      print('DEBUG:')
      print('./ciim.pl event=%s -fast' % dyficode)
      break

    print('n:',n,'event:',evid,'loaded:',nloaded)

        


