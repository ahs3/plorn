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
import sys

import lib.db
import lib.reqts

def run(reqts):
    for ii in reqts:
        lib.db.list_reqt(ii)
    return

def usage_line():
    info = "list <reqt-id> ... \t=> dump one or more requirements in YAML"
    info += '\n'
    info += "                         \t   form to stdout"
    return info

