#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

__progname = "plorn"
__version = "0.3.1"

def print_version():
    print("%s, v%s" % (__progname, __version))
    return

def full_program():
    return "%s, v%s" % (__progname, __version)

def program():
    return __progname

