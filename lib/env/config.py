#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import configparser
import os

defaultrc="/etc/plorn"
userrc="$HOME/.plornrc"

config = configparser.ConfigParser()
config['user'] = { "name" : "",
                   "email" : "",
		   "db" : "",
                 }
config['definitions'] = { "path" : "."
		       }

def readrc():
    global config

    for ii in [defaultrc, userrc]:
        fpath = os.path.expandvars(ii)
        if os.path.exists(fpath):
            with open(fpath, "r") as cfile:
                config.read_file(cfile)

    if config.get("user", "name") == "":
        config.set("user", "name", os.environ['USER'])
    if config.get("user", "email") == "":
        config.set("user", "email", os.environ['USER']+'@localhost')
    if config.get("user", "db") == "":
        config.set("user", "db", 'plorn.db')

    config.set("definitions", "path",
    	os.path.expandvars(config.get("definitions", "path")))

    return

def dump():
    global config

    for ii in config.sections():
        print("[%s]" % (ii))

        for jj in config.options(ii):
            print("\t%s = %s" % (jj, config[ii][jj]))

    return

def get_user():
    global config

    who = [ config.get("user", "name"), config.get("user", "email") ]

    return who

def get_definitions_path():
    global config

    return config.get("definitions", "path")

def get_dbpath():
    global config

    return config.get("user", "db")
