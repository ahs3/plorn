#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import lib.env.config

def run(fnames):
    lib.env.config.dump()
    return

def usage_line():
    return "config                 \t=> list current config variables"

