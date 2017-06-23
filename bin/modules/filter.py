"""
  A collection of time and space filters for checking event origins

"""

from matplotlib.path import Path
import numpy as np
import datetime

def TimeFilter(start,end):
  """ Create a filter function that takes two datestrings """ 

  tStart=datetime.datetime.strptime(start,'%Y-%m-%d')
  tEnd=datetime.datetime.strptime(end,'%Y-%m-%d')
  
  def filter(timestring):
    tEvent=datetime.datetime.fromtimestamp(int(timestring)/1000)
    return tStart<=tEvent and tEvent<=tEnd

  return filter


def SpaceFilter(polyfile):
  """ Create a filter function that takes a polygon file or file object """
  def loadPolyfile(file):
    rawArray=[]
    if isinstance(file,str):
      f=open(file,'r')
    else:
      f=file

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

