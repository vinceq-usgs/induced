#! /bin/env python3
# Simple script to count nresponses from geojson file

import json

f=open('collated.geojson','r') 

data=json.load(f)
counter=0
for event in data.values():
    counter+=event['nresponses']
    print('Counter is now',counter)

