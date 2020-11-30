#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import lib.env
import lib.cmds

def usage():
    print
    lib.env.print_version()

    print("usage: %s <command> [ <argument> ...]" % (lib.env.program()))
    print("where <command> can be:")

    print("\t%s" % (lib.cmds.add.usage_line()))     # "add" command
    print("\t%s" % (lib.cmds.adoc.usage_line()))    # "adoc" command
    print("\t%s" % (lib.cmds.check.usage_line()))   # "check" command
    print("\t%s" % (lib.cmds.config.usage_line()))  # "config" command
    print("\t%s" % (lib.cmds.dump.usage_line()))    # "dump" command
    print("\t%s" % (lib.cmds.usage.usage_line()))   # "help" command
    print("\t%s" % (lib.cmds.init.usage_line()))    # "init" command
    print("\t%s" % (lib.cmds.list.usage_line()))    # "list" command

    return

def usage_line():
    return "help\t\t\t=> return this info"

