
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os
import shutil
import sys
import unittest

import plorn.album
import plorn.config
import plorn.db
import plorn.photo

class TestDbBasics(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            "[plorn]",
            "user = fred",
            "full_name = Fred Flintstone",
            "config_dir = /tmp/plorn_barney",
            f"data_dir = {os.path.expanduser('~/.local/share/plorn')}",
            "dbname = completely_bogus.db",
        ]
        with open(name, "w") as cfg:
            for ii in data:
                cfg.write(ii + "\n")
        cfg.close()

    def get_test_dbname(self):
        dbpath = os.path.expanduser("~/.local/share/plorn")
        return os.path.join(dbpath, "completely_bogus.db")

    def get_test_cfgname(self):
        path = os.path.expanduser("~/.config/plorn")
        return os.path.join(path, "completely_bogus.cfg")

    def setUp(self):
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)
        self.write_test_config(self.get_test_cfgname())

    def tearDown(self):
        plorn.db.close()
        plorn.config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def test_open(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        self.assertTrue(db != None)
        plorn.db.close()
        plorn.config.close()

    def test_multiple_opens(self):
        db1 = plorn.db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        db2 = plorn.db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        self.assertTrue(db1 == db2)
        db1.close()
        db2.close()
        plorn.db.close()
        plorn.config.close()

    def test_config_table(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        row = db.get_config()
        self.assertEqual(row["name"], "plorn")
        self.assertEqual(row["username"], "fred")
        self.assertEqual(row["fullname"], "Fred Flintstone")
        dbfile = os.path.join(row["datadir"], self.get_test_dbname())
        datadir = os.path.expanduser("~/.local/share/plorn")
        self.assertEqual(row["datadir"], datadir)
        plorn.db.close()
        plorn.config.close()

