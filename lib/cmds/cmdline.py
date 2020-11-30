#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import sys

import lib.cmds.add
import lib.cmds.adoc
import lib.cmds.check
import lib.cmds.config
import lib.cmds.dump
import lib.cmds.init
import lib.cmds.list
import lib.cmds.usage
import lib.db
import lib.env.config

__cmd = ''
__args = []


def get():
    global __cmd, __args

    if len(sys.argv) > 1:
        __cmd = sys.argv[1]
    if len(sys.argv) > 2:
        __args = sys.argv[2:]
    return

def print_line():
    global __cmd, __args

    if __cmd == '':
        print("? no command given")
        return

    print("command: %s %s" % (__cmd, " ".join(__args)))

    return

def run():
    get()

    if __cmd == "" or __cmd == "help" or __cmd == "?":
        lib.cmds.usage.usage()

    elif __cmd == "add":
        db = lib.env.config.get_dbpath()
        lib.db.opendb(db)

        if len (__args) > 0:
            lib.cmds.add.run(__args)
        else:
            print("? add command requires a file to be added")

        lib.db.closedb()

    elif __cmd == "adoc":
        db = lib.env.config.get_dbpath()
        lib.db.opendb(db)

        if len (__args) > 0:
            lib.cmds.adoc.run(__args)
        else:
            print("? adoc command requires a file for a spec")

        lib.db.closedb()
    elif __cmd == "check":
        db = lib.env.config.get_dbpath()
        lib.db.opendb(db)

        if len (__args) > 0:
            lib.cmds.check.run(__args)
        else:
            print("? check command requires a file to be checked")

        lib.db.closedb()

    elif __cmd == "dump":
        db = lib.env.config.get_dbpath()
        lib.db.opendb(db)

        if len (__args) > 0:
            lib.cmds.dump.run(__args[0])
        else:
            print("? dump command requires a directory name")

        lib.db.closedb()

    elif __cmd == "list":
        db = lib.env.config.get_dbpath()
        lib.db.opendb(db)

        if len (__args) > 0:
            lib.cmds.list.run(__args)
        else:
            print("? list command requires at least one requirement ID")

        lib.db.closedb()

    elif __cmd == "init":
        db = ''
        if len(__args) > 0:
            db = __args[0]
        else:
            db = lib.env.config.get_dbpath()
        lib.cmds.init.run(db)

    elif __cmd == "config":
        lib.cmds.config.run(__args)

    else:
        print("? no such command: %s" % (__cmd))

    return
