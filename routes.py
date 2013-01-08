#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import simplejson
import re
from flask import Flask, request, g, redirect, url_for, \
        abort, render_template, jsonify, json
from flask_sqlalchemy import SQLAlchemy
import datetime
import os


app = Flask(__name__, instance_relative_config=True)
path_to_db = os.path.expanduser("~/stops.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + path_to_db
db = SQLAlchemy(app)

@app.route("/")
def main():
	Stops = DB_Stop.query.all()
	return render_template("index.html", stops=Stops)

@app.route("/stops/<show_only>/<north>/<east>/<south>/<west>")
def stops_in_bounding_box(show_only, north, east, south, west):
	if show_only=="problemsonly":
		result = DB_Stop.query.filter(
			DB_Stop.lat.between(float(south),float(north)),
			DB_Stop.lon.between(float(west), float(east)),
			DB_Stop.matches==0
		).all()
	elif show_only=="matchesonly":
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

	return render_template("index.html", stops=result)

@app.route("/recheck/<id>")
def recheck(id):
	stop = DB_Stop.query.filter_by(id=id).first()
	stop.matches = VBB_Stop(stop.to_vbb_syntax()).is_in_osm()
	stop.last_run = datetime.datetime.now().replace(microsecond=0);
	db.session.commit()	
	return redirect(url_for("main"))

@app.route("/nomatch_all")
def nomatch_all():
	Stops = DB_Stop.query.filter(DB_Stop.matches < 1).all()
	all_stops = []
	for Stop in Stops:
		all_stops.append({"lat": Stop.lat, "lon": Stop.lon, "name": Stop.name})
	return jsonify(stops=all_stops)

@app.route("/map_of_the_bad")
def map_of_the_bad():
	return render_template("map.html")

def get_trains():
	req = requests.get("http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/routes.txt")
	text = req.text.split("\n")
	all_bvg_lines = []
	for line in text:
		Train = Bvg_line(line)
		if Train.operator in ["BVG", "DB"]:
			print Train.line_number + " ist ein(e) " + Train.transit_type
			all_bvg_lines.append(Train.line_number)
	return all_bvg_lines

def get_stops():
	req = requests.get("http://datenfragen.de/openvbb/GTFS_VBB_Okt2012/stops.txt")
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

class DB_Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_run = db.Column(db.DateTime)
    name = db.Column(db.String(200), index=True)
    matches = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def __init__(self, vbb_id, name, lat, lon, matches):
	self.id = vbb_id
        self.name = name
        self.lat = lat
        self.lon = lon
	self.matches = int(matches)
        self.last_run = datetime.datetime.now().replace(microsecond=0)
	
    def to_vbb_syntax(self):
	return '%i,,"%s",,%f,%f'%(self.id, self.name, self.lat, self.lon)    

    def __repr__(self):
        return '<Stop %r>' % self.name


class VBB_Stop():
	def __init__(self, line_from_stops_txt):
		#since csvreader doesnt understand unicode we'll just use good old regex
		pattern = re.compile('(\d*),,"(.*)",,(\d*\.\d*),(\d*\.\d*)')
		fields = re.findall(pattern, line_from_stops_txt)[0]
		self.stop_id = fields[0]
		self.name = fields[1]
		self.lat = float(fields[2])
		self.lon = float(fields[3])

	def is_in_osm(self):
		north = self.lat - 0.002 
		east =  self.lon - 0.002
		south = self.lat + 0.002
		west =  self.lon + 0.002
		short_name = self.name
		if "(" in self.name:
			short_name = short_name.split(" (")[0]
		if "/" in self.name:
			short_name = short_name.split("/")[1] # if we have something like StreetA/StreetB overpass is not able to find this
							      # we can just look for StreetB though since we are limiting the search on a small ara
       		payload = {"data":'[output:json];node(%f, %f, %f, %f)["name"~"%s"];out skel;'%(north, east, south, west, short_name)}
		r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
		json = simplejson.loads(r.text)
		stations = json.get("elements")
		return len(stations)

class Bvg_line():
	def __init__(self, line_from_routes_txt):
		fields = line_from_routes_txt.split(",")
		self.bvg_id = fields[0]
		self.agency = fields[1][:3]
		self.line_number = fields[2]
		#operator
		if self.agency.startswith("BV"):
			self.operator = "BVG"
		elif self.agency.startswith("DB"):
			self.operator = "DB"
		else:
			self.operator = "other"
		#transit_type (Bus/tram/etc.)
		if self.agency.endswith("T"):
			self.transit_type = "Tram"
		elif self.agency.endswith("S"):
			self.transit_type = "S-Bahn"
		elif self.agency.endswith("B"):
			self.transit_type = "Bus"
		elif self.agency.endswith("F"):
			self.transit_type = "Faehre"
		else:
			self.transit_type = self.agency
	def is_in_osm():
		payload = {"data":'[output:json];relation["network"="VBB"]["ref"="%s"];out;'%line_name}	
		r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
		if "tags" in r.text:
			return r.text.split('"name": "')[1].split('"')[0]
		else:
			return False
		
def print_success(message):
        print '\033[1;32m%s\033[1;m'%(message)

def print_failure(message):
        print '\033[1;31m%s\033[1;m'%(message)

if __name__=="__main__":
	app.debug = True
	app.run()
