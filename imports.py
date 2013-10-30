#! /usr/bin/env python
# -*- coding:utf-8 -*-

from models import Agency, db
import codecs


def create_agency_db():
    """Create the agencies in the database"""
    with codecs.open("data/GTF_VBB_BVG_20110530/agency.txt", mode="r", encoding="utf-8") as infile:
        content = infile.readlines()
    for line in content[1:]:
        fields = line.split(",")
        print(fields[1])
        a = Agency(int(fields[0]), fields[1], fields[2], fields[3])
        db.session.add(a)
    db.session.commit()
    print("Done!")


def get_agency(id):
    this_agency = Agency.query.filter_by(id=id).first()
    print(this_agency)


if __name__ == "__main__":
    #    create_agency_db()
    get_agency(671)
