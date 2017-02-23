# dyfi-induced

* *Prototype* DYFI Induced Events database. A dataset of DYFI intensity observations for the Oklahoma and Kansas area between 2003 and 2016.

The goal of this project is to provide an observed intensity dataset that can be compared with the Oklahoma-Kansas Induced Earthquakes Database currently being developed(1). 

Two datasets are included: An aggregated dataset using publicly available aggregated data (in 1km and 10km UTM boxes(2)), and 

Users may also use the attached scripts to recreate the public component of the database by downloading and collating publicly available data from the USGS ComCat database. Users may update modify the event parameters (to capture different regions or time periods, for example) and create a new DYFI dataset using public data.

(1) See Rennolet, Moschetti, Thompson, and Yeck, 2016. A Flatfile of Ground Motion Intensity Measurements from Induced Earthquakes in Oklahoma and Kansas. Earthquake Spectra (submitted)

(2) For information on the UTM Grid see https://pubs.usgs.gov/fs/2001/0077/report.pdf

INCLUDED FILES
-------------

Input datasets
========

These input datasets can be found in the input/ directory.

- polygon_is_14_ok_comb.txt: Area polygon for the Kansas-Oklahoma study area, from Moschetti. Space-delimited text file.

- emm_c2_OK_KS.txt: List of event origins used for the ongoing study, from Moschetti(1). Tab-delimited text file.

- dyfi.events.geojson: Origin information for the DYFI induced event list. These include events matched to the above dataset, and those included in the area polygon. GeoJSON format.

Aggregated output
==============

For each event in the DYFI event origin list, we geocode the individual entries and aggregate them into 1 km and 10 km UTM boxes to compute the resulting intensities. These files can be found in the aggregated_10km/ and aggregated_1km/ directories. Each directory contains one file per event. GeoJSON format.

Individual entry data
==========

DYFI individual observations. These are DYFI questionnaires submitted by individual users. User comments and personal identity information have been removed, and geocoded locations degraded to 1km precision, to protect privacy. GeoJSON format.

Scripts
=======


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
