#!/usr/bin/env python3
from models import db
import routes

# create tables
db.create_all()

# import data
routes.get_stops()
