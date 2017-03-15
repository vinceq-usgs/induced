#! /usr/bin/env python3

"""
makeEntries.py

This script will recreate the individual entries of the DYFI Induced Events Database. 

You must run in the DYFI home environment and access the DYFI database. If you are not the DYFI operator, DYFI individual entries contain private personal information and cannot be downloaded automatically. 

Instead, you can download the aggregated dataset instead using:

makeAggregated.py

Run with the -help flag to see options.
"""

import os.path
import json
import shutil
import re
import copy
import datetime
from geopy.distance import great_circle

from DyfiMysql import Db

targetMag=4.0
targetDist=20.0

eventsfile='data/allevents.json'
allentriesfile='entries.json'
entryfiletemplate='entries/raw.%s.json'

PRECISION=4

db=None

def getEventList(outfile):
    f=open(outfile,'r')
    results=json.load(f)
    print('Loaded',outfile,'with',len(results),'results.')

    return results

def getEntries(event):
    evid=event['eventid']
    entryfile=entryfiletemplate % evid

    try: 
        f=open(entryfile,'r')
        entries=json.load(f)
        assert len(entries)>0

    except:
        print('Loading from database.')
        entries=readExtendedTable(event)
        f=open(entryfile,'w')
        f.write(json.dumps(entries,indent=4,default=Db.serialize_datetime))
        print('Done writing',evid)

    return entries

def readExtendedTable(event):
    global db
    if not db:
        db=Db()

    evid=event['eventid']
    table=getTable(event)
    text='eventid="%s"' % evid
    results=db.query(table=table,text=text)
    print('Loaded',evid,'had',len(results),'results.')

    if not results:
        print('ERROR: No results found for',evid)
        exit()

    entries=[]
    for entry in results:
        dist=getDistance(event,entry)
        if not dist:
            continue

        newentry=sanitize(entry)
        newentry['dist']=dist
        entries.append(newentry)

    print('Geocoded',evid,'had',len(entries),'results.')
    return entries


def sanitize(entry):
    piilist=('comments','name','email','phone','street','response','situation','building','zip_latitude','zip_longitude')
    sanitized={}

    degradelist=('latitude','longitude')

    for key,val in entry.items():
        if val is None:
            continue
        if key in piilist:
            continue
        if key in degradelist:
            val=degradeVal(val)
        sanitized[key]=val
    
    return sanitized

def degradeVal(val):
    if isinstance(val,str):
        val=float(val)
    val=round(val,PRECISION)
    return val

def getDistance(event,entry):

    if 'latitude' in entry and 'longitude' in entry:
        lat=entry['latitude']
        lon=entry['longitude']

    if not lat and not lon and 'zip_latitude' in entry and 'zip_longitude' in entry:
        lat=entry['zip_latitude']
        lon=entry['zip_longitude']

    if not lat and not lon:
        print('Missing geo or zip coords.')
        print(entry)
        return None
  
    elat=event['lat']
    elon=event['lon']
    dist=great_circle((lat,lon),(elat,elon)).kilometers
    dist=float('%.1f' % dist)
    return dist



def getTable(event):
    datetime=event['eventdatetime']
    year=datetime[0:4]
    if int(year)<2003:
        year='pre'

    table='extended_%s' % year
    return table


if __name__=='__main__':

    eventlist=getEventList(eventsfile)
    counterMag=0
    counterDist=0
    counterDistMag=0

    for event in eventlist:

        magflag=False
        if event['mag']>=targetMag:
            magflag=True

        evid=event['eventid']
        nresp=event['nresponses']
        print('Trying',evid,'with',nresp,'responses.')

        entries=getEntries(event)

        if magflag:
            counterMag+=nresp

        for entry in entries:
            distflag=False
            if entry['dist']<=targetDist:
                distflag=True

                if distflag:
                    counterDist+=1
                if distflag and magflag:
                    counterDistMag+=1

        print('So far: n(M>%i)=%i, n(r<%i)=%i, n(both)=%i' % (
            targetMag,counterMag,targetDist,counterDist,counterDistMag))

        


