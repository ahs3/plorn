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

import lib.db
import lib.reqts

def run(fnames):
    for ii in fnames:
        if not os.path.exists(ii):
            print("? no file called \"%s\", ignoring" % ii)
        else:
            # print("> adding %s" % ii)
            lib.reqts.add(ii)

    return

def usage_line():
    return "add <file> ...      \t=> add requirements to the data base"

