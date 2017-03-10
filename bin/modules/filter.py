from matplotlib.path import Path
import numpy as np
from datetime import datetime

def TimeFilter(start,end):
  tStart=datetime.strptime(start,'%Y-%m-%d')
  tEnd=datetime.strptime(end,'%Y-%m-%d')
  
  def filter(timestring):
    tEvent=datetime.fromtimestamp(int(timestring)/1000)
    return tStart<=tEvent and tEvent<=tEnd

  return filter


def SpaceFilter(polyfile):

  def loadPolyfile(file):
    rawArray=[]
    with open(file,'r') as f:
      for line in f:
        line=line.lstrip()
        (lon,lat)=line.split()
        rawArray.append([float(lon),float(lat)]) 

    # check that first and last points are the same
    firstPt=rawArray[0]
    if not (firstPt[0]==rawArray[-1][0]
      and firstPt[1]==rawArray[-1][1]):
      print('Adding first point as last point')
      rawArray.append([firstPt[0],firstPt[1]])

    return Path(rawArray)

  try:
    poly=loadPolyfile(polyfile)
  except:
    print('Unable to load polyfile',polyfile)
    exit()

  def filter(loc):
    # loc should be an array (lon,lat)
    isIn=poly.contains_point(loc)
    return isIn

  return filter

