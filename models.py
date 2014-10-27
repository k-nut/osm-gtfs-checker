#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import config
import logging

import os
import datetime
import difflib
import json

from helpers import get_county

app = Flask(__name__, instance_relative_config=True)
path_to_db = os.path.expanduser(config.db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + path_to_db
db = SQLAlchemy(app)


class Stop(db.Model):
    ''' The represenation of a stop in the database '''
    id = db.Column(db.Integer, primary_key=True)
    last_run = db.Column(db.DateTime)
    name = db.Column(db.String(200), index=True)
    matches = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    county = db.Column(db.String)
    turbo_url = db.Column(db.String)
    isStation = db.Column(db.Boolean)
    exception = db.Column(db.String)
    names_in_osm = db.Column(db.String)

    def __init__(self, line_from_stops_txt, exception=None):
        self.id = int(line_from_stops_txt["stop_id"])
        self.name = line_from_stops_txt["stop_name"]
        self.lat = float(line_from_stops_txt["stop_lat"])
        self.lon = float(line_from_stops_txt["stop_lon"])
        parent_station = line_from_stops_txt["parent_station"]
        if parent_station == "":
            self.isStation = True
        else:
            self.isStaion = False
        self.exception = exception
        self.turbo_url = "http://overpass-turbo.eu/?Q=" + \
            self.create_payload()["data"] + '&R'
        self.county = get_county(self.lat, self.lon)

    def update(self):
        self.matches = self.is_in_osm()
        self.last_run = datetime.datetime.now().replace(microsecond=0)

    def get_short_name(self):
        short_name = self.name

        # in the smaller cities there are some stops that are just
        # <name of the village>, Bahnhof.
        # in osm those are just the village name without the "Bahnhof"
        # so we filter for that special case
        if short_name.endswith(", Bahnhof"):
            short_name = short_name.split(", Bahnhof")[0]

        if (", ") in short_name:
            short_name = short_name.split(", ")[1]

        if "(" in short_name:  # remove the (Berlin) from the line
            short_name = short_name.split(" (")[0]
            short_name = short_name.split("(")[0]

        # if we have something like StreetA/StreetB overpass is not able to find this
        # we can just look for StreetB or StreetA though since we are limiting the search on a small ara
        if "/" in short_name:
            short_name = short_name.replace("/", "|")

        # In Osm "Spandau Bhf" is just "Spandau" so we drop the "Bhf"
        if "Bhf" in short_name:
            short_name = short_name.replace(" Bhf", "")

        if "Str." in short_name:
            parts = short_name.split("Str.")
            short_name = short_name + "|" + parts[0] + u"Straße"

        if "str." in short_name:
            short_name = short_name + "|" + short_name.replace(u"str.", u"straße")

        if "S+U" in short_name:
            # Stops Like "S+U Wedding" are in OSM as "S Wedding" and "U Wedding"
            # So we split it up and check for both
            stop_name = short_name[3:]  # Take the part without "S+U"
            s_station = "S" + stop_name
            u_station = "U" + stop_name
            short_name = s_station + "|" + u_station

        if self.exception:
            short_name = short_name + "|" + self.exception

        return short_name

    def create_payload(self):
        short_name = self.get_short_name()
        payload = {"data": """
        [out:json];
        (
        node(around: 250, %(lat)f, %(lon)f)
        ["highway"="bus_stop"];
        node(around: 250, %(lat)f, %(lon)f)
        ["railway"="tram_stop"];
        node(around: 250, %(lat)f, %(lon)f)
        ["railway"="station"];
        node(around: 250, %(lat)f, %(lon)f)
        ["public_transport"="stop_position"];
        );
        out;
        """ % {'lat': self.lat, 'lon': self.lon}}
        return payload

    def is_in_osm(self):
        ''' Call Overpass to see if there are public transportation stops
        close to the cordinates given '''
        short_name = self.get_short_name()
        logging.info("[in_osm]  Name: %s; Checking: %s" % (self.name, short_name))
        payload = self.create_payload()
        r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
        overpass_response = r.json()
        stations = overpass_response.get("elements")
        names = [station["tags"]["name"] for station in stations if "tags" in station and "name" in station["tags"]]
        self.names_in_osm = json.dumps(names)
        matches = 0
        for name in names:
            for short_n in short_name.split("|"):
                if difflib.SequenceMatcher(None, name, short_n).ratio() > 0.6:
                    matches += 1
                    break
        return matches

    def to_dict(self):
        return {
            "lat": self.lat,
            "lon": self.lon,
            "name": self.name,
            "matches": self.matches
        }

    def __repr__(self):
        return '<Stop %r>' % self.name
