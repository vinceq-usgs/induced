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

def getEventFile(infile):
  print('Opening file',infile)
  f=open(infile,'r')
  results=json.load(f)
  print('Loaded',outfile,'with',len(results),'results.')
  return results


if __name__=='__main__':

  parser=argparse.ArgumentParser(description='Create a DYFI event dataset.')

  parser.add_argument('--output', type=str,
    default='../output/events.geojson',
    help='Output file, default ../output/events.geojson')

  parser.add_argument('--input',type=str,
    default='../input/dyfi.events.json',
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
    help='Collate the results with another induced events file')

  args=parser.parse_args()
  inputfile=args.input 
  outputfile=args.output
  startdate=args.start
  enddate=args.end
 
  # First, get the input list

  if not os.path.isfile(inputfile):
    print('Reading ComCat catalog.')
    input=Events(startdate,enddate).events
    print('Got',len(input),'events.')

    print('Creating',inputfile)
    with open(inputfile,'w') as f:
      json.dump(input,f,indent=2)
    exit()

  else:
    input=getEventFile(inputfile)

  if not input:
    print('Could not get any events from',inputfile)
    exit()

  # Then, filter the list in space and time

  # Now print output

  filteredresults=[]
  with open(outputfile,'w') as f:
    json.dumps(filteredresults)  

  exit()


def getInducedList(inducedfile):
    results=[]
    with open(inducedfile,'r') as f:
        for line in f:
            results.append(line)

    print('Got',len(results),'lines from',inducedfile)
    return results


def processLine(line):
    bits=re.split('\s+',line)
    lineFormat=('mag','lon','lat','depth','year','month','day',
            'hour','minute','second')

    eventData={} 
    c=0
    for key in lineFormat:
        if re.match('year|month|day|hour|minute',key):
            val=int(bits[c])
        elif key=='second':
            val=int(float(bits[c]))
        else:
            val=float(bits[c])
        eventData[key]=val
        c+=1

    return eventData


def checkdate(inducedEvent,eventlist):

    i=inducedEvent
    thistime=datetime.datetime(i['year'],i['month'],i['day'],
            i['hour'],i['minute'],int(i['second']),0)

    thisyear=str(int(inducedEvent['year']))
    events=eventlist[thisyear]

    for event in events:
        evdate=event['eventdatetime']
        evtime=datetime.datetime.strptime(evdate,'%Y-%m-%dT%H:%M:%S')
        diff=abs(evtime-thistime).total_seconds()
        if diff<5:
            return event
        if diff<120:
            print('Possible match, diff=',diff)

    return None

def checkmag(inducedEvent,matchEvent):
    magdiff=abs(inducedEvent['mag']-matchEvent['mag'])
    if magdiff<0.5:
        return True
    else:
        return False


if __name__=='__main__':
    exit()
    eventlist=getEventFile(eventsfile)
    inducedlist=getInducedList(inducedfile)

    nline=0
    nmatches=0
    allmatches={}

    for line in inducedlist:
        nline+=1
        inducedevent=processLine(line)

        # Now see if nline matches any events

        matchevent=checkdate(inducedevent,eventlist)
        matchmag=None
        if matchevent:
            matchmag=checkmag(inducedevent,matchevent)

        if matchevent and matchmag:

            print('Got match:',matchevent['eventid'],matchevent['eventdatetime'])
            nmatches+=1
            print('Got %i / %i matches so far.' % (nmatches,nline))
            matchevent['catalog']=line
            matchevent['catalogline']=nline
            allmatches[nline]=matchevent

    print('Writing',collatedfile)
    with open(collatedfile,'w') as f:
        f.write(json.dumps(allmatches,indent=4))

    exit()

# Make sure datafiles exist

    counter=0
    eventsfiletemplate='geocoded/%s_dyfi_geo10km.json'
    for event in eventlist:
        counter+=1
        evid=event['eventid']
        eventsfile=eventsfiletemplate % (evid)

        if os.path.isfile(eventsfile):
            # Output already exists, skipping
            continue

        else:
            print(counter,': Rerunning',evid)
            rerunEvent(evid,eventsfile)

    # Now load and collate

    locations={}
    counter=0
    for event in eventlist:
        counter+=1
        if counter%1000==0:
            print('%s: Collating %s (%s locs so far).' %
                    (counter,evid,len(locations)))

        evid=event['eventid']
        eventsfile=eventsfiletemplate % (evid)
        with open(eventsfile,'r') as f:
            locs=json.load(f)

        for feature in locs['features']:
            p=feature['properties']
            (utmcoord,name)=re.split('<br>',p['name'])

            # Populate event data

            eventdata={
                    'nresp':p['nresp'],
                    'cdi':p['cdi']
                    }
            for key in ('eventid','eventdatetime','mag',
                    'lat','lon'):
                eventdata[key]=event[key]

            if utmcoord not in locations:
                locations[utmcoord]={
                        'type':'Feature',
                        'geometry':copy.deepcopy(feature['geometry']),
                        'id':utmcoord,
                        'properties':{
                            'name':name,
                            'events':[]
                            }
                        }

            locations[utmcoord]['properties']['events'].append(eventdata)

    # At this point, all locations in all events are in locations dict
    # Now find nresponses and maxcdi

    print('Collating entry data.')
    for location in locations.values():
        maxcdi=None
        maxmag=None
        totalnresp=0
        numevents=0

        p=location['properties']
        for event in p['events']:
            totalnresp+=event['nresp']
            numevents+=1
            if not maxcdi or maxcdi<event['cdi']:
                maxcdi=event['cdi']
            if not maxmag or maxmag<event['mag']:
                maxmag=event['mag']

        p['maxcdi']=maxcdi
        p['totalresp']=totalnresp
        p['maxmag']=maxmag
        p['numevents']=numevents

    # Now turn into FeatureCollection and export

    collated={
            'type':'FeatureCollection',
            'features':locations
            }

    print('Writing',collatedfile)
    with open(collatedfile,'w') as f:
        f.write(json.dumps(collated,indent=4))




