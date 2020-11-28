#!/usr/bin/env python3
#======================================================================
#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2106, Al Stone <ahs3@redhat.com>
#
#======================================================================
#

import os
import sqlite3
import sys

import lib.db

def run(dbname):
    if os.path.exists(dbname):
        print("? data base \"%s\" already exists, exiting" % dbname)
        sys.exit(1)

    lib.db.init(dbname)

    return

def usage_line():
    return "init [<filename>] \t=> initialize requirements data base"

