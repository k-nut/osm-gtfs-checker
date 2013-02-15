#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import requests
from flask import redirect, url_for, \
    render_template, jsonify, request
import datetime
import logging

from models import DB_Stop, DB_Train, VBB_Stop, Bvg_line, app, db
from helpers import print_success, print_failure


@app.route("/")
def main():
    ''' The main page '''
    return pagination(1)


@app.route("/city/<city>/page/<number>")
def pagination(number, city="Berlin"):
    """ Render only 100 stops for better overview"""
    number = int(number)
    start = (number-1)*50
    stop = number * 50
    matches = DB_Stop.query.filter(
        DB_Stop.landkreis == city,
        DB_Stop.matches > 0
    ).count()
    all_stops = DB_Stop.query.filter(DB_Stop.landkreis == city).count()
    Stops = DB_Stop.query \
        .filter(DB_Stop.landkreis == city) \
        .order_by("last_run desc") \
        .slice(start, stop)
    landkreise = list(set([stop.landkreis for stop in
                           DB_Stop.query.all()]))
    landkreise.sort()
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
    Stops = DB_Stop.query.filter(DB_Stop.name.like("%" + query + "%")).all()
    return render_template("index.html", stops=Stops, pages=False)


@app.route("/stops/<show_only>/<north>/<east>/<south>/<west>")
def stops_in_bounding_box(show_only, north, east, south, west):
    ''' Only show stops within a given bounding box. Allow filtering by
    matches/nomatches'''
    if show_only == "problemsonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches == 0
        ).all()

    elif show_only == "matchesonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches > 0
        ).all()
    else:
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
        ).all()

    return render_template("index.html", stops=result)


@app.route("/api/jsonstops/<show_only>/<north>/<east>/<south>/<west>")
def json_stops(show_only, north, east, south, west):
    ''' Only show stops within a given bounding box. Allow filtering by
    matches/nomatches'''
    if show_only == "problemsonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches == 0
        ).all()

    elif show_only == "matchesonly":
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
            DB_Stop.matches > 0
        ).all()
    else:
        result = DB_Stop.query.filter(
            DB_Stop.lat.between(float(south), float(north)),
            DB_Stop.lon.between(float(west), float(east)),
        ).all()

    all_stops = []
    for stop in result:
        all_stops.append(stop.to_dict())
    if len(all_stops) > 100:
        return jsonify(stops="Too many")
    return jsonify(stops=all_stops)


@app.route("/recheck/<id>")
def recheck(id, from_cm_line=False):
    ''' Rerun the checks for a stop and update the db'''
    stop = DB_Stop.query.filter_by(id=id).first()
    stop.matches = VBB_Stop(stop.to_vbb_syntax()).is_in_osm()
    stop.last_run = datetime.datetime.now().replace(microsecond=0)
    db.session.commit()
    if not from_cm_line:
        logging.basicConfig(filename="rechecks.log", level=logging.INFO)
        logging.info("%s: %s" % (stop.name, stop.matches))
        return redirect(url_for("pagination", number=1, city=stop.landkreis))
    else:
        if stop.matches > 0:
            print_success("%s now matches %i stops" % (stop.name,
                                                       stop.matches))
        else:
            print_failure("%s does not match any stops..." % (stop.name))
        return True


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


def recheck_all_missings_stops():
    Stops = DB_Stop.query.filter(DB_Stop.matches < 1).all()
    for Stop in Stops:
        recheck(Stop.id, from_cm_line=True)


def recheck_all():
    Stops = DB_Stop.query.all()
    for Stop in Stops:
        recheck(Stop.id, from_cm_line=True)


def get_stops():
    ''' The initial query to set up the stop db '''
    all_stops = DB_Stop.query.all()
    all_ids = [stop.id for stop in all_stops]
    url = "http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/stops.txt"
    req = requests.get(url)
    text = req.text.split("\n")[1:]
    for line in text[35:]:  # start in line 35 to exlclude stops in Poland
        if len(line) > 1:
            Stop = VBB_Stop(line)
            if Stop.stop_id not in all_ids:
                feedback = Stop.is_in_osm()
                if feedback > 0:
                    print_success(Stop.name + ": " + str(feedback))
                else:
                    print_failure(Stop.name + ":  0")
                new_stop = DB_Stop(
                    name=Stop.name,
                    lat=Stop.lat,
                    lon=Stop.lon,
                    matches=feedback,
                    vbb_id=Stop.stop_id
                )
                db.session.add(new_stop)
                db.session.commit()


if __name__ == "__main__":
    app.debug = True
    app.run()
