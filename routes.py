#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from flask import redirect, url_for, \
    render_template, jsonify, request, \
    send_from_directory
import datetime
import logging
import sys
import csv
from math import log10

from models import Stop, DB_Train, Bvg_line, app, db
from helpers import print_success, print_failure


logging.basicConfig(filename="rechecks.log",
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    level=logging.INFO)
if "--verbose" in sys.argv:
    console = logging.StreamHandler(sys.stdout)
    logging.getLogger('').addHandler(console)


@app.route("/")
def main():
    ''' The main page '''
    return pagination(1)


@app.route("/city/<city>/page/<number>")
def pagination(number, city="Berlin"):
    """ Render only 100 stops for better overview"""
    number = int(number)
    start = (number - 1) * 50
    end = number * 50
    q = Stop.query\
        .filter(Stop.landkreis == city)\
        .order_by("last_run desc").all()
    Stops = q[start:end]
    all_stops = len(q)
    matches = len([stop for stop in q if stop.matches > 0])
    landkreise = list(set([stop.landkreis for stop in
                           Stop.query.all()]))
    landkreise.sort()

    for stop in Stops:
        stop.turbo_url = stop.turbo_url

    return render_template("index.html",
                           city=city,
                           stops=Stops,
                           pages=all_stops,
                           this_page=number,
                           matches_count=matches,
                           landkreise=landkreise
                           )


@app.route("/search/<query>")
def search(query):
    """ Return a list with all the stops that match the query"""
    Stops = Stop.query.filter(Stop.name.like("%" + query + "%")).all()

    for stop in Stops:
        stop.turbo_url = stop.turbo_url

    return render_template("index.html", stops=Stops, pages=False)


@app.route("/stops/<show_only>/<north>/<east>/<south>/<west>")
def stops_in_bounding_box(show_only, north, east, south, west):
    ''' Only show stops within a given bounding box. Allow filtering by
    matches/nomatches'''
    if show_only == "problemsonly":
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
            Stop.matches == 0
        ).all()

    elif show_only == "matchesonly":
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
            Stop.matches > 0
        ).all()
    else:
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
        ).all()

    landkreise = list(set([stop.landkreis for stop in
                           Stop.query.all()]))
    landkreise.sort()
    return render_template("index.html",
                           stops=result,
                           landkreise=landkreise
                           )


@app.route("/api/jsonstops/<show_only>/<north>/<east>/<south>/<west>")
def json_stops(show_only, north, east, south, west):
    ''' Only show stops within a given bounding box. Allow filtering by
    matches/nomatches'''
    if show_only == "problemsonly":
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
            Stop.matches == 0
        ).all()

    elif show_only == "matchesonly":
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
            Stop.matches > 0
        ).all()
    else:
        result = Stop.query.filter(
            Stop.lat.between(float(south), float(north)),
            Stop.lon.between(float(west), float(east)),
        ).all()

    if len(result) > 200:
        return jsonify(stops="Too many")

    all_stops = [stop.to_dict() for stop in result]

    return jsonify(stops=all_stops)


@app.route("/recheck/<id>")
def recheck(id, from_cm_line=False):
    ''' Rerun the checks for a stop and update the db'''
    stop = Stop.query.filter_by(id=id).first()
    old_matches = stop.matches
    stop.matches = stop.is_in_osm()
    stop.last_run = datetime.datetime.now().replace(microsecond=0)
    db.session.commit()
    if not from_cm_line:
        logging.info("[recheck] Name: %-5s; Old: %-3i; New: %-3i; IP: %-3s" % (stop.name,
                                                                               old_matches,
                                                                               stop.matches,
                                                                               request.remote_addr))
        return redirect(url_for("pagination", number=1, city=stop.landkreis))
    else:
        if stop.matches > 0:
            print_success("%s now matches %i stops" % (stop.name,
                                                       stop.matches))
        else:
            print_failure("%s does not match any stops..." % (stop.name))
        return stop.matches


@app.route("/map_of_the_bad")
def map_of_the_bad():
    ''' Return a map with all the stops that aren't in OSM '''
    return render_template("map.html")


@app.route("/api/stops")
def api_stops():
    if request.args.get("matchesOnly"):
        Stops = Stop.query.filter(Stop.matches >= 1).all()
    elif request.args.get("noMatchesOnly"):
        Stops = Stop.query.filter(Stop.matches < 1).all()
    else:
        Stops = Stop.query.all()

    all_stops = []
    for stop in Stops:
        all_stops.append(stop.to_dict())
    return jsonify(stops=all_stops)


@app.route('/robots.txt')
def serve_static():
    return send_from_directory(app.static_folder, request.path[1:])


def get_trains():
    ''' The initial query to set up the train db '''
    url = "http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/routes.txt"
    req = requests.get(url)
    text = req.text.split("\n")
    for line in text:
        Train = Bvg_line(line)
        if Train.operator in ["BVG", "DB"]:
            feedback = Train.is_in_osm()
            if feedback:
                print_success(feedback)
            else:
                print_failure(Train.line_number + " is not in OSM")
            db_rep = DB_Train()
            db.session.add(db_rep)
            db.session.commit()


def recheck_batch(Stops):
    total = 0
    number_of_stops = len(Stops)
    # get the number of digits we want to show
    digits = int(log10(number_of_stops)) + 1
    counter = 0
    for Stop in Stops:
        counter += 1
        print("%*i/%*i " % (digits, counter, digits, number_of_stops))
        out = recheck(Stop.id, from_cm_line=True)
        if out > 0:
            total += 1
    print_success("Insgesamt %i neue Treffer" % total)


def recheck_all_missings_stops():
    Stops = Stop.query.filter(Stop.matches < 1).all()
    recheck_batch(Stops)


def recheck_by_name(name):
    Stops = Stop.query.filter(Stop.name.like("%" + name + "%"),
                              Stop.matches < 1).all()
    recheck_batch(Stops)


def recheck_all():
    Stops = Stop.query.all()
    recheck_batch(Stops)


def get_stops():
    ''' The initial query to set up the stop db '''
    all_stops = Stop.query.all()
    all_ids = [stop.id for stop in all_stops]
    url = "http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/stops.txt"
    req = requests.get(url)
    req.encoding = 'utf-8'
    text = req.text.split('\n')
    reader = csv.DictReader(text, delimiter=',', quotechar='"')
    for line in reader:
        stop = Stop(line)
        if stop.id not in all_ids:
            stop.matches = stop.is_in_osm()
            if stop.matches > 0:
                print_success(stop.name + ": " + str(stop.matches))
            else:
                print_failure(stop.name + ":  0")
            stop.last_run = datetime.datetime.now().replace(microsecond=0)
            db.session.add(stop)
            db.session.commit()


if __name__ == "__main__":
    app.debug = True
    app.run()
