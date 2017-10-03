# dyfi-induced

DYFI INDUCED EVENTS DATABASE

A dataset of DYFI intensity observations for the Oklahoma and Kansas area between 2001 and 2016.

The goals of this project are:

1. To provide an observed intensity dataset that can be compared with the Oklahoma-Kansas Induced Earthquakes Database currently being developed(1). 

2. To allow users to create their own DYFI dataset with their own event parameters (for example, different regions or time periods) using these tools as a template.

Two datasets are included: 

1. An aggregated dataset using publicly available aggregated data (in 1km and 10km blocks using the UTM (2)), and 

2. The raw DYFI questionnaires for the OK-KS spatial boundary and date range, with Personally Identifiable Information (PII) redacted.

(1) See Rennolet, Moschetti, Thompson, and Yeck, 2016. A Flatfile of Ground Motion Intensity Measurements from Induced Earthquakes in Oklahoma and Kansas. Earthquake Spectra (submitted)

(2) For an explanation of the UTM Grid see https://pubs.usgs.gov/fs/2001/0077/report.pdf

This dataset can be found in the following locations:

- Github repository: https://github.com/vinceq-usgs/induced

- FTP site: ftp://hazards.cr.usgs.gov/dyfi/induced/

- On ScienceBase under DYFI data for Induced Earthquake Studies (https://www.sciencebase.gov/catalog/item/58efbad6e4b0eed1ab8e3d82)

INCLUDED FILES
-------------

Input files can be found in the 'input' directory.

Input catalog
========

catalog.json: All events from ComCat with DYFI products from 2001 to 2016. JSON format; each entry is an event. This file is current as of the file creation date and will be obsolete as ComCat is updated. To update, see the 'Programs' section below.

Input polygon
==========

polygon_is_14_ok_comb.txt: the area polygon for the Kansas-Oklahoma study area, from Moschetti. All events with epicenters inside the polygon are checked for inclusion in the induced events database. 

This is a space-delimited text file. Each line is a longitude-latitude pair that delineates the sides of the polygon. The first and last point is identical.

Events from the Moschetti study
==========

emm_c2_OK_KS.txt: a list of event origins used for the ongoing study from Moschetti(1) and used to collate with the DYFI event list. See that article for details on the file format.

Output event list
==========

output/dyfi.inducedevents.geojson: contains the set of all events within the Kansas-Oklahoma area that comprise the DYFI Induced Dataset. Each GeoJSON entry contains origin data (epicentral coordinates, origin time, and magnitude) and the line that corresponds to the Moschetti list of events, if found. GeoJSON format. To recreate this file using updated data or with a different set of parameters, see the 'Programs' section below.

Aggregated output
==============

For each event in the DYFI event origin list, we geocode the individual entries and aggregate them into 1 km and 10 km UTM boxes to compute the resulting intensities. These files can be found in the following directories:

- aggregated_10km/ 

- aggregated_1km/ 

Each directory contains a TAR'd, GZip'd file (aggregated_1km.geojson.tgz or aggregated_10km.geojson.tgz) that, when uncompressed, expands to one file per event in the DYFI Induced Catalog. Each event file is named with the event ID, in GeoJSON format. Each event contains one feature for each aggregated block with intensity data. 

For example, the file 'usc000twqf.dyfi_geo_1km.geojson' contains two 1km aggregated block features. Here is an example feature:

~~~
{"geometry":{"coordinates":[[[-97.57582,35.60434],[-97.56478,35.60421],[-97.56462,35.61323],[-97.57566,35.61336]]],"type":"Polygon"},"type":"Feature","properties":{"nresp":1,"name":"UTM:(14S 0629 3941 1000)<br>Oklahoma City","cdi":2.7,"dist":110}},{"geometry":{"coordinates":[[[-97.30744,36.286],[-97.29631,36.28584],[-97.29611,36.29485],[-97.30724,36.29501]]],"type":"Polygon"},"type":"Feature","properties":{"nresp":1,"name":"UTM:(14S 0652 4017 1000)<br>Perry","cdi":2,"dist":45}}
~~~

Each geometry feature is always a polygon (a rectangle delineating the 1km or 10km block of the UTM grid). Each block has the following properties:

- nresp: The number of responses contributing to this block for this event.

- name: The name of the block, which includes the UTM coordinates and (optionally) a city or nearest location name, separated by an HTML break.

- cdi: The Community Decimal Intensity (DYFI intensity) computed for this block.

Individual entry data
==========

The 'entries' directory contains the file raw.json.tgz. This is a TAR'd, GZip'd file that, when uncompressed, expands to one raw file per event in the DYFI Induced Catalog. Each file is a compilation of the results of the DYFI questionnaires for each event, submitted by individual users. User comments and personal identity information have been removed, and geocoded locations degraded to 1km precision, to protect privacy. GeoJSON format.

For example, the file 'raw.usc000twp6.json' contains 595 individual entries. Each entry will have the following fields:

- subid: unique ID for this entry

- exttable: The internal table this belongs to. Each entry has a unique subid and exttable.

- eventid: The event to which this entry is associated 

- orig_id: The event questionnaire originally used for this entry, before association (some entries were entered to an "unknown" event, or to the wrong event)

- suspect: This is set to a nonzero number if the associator believes it is a bogus entry

- region: The global region for this entry location (usually 'cus' for Central US)

- usertime: The user-entered time, for users who filled the "unknown event" questionnaire; otherwise, the time of the event questionnaire used

- time_now: The machine-generated time when the questionnaire was submitted

- latitude: The latitude of the user, as entered on the questionnaire or geolocated. This value is rounded to the nearest 0.01 degree to protect the user's privacy.

- longitude: The latitude of the user, as entered on the questionnaire or geolocated. This value is rounded to the nearest 0.01 degree to protect the user's privacy.

- asleep: Was the user asleep, and if so, was he/she woken up by the earthquake?

- felt, other_felt, motion, reaction, stand, sway, creak, shelf, picture, furnitude, heavy_appliance, walls, slide_1_foot, d_text: These values are used in the CDI calculation. See the DYFI documentation for details.

- user_cdi: The intensity calculated using the values of this entry alone (not necessarily the intensity of the area).

- confidence: A measure of the precision of the geolocation for this entry, from 0 (unknown) to 5 (rooftop precision).
 
Programs
=======

All programs can be found in the bin directory. For detailed instructions on running these programs, use the -h flag.

- makeEvents.py: Recreate the output catalog with custom parameters from the Comcat database or a custom input catalog. You may also update the included input catalog.

- makeAggregated.py: Recreate the aggregated DYFI dataset by pulling aggregated data from DYFI events in ComCat.

- makeEntries.py: Recreate the raw entries from the DYFI database. (For DYFI operators only.)

LICENSE
-------
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

