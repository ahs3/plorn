#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import os
import os.path
import sys

import lib.db
import lib.reqts

def run(dirname):
    # print("> dump db to %s" % dirname)
    if os.path.exists(dirname):
        if not os.path.isdir(dirname):
            print("? %s is not a directory" % dirname)
            sys.exit(1)
    else:
        os.makedirs(dirname)

    lib.reqts.dump(dirname)

    return

def usage_line():
    info = "dump <directory> ... \t=> dump requirements in YAML form"
    info += '\n'
    info += "                         \t   to a directory"
    return info

