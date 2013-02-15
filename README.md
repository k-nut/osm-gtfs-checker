osm-vbb-checker
===============

Compares the public transit data in OSM to the data published by the VBB


The VBB published some of its data under a cc-by license. This tool compares the stops (and at some point trains/buses/etc)
to the data that is in osm.

Requirements
------------
- flask
- flask-sqlalchemy
- requests

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
