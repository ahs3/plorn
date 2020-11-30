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
import lib.asciidoc

def run(fnames):
    for ii in fnames:
        lib.asciidoc.generate(ii)
    return

def usage_line():
    info = "adoc <spec-yaml> ... \t=> generate asciidoc for one or more"
    info += '\n'
    info += "                         \t   specifications in YAML form"
    return info

