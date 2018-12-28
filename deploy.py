#!/usr/bin/env python3
from models import db
import app

# create tables
db.create_all()

# import data
app.get_stops()
