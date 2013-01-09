#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from flask import Flask, redirect, url_for, \
        render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

import config

from models import DB_Stop, VBB_Stop, Bvg_line, app, db

@app.route("/")
def main():
    ''' The main page '''
    Stops = DB_Stop.query.all()
    return render_template("index.html", stops=Stops)

@app.route("/stops/<show_only>/<north>/<east>/<south>/<west>")
def stops_in_bounding_box(show_only, north, east, south, west):
    ''' Only show stops within a given bounding box. Allow filtering by
    matches/nomatches'''
    if show_only == "problemsonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south),float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches==0
            ).all()

    elif show_only == "matchesonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south),float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches>0
            ).all()
    else:
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south),float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            ).all()

    return render_template("index.html", stops = result)

@app.route("/recheck/<id>")
def recheck(id):
    ''' Rerun the checks for a stop and update the db'''
    stop = DB_Stop.query.filter_by(id=id).first()
    stop.matches = VBB_Stop(stop.to_vbb_syntax()).is_in_osm()
    stop.last_run = datetime.datetime.now().replace(microsecond=0)
    db.session.commit()
    return redirect(url_for("main"))

@app.route("/nomatch_all")
def nomatch_all():
    ''' Return a json file of all stops that are not in OSM '''
    Stops = DB_Stop.query.filter(DB_Stop.matches < 1).all()
    all_stops = []
    for stop in Stops:
        all_stops.append(stop.to_dict())
    return jsonify(stops=all_stops)

@app.route("/map_of_the_bad")
def map_of_the_bad():
    ''' Return a map with all the stops that aren't in OSM '''
    return render_template("map.html")

@app.route("/api/stops")
def api_stops():

    if request.args.get("matchesOnly"):
        Stops = DB_Stop.query.filter(DB_Stop.matches >= 1).all()
    elif request.args.get("noMatchesOnly"):
        Stops = DB_Stop.query.filter(DB_Stop.matches < 1).all()
    else:
        Stops = DB_Stop.query.all()

    all_stops = []
    for stop in Stops:
        all_stops.append(stop.to_dict())
    return jsonify(stops=all_stops)

def get_trains():
    ''' The initial query to set up the train db '''
    url = "http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/routes.txt"
    req = requests.get(url)
    text = req.text.split("\n")
    all_bvg_lines = []
    for line in text:
        Train = Bvg_line(line)
        if Train.operator in ["BVG", "DB"]:
            print Train.line_number + " ist ein(e) " + Train.transit_type
            all_bvg_lines.append(Train.line_number)
    return all_bvg_lines

def get_stops():
    ''' The initial query to set up the stop db '''
    url = "http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/stops.txt"
    req = requests.get(url)
    text = req.text.split("\n")[1:]
    for line in text:
        if len(line) > 1:
            Stop = VBB_Stop(line)
            if "(Berlin)" in Stop.name:
                feedback = Stop.is_in_osm()
                if feedback > 0:
                    print_success(Stop.name + ": " + str(feedback))
                else:
                    print_failure(Stop.name + ":  0")
                    new_stop = DB_Stop(
                            name = Stop.name,
                            lat = Stop.lat,
                            lon = Stop.lon,
                            matches = feedback,
                            vbb_id = Stop.stop_id
                            )
                    db.session.add(new_stop)
                    db.session.commit()


def print_success(message):
    ''' Print the message in green '''
    print '\033[1;32m%s\033[1;m'% (message)

def print_failure(message):
    ''' Print the message in red '''
    print '\033[1;31m%s\033[1;m'% (message)

if __name__ == "__main__":
    app.debug = True
    app.run()
