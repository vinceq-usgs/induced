#! //anaconda/bin/python3

import json
import urllib.request
import re
import datetime 

class Comcat:

    SERVER = 'earthquake' #comcat server name
    URLBASE = 'http://[SERVER].usgs.gov/fdsnws/event/1/query?'.replace('[SERVER]',SERVER)
    ALLPRODURL = 'http://earthquake.usgs.gov/fdsnws/event/1/query?'

    def __init__(self,query):
       
        self.contents=None
        self.events=[]

        url=Comcat.URLBASE+query
        print('Requesting:',url)

        try:
          contents=urllib.request.urlopen(url).read().decode('utf8')
        except:
          print('No data found (is ComCat down?)') 
          return
       
        try: 
          contents=json.loads(contents)
        except:
          print('Could not parse JSON (server error?)')
          return

        self.contents=contents
        if 'features' in contents:
          self.events=contents['features']


class Events:

    QUERY='format=geojson&producttype=dyfi&starttime=[START]&endtime=[END]'
    EVENTPROPS = ['net','title','type','status','time','mag','cdi','updated','detail'] 

    def __init__(self,startdate,enddate):

      results=[]
      self.events=None
      for (startdate,enddate) in splitDates(startdate,enddate):
        print('Querying from',startdate,'to',enddate)
        query=Events.QUERY.replace('[START]',startdate).replace('[END]',enddate)

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
    
    QUERY='format=geojson&includesuperseded=[SUPERCEDED]&eventid=[EVENTID]'

    def __init__(self,evid,includeSuperseded=False):
        query=Event.QUERY.replace('[EVENTID]',evid)
        self.products=[]
        if includeSuperseded:
            superseded='true'
        else:
            superseded='false'
            
        query=query.replace('[SUPERCEDED]',superseded)
        contents=Comcat(query).contents
        self.contents=contents 
        if 'products' in contents['properties']:
          self.products=contents['properties']['products']


    def getProductList(self,type):
      if type not in self.products:
        print('Type',type,'not found')
        return

      products=self.products[type]
      print('There are',len(products),'products of type',type)
      if(len(products)>1):
        print(json.dumps(products,indent=2))
        exit()

      return list(products[0]['contents'].keys())


    def felt(self):
        try:
            p=self.contents['properties']
            return p['felt']
        except:
            return 0
       
 
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

def parseDyfiProps(props):
    for key in ['num-responses','numResp','maxmmi']:
        if key not in props:
            continue
        print('    ',key,':',props[key])

    return(props)

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
  if re.match('%d%d%d%d',date):
    return int(date)
  try:
    dt=datetime.datetime.strptime(date,'%Y-%m-%d')
    print('Got',dt)
    return int(dt.year)
  
  except:
    print('Invalid year',date)
    exit()


if __name__=='__main__':

    import sys
    args=sys.argv
    if len(args)<2:
        print('Usage: %s eventid' % args[0])
        exit()

    evid=args[1]
    print('Checking evid',evid)

    event=Event(evid)
    contents=event.contents

    print('Type: ',contents['type'])
    print('Id: ',contents['id'])
    print('Geometry:')
    print(contents['geometry'])

    p=contents['properties']
    print('Status:',p['status'])
    products=p['products']

    for key,val in products.items():
      print('Product:',key)

    exit()
    products=event.DYFIProducts()
    for product in products:
        product.parse()

        
        
    
    
                        
