[![Build Status](https://travis-ci.org/k-nut/osm-gtfs-checker.png?branch=master)](https://travis-ci.org/k-nut/osm-gtfs-checker)osm-gtfs-checker

OSM GTFS Checker
===============

Compares the public transit data in OpenStreetMap (OSM) to the data published by a GTFS-provider.


Setup & config
--------------
First install the dependencies:
```
pip install -r requirements.txt
```


There are two predefined config files. Those are for the city of Ulm and for Berlin. Simply rename one of them to `config.py` or create your own config file.
You should also set a couple of environment variables:

```
DATABASE_URL: #The URL to you database e.g. postgres://postgres@0.0.0.0:5432/osm-checker
OSM_CHECKER_APP_NAME="Ulmer OSM Haltestellen-Validator"
OSM_CHECKER_LAT=48.35
OSM_CHECKER_LON=10.00
OSM_CHECKER_STOPS_TXT_URL="https://gtfs.swu.de/daten/stops.txt"
OSM_CHECKER_ATTRIBUTION="The data provider (http://example.org)"
```

After you configured your databse you should create the database by running:
```
flask db init
flask db upgrade
```

Initial import
--------------

To run an initial import for all stops from your data provider run

```
flask import-stops
```

Arguments
---------
If you are in development mode you might want to pass ``` --verbose ``` to app.py

License
-------
Published under the MIT License. Refer to the LICENSE.txt for a copy of the license.
