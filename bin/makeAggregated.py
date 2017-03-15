#! /usr/bin/env python3

"""
makeAggregated.py

This script will recreate the aggregated intensity portion of the DYFI Induced Events Database. 

This script has two modes:

1. You can download the aggregated files from a list of events (created via makeEvents.py) from the ComCat online catalog.

2. If you have the individual entry files (created via makeEntries.py or downloaded from the DYFI operator), you can use those files as raw input to compute the aggregated intensities.

Run with the -help flag to see options.
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

def getEventList(eventfile):
    f=open(eventfile,'r')
    results=json.load(f)
    events=results['features']

    return events

def getAggregated(event):
    evid=event['id']
    try:
      event=Event(evid)
    except:
      print('Possible bad ID',evid)
      return

    productlist=event.getProductList('dyfi')
    products=[]
    try:
      products.append(event.loadProduct('dyfi','dyfi_geo_1km'))
      products.append(event.loadProduct('dyfi','dyfi_geo_10km'))
      return products
    except:
      print('Must rerun',evid)
      print(productlist)
      return


if __name__=='__main__':

  parser=argparse.ArgumentParser(description='Create a DYFI aggregated intensity dataset.')

  parser.add_argument('--output_1km', type=str,
    default='../aggregated_1km',
    help='Output directory. Default ../aggregated_1km')

  parser.add_argument('--output_10km', type=str,
    default='../aggregated_10km',
    help='Output directory. Default ../aggregated_10km')

  parser.add_argument('--input',type=str,
    default='../output/events.collated.geojson',
    help='Specify directory of JSON file of input events. Default ../output/events.collated.geojson')

  parser.add_argument('--entries',type=str,
    help='Specify directory of raw entry files. If not specified, download aggregated data from ComCat instead.')

  args=parser.parse_args()

  if args.entries:
    print('--entries flag not yet implemented.')
    exit()

  eventlist=getEventList(args.input)
  print('Got',len(eventlist),'events from',args.input)

  n=0
  nsuccess=0
  for event in eventlist:
    n+=1
    entries=getAggregated(event)
    if entries:
      nsuccess+=1

    print('n:',n,'event:',event['id'],'so far:',nsuccess)

        


