#!/usr/bin/env python

# create tables
from routes import db
db.create_all()

# import data
import routes
routes.get_stops()
