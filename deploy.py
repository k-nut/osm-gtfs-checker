#!/usr/bin/env python

# create tables
from models import db
db.create_all()

# import data
import routes
routes.get_stops()
