import re
import datetime
import geopy.distance

def readCollateFile(inducedfile):
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
    emag=event['properties']['mag']
    magdiff=abs(float(emag)-trymag)
    if magdiff<0.5:
        return True
    else:
        return False


def checkstamp(event,trystamp):
    eventstamp=int(int(event['properties']['time'])/1000)
    diff=abs(eventstamp-trystamp)

    if diff<=5:
        return True
    if diff<120:
        print('Possible match, diff=',diff)

    return False


def checkloc(event,lat,lon):

  (elon,elat,depth)=event['geometry']['coordinates']
  dist=geopy.distance.great_circle((lat,lon),(elat,elon)).kilometers
  return dist<5.0


