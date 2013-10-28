#!/usr/bin/env python3

# create tables
from models import db
db.create_all()

# import data
import routes
routes.get_stops()
