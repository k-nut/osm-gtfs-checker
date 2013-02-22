#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from helpers import print_success, print_failure, print_info


def main():
    if len(sys.argv) < 2:
        print "You need to pass the path to the logfile" + \
              " e.g logviewer.py recheckes.log"
        return False
    path = sys.argv[1]
    logview(path)


def logview(logfile):
    with open(logfile, "r") as infile:
        t = infile.readlines()
    for line in t:
        if "root" in line:
            line = line.replace("\n", "")
            if "in_osm" in line:
                print_info(line)
            elif "recheck" in line:
                parts = line.split("[recheck]")[1].split(";")
                old = int(parts[1].split(":")[1])
                new = int(parts[2].split(":")[1])
                if new > old:
                    print_success(line)
                else:
                    print_failure(line)

if __name__ == "__main__":
    main()
