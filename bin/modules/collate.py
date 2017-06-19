'''
collate.py

A collection of functions to read and collate the relocated events
data provided by Moschetti et al. For the DYFI Induced Database,
this finds DYFI events (with DYFI intensities) that also exist 
in the Moschetti event list (which have instrumental data).

'''

import re
import datetime
import geopy.distance

# The following values are used to see if two events are identical

ALLOWED_MAGDIFF=0.2   # in magnitude units
ALLOWED_TIMEDIFF=5    # in seconds
ALLOWED_DISTDIFF=5.0  # in kilometers

def readCollateFile(inducedfile):
    """

    Read the relocated event file provided by Moschetti.
    You may have to edit this function if the file format changes.

    """

    LINEFORMAT=('mag','lon','lat','depth','year','month','day',
        'hour','minute','second')
    collatedata=[]
    with open(inducedfile,'r') as f:
        for line in f:
            eventData={'line':line}
            vals=re.split('\s+',line)
            for key in LINEFORMAT:
                val=vals.pop(0)
                if re.match('year|month|day|hour|minute',key):
                  val=int(val)
                elif key=='second':
                  val=int(float(val))
                else:
                  val=float(val)
                eventData[key]=val

            collatedata.append(eventData)

    print('Got',len(collatedata),'lines from',inducedfile)
    return collatedata


def collateEvents(events,tocollate):
    """

      Attempt to collate events between two datasets.

    """

    print('Attempting to locate',len(tocollate),'events in collate list.')

    c=0 
    ncollated=0
    for tryevent in tocollate:
      trymag=float(tryevent['mag'])
      trystamp=datetime.datetime(tryevent['year'],tryevent['month'],
        tryevent['day'],tryevent['hour'],tryevent['minute'],
        int(tryevent['second'])).timestamp()
      trylat=float(tryevent['lat'])
      trylon=float(tryevent['lon'])

      c=c+1
      if not c%1000:
        print('Collate event',c,'so far collated:',ncollated)

      for event in events:
        if not checkloc(event,trylat,trylon):
          continue
        if not checkmag(event,trymag):
          continue
        if not checkstamp(event,trystamp):
          continue

        event['properties']['line_collated']=c
        event['properties']['collated']=tryevent['line']
        ncollated+=1
        break

    print('Got',ncollated,'events were collated.')


def checkmag(event,trymag):
    """ Compare if two magnitudes are within the allowed diff """

    emag=event['properties']['mag']
    magdiff=abs(float(emag)-trymag)
    if magdiff<=ALLOWED_MAGDIFF:
        return True
    else:
        return False


def checkstamp(event,trystamp):
    """ Compare if two timestamps are within the allowed diff """

    eventstamp=int(int(event['properties']['time'])/1000)
    diff=abs(eventstamp-trystamp)

    if diff<=ALLOWED_TIMEDIFF:
        return True
    if diff<120:
        print('Possible match, diff=',diff)

    return False


def checkloc(event,lat,lon):
  """ Compare if two origins are close enough """

  (elon,elat,depth)=event['geometry']['coordinates']
  dist=geopy.distance.great_circle((lat,lon),(elat,elon)).kilometers
  return dist<=ALLOWED_DISTDIFF


