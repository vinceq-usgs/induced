# dyfi-induced
* *Prototype* DYFI Induced Events database. A dataset of DYFI intensity observations for the Oklahoma and Kansas area between 2003 and 2016.

The goal of this project is to provide an observed intensity dataset that can be compared with the Oklahoma-Kansas Induced Earthquakes Database currently being developed(1). 

(1) See Rennolet, Moschetti, Thompson, and Yeck, 2016. A Flatfile of Ground Motion Intensity Measurements from Induced Earthquakes in Oklahoma and Kansas. Earthquake Spectra (submitted)


Included files
---------------

polygon_is_14_ok_comb.txt
Area polygon, from Moschetti. Space-delimited text file.

emm_c2_OK_KS.txt
Event origin dataset used for the ongoing study, from Moschetti. Tab-delimited text file.

dyfi.allevents.geojson
DYFI event origin dataset. These include events matched to the above dataset, and those included in the area polygon. GeoJSON format.

DYFI geocoded and aggregated datasets. These are available in 1km and 10km box aggregated data. GeoJSON format.

DYFI individual observations. These are DYFI questionnaires submitted by individual users. User comments and personal identity information have been removed, and geocoded locations degraded to 1km precision, to protect privacy. GeoJSON format.



Observation selection criteria
---------


Notes on preliminary version
-----------------------

Output is a GeoJSON FeatureCollection file. 

LICENSE
-------
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

=======
# induced
DYFI Induced Events Database
