[![Build Status](https://travis-ci.org/k-nut/osm-vbb-checker.png?branch=master)](https://travis-ci.org/k-nut/osm-vbb-checker)
osm-gtfs-checker
===============

Compares the public transit data in OSM to the data published by a GTFS-provider.



Requirements
------------
- flask
- flask-sqlalchemy
- requests


Setup
-----
There are two predefined config files. Those are for the city of Ulm and for Berlin. Simply rename one of them to ```config.py``` or create your own config file.


Deploy
------

To install the dependencies and create the initial database use:

    pip install -r requirements.txt
    ./deploy.py

Arguments
---------
If you are in development mode you might want to pass ``` --verbose ``` to routes.py

License
-------
Published under the MIT License. Refer to the LICENSE.txt for a copy of the license.
