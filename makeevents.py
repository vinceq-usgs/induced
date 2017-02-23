#! /bin/env python3

"""Create the DYFI Induced Events Database for the Oklahoma-Kansas region.

This script will recreate the DYFI Induced Events Database. Note that it needs 
to run in the DYFI home environment and access the DYFI database
for the DYFI event and entry tables. If you are not a DYFI operator,
use the included flatfiles dyfi.events.json and dyfi.entries.json
which are copies of the DYFI database (stripped of personal identity
information).

Run with the -help flag to see options.
"""


import os.path
import json
#import subprocess
import os # Deprecated, redo using subprocess instead
import shutil
import re
import copy
import datetime

eventsfile='allevents.json' # All DYFI events
collatedfile='collated.geojson' # List of events in IDB
inducedfile='emm_c2_OK_KS.txt'

def getEventList(outfile):
    results=None
    try:
        f=open(outfile,'r')
        results=json.load(f)
        print('Loaded',outfile,'with',len(results),'results.')
        
    except:
        from DyfiMysql import Db
        db=Db()
        text='lat>=33.6 and lat<=37.6 and lon>=-99.5 and lon<=-95.6 and eventdatetime>="2001-01-01" and eventdatetime<="2016-12-01" and nresponses>1 and (invisible=0 or invisible is null)'
        results=db.query(table='event',text=text)

        with open(outfile,'w') as f:
            print('Writing to',outfile)

            f.write(json.dumps(results,indent=4,default=Db.serialize_datetime))
            print('Now need to filter this dataset via polygon.')
            exit()

    byyear={}
    for event in results:
        year=event['eventdatetime'][0:4]
        event['year']=year
        if year in byyear:
            byyear[year].append(event)
        else:
            byyear[year]=[ event ]

    return byyear


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

    eventlist=getEventList(eventsfile)
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




