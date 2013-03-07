#!/usr/bin/env python
with open('./data/GTF_VBB_BVG_20110530/shapes.txt', 'r') as f:
    current_id = None
    current_points = []
    for line in f.readlines():
        shape_id, lat, lon, seq = line.split(",")
        if current_id != shape_id:
            #print(current_id)
            s = ['{} {}'.format(lon, lat) for lat, lon in current_points]
            print("LINESTRING(" + ", ".join(s) + ")")
            current_id = shape_id
            current_points = []
            #save to db...
        else:
            current_points.append((lat, lon))

