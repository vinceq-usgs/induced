""" 

This code is a simplified version of the libcomcat library,
a Python interface to the USGS ComCat earthquake catalog. Among
other modifications, it only looks for events with DYFI products.

See https://github.com/usgs/libcomcat for details.

"""

import json
import urllib.request
import urllib.parse
import re
import datetime 

class Comcat:
    """ Query Comcat online server and turn results into JSON """

    SERVER = 'earthquake.usgs.gov' #comcat server name
    URLBASE = 'http://[SERVER]/fdsnws/event/1/query?'.replace('[SERVER]',SERVER)

    def __init__(self,query):
       
        self.contents=None
        self.events=[]

        url=Comcat.URLBASE+'&'+urllib.parse.urlencode(query)
        print('Requesting:',url)

        try:
          contents=urllib.request.urlopen(url).read().decode('utf8')
        except:
          print('No data found (is ComCat down?)') 
          return
     
        self.raw=contents 
        try: 
          contents=json.loads(contents)
        except:
          print('Could not parse JSON (server error?)')
          return

        self.contents=contents
        if 'features' in contents:
          self.events=contents['features']
        else:
          self.events=contents


class Events:
    """ Query Comcat server for list events with given start/end dates """

    EVENTPROPS = ['net','title','type','status','time','mag','cdi','felt','updated','detail'] 

    def __init__(self,startdate,enddate):

      results=[]
      self.events=None
      for (startdate,enddate) in splitDates(startdate,enddate):
        print('Querying from',startdate,'to',enddate)

        query={
          'format':'geojson',
          'producttype':'dyfi',
          'starttime':startdate,
          'endtime':enddate
        }

        events=Comcat(query).events
        if not events:
          return

        # Copy event data to new container

        thisresults=[]
        for event in events:
          eventdata={}
          for key,val in event.items():
            if key!='properties':
              eventdata[key]=val

          props={}
          p=event['properties']
          for prop in Events.EVENTPROPS:
            props[prop]=p[prop]

          eventdata['properties']=props
          thisresults.append(eventdata)

        if(thisresults):
          print('Got',len(thisresults),'results.')
          results.extend(thisresults) 

      print('Got total',len(results),'results.')
      self.events=results


class Event:
    """ Query ComCat server for a particular event ID """

    def __init__(self,evid,includeSuperseded=False):
        """ Begins with attributes 'evid','products','contents' """

        self.products=[]
        self.evid=evid

        if includeSuperseded:
            superseded='true'
        else:
            superseded='false'
            
        query={
          'format':'geojson',
          'eventid':evid,
          'includesuperseded':superseded
        }

        contents=Comcat(query).contents
        if not contents:
          return

        self.contents=contents 
        if 'products' in contents['properties']:
          self.products=contents['properties']['products']


    def getProducts(self,type):
      """ Gets the first set of products of a certain type. Adds 'code' and 'product' attributes """

      self.product=None

      if type not in self.products:
        print('Type',type,'not found for event',self.evid)
        return

      products=self.products[type]
      if(len(products)>1):
        print('WARNING: There are',len(products),'products of type',type)
        print('Taking the first one as authoritative')

      self.code=products[0]['code']
      self.product=products[0]['contents']
 
      # Now self.product has a dict keyed by product file
      return self.product

    def saveFile(self,productname,outfile):
      """ Save a product. Requires getProducts to be run"""

      if not self.product:
        print('ERROR: Must run getProducts first')
        exit()

      try:
        pdata=self.product[productname]
        url=pdata['url']
        print('Downloading url',url)
        contents=urllib.request.urlopen(url).read().decode('utf8')

      except:
        print('Could not save',productname,'(skipping)')
        return

      print('Writing to',outfile)
      jdata=json.loads(contents)
      if not jdata['features']:
        return

      # Prettyprint the JSON file
 
      with open(outfile,'w') as f:
        json.dump(json.loads(contents),f,indent=2)
      return True


    # XXXX Not used so far
    def felt(self):
        try:
            p=self.contents['properties']
            return p['felt']
        except:
            return 0
       
 
# XXXX Not used by getEvents
class Product:
    
    def __init__(self,rawdata):
        self.data=rawdata
        self.status=rawdata['status']
    
    def parse(self):

        prod=self.data
        print('  Code:',prod['code'])
        print('  Status:',prod['status'])

        if (prod['status']=='DELETED'):
            return product

        if 'properties' in prod:
            parseDyfiProps(prod['properties'])
        else:
            print('WARNING: no properties, probably older DYFI')
            for (key,val) in prod.items():
                if isinstance(val,(str,int,float)):
                    print(key,':',val)
        
        
        return prod

    def nresponses(self):

        if 'properties' in self.data:
            p=self.data['properties']
            if 'num-responses' in p:
                nresp=p['num-responses']
            elif 'numResp' in p:
                nresp=p['numResp']
            else:
                print('Product: Missing nresp!')
                exit()
        else:
            print('Product has no nresponses property.')
            return 0
                
        return nresp
    
    def eventid(self):
        return self.data['code']
        
    
# These are functions, not methods    

# XXXX Not used
def parseDyfiProps(props):
    for key in ['num-responses','numResp','maxmmi']:
        if key not in props:
            continue
        print('    ',key,':',props[key])

    return(props)


# XXXX Not used
def display(data):
    if not isinstance(data,dict):
        print('Cannot display non-dict data',data)
        exit()
        
    for (key,val) in data.items():
        if isinstance(val,(dict,list)):
            print(key,':',type(val))
        else:
            print(key,':',val)
    
    return


def splitDates(start,end):
  """ 

    Used by Events class to take a multiyear start date and end date,
    then split it into multiple years for querying Comcat multiple times.
    Otherwise, querying Comcat with a large date range can result in
    network timeouts.

  """

  startyear=getYear(start)
  endyear=getYear(end)
   
  if startyear==endyear:
    return (startyear,endyear)

  dates=[]
  for year in range(startyear,endyear+1):
    if year==startyear:
      thisStart=start+'T00:00:00'
    else:
      thisStart=str(year)+'-01-01T00:00:00'

    if year==endyear:
      thisEnd=end+'T00:00:00'
    else:
      thisEnd=str(year+1)+'-01-01T00:00:00'

    if thisStart!=thisEnd:
      dates.append((thisStart,thisEnd))

  return dates

def getYear(date):
  """ Used by splitDates to extract year from date string """

  if re.match('%d%d%d%d',date):
    return int(date)
  try:
    dt=datetime.datetime.strptime(date,'%Y-%m-%d')
    print('Got',dt)
    return int(dt.year)
  
  except:
    print('Invalid year',date)
    exit()

