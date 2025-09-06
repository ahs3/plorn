import getpass
import os
import pwd
import unittest

import plorn_config

class TestConfigMethods(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            "[plorn]",
            "user = fred",
            "full_name = Fred Flintstone",
            "config_dir = /tmp/barney",
            "data_dir = /tmp/wilma",
            "dbname = dino.db",
        ]
        with open(name, "w") as cfg:
            for ii in data:
                cfg.write(ii + "\n")
        cfg.close()

    def setUp(self):
        cfg_file = os.path.expanduser("~/.config/plorn/.bogus_test.cfg")
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        db_file = os.path.expanduser("~/.local/share/plorn/.bogus_test.db")
        if os.path.exists(db_file):
            os.remove(db_file)

        cfg_file = "completely_bogus_test.cfg"
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        db_file = "/tmp/wilma/dino.db"
        if os.path.exists(db_file):
            os.remove(db_file)
        self.write_test_config(cfg_file)

    def tearDown(self):
        cfg_file = os.path.expanduser("~/.config/plorn/.bogus_test.cfg")
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        db_file = os.path.expanduser("~/.local/share/plorn/.bogus_test.db")
        if os.path.exists(db_file):
            os.remove(db_file)

        cfg_file = "completely_bogus_test.cfg"
        if os.path.exists(cfg_file):
            os.remove(cfg_file)
        db_file = "/tmp/wilma/dino.db"
        if os.path.exists(db_file):
            os.remove(db_file)

    def test_open_new(self):
        """
        Assume defaults for most things
        """
        plorn_config.close()
        cfg = plorn_config.get_config(".bogus_test.cfg")
        user = getpass.getuser()
        self.assertEqual(cfg.get_username(), user)
        fullname = pwd.getpwnam(user).pw_gecos
        self.assertEqual(cfg.get_fullname(), fullname)
        cfg_dir = os.path.expanduser("~/.config/plorn")
        self.assertEqual(cfg.get_configdir(), cfg_dir)
        data_dir = os.path.expanduser("~/.local/share/plorn")
        self.assertEqual(cfg.get_datadir(), data_dir)
        dbname = ".bogus_test.db"
        self.assertEqual(cfg.get_dbname(), dbname)
        self.assertTrue(cfg.get_version() != "")
        self.assertTrue(cfg.needs_db() == True)

    def test_open_existing(self):
        """
        Try a completely made up config file

        NB: if a config file exists, we assume a db has been made.
        """
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        self.assertEqual(cfg.get_filename(), cfg_file)
        self.assertEqual(cfg.get_username(), "fred")
        self.assertEqual(cfg.get_fullname(), "Fred Flintstone")
        self.assertEqual(cfg.get_configdir(), "/tmp/barney")
        self.assertEqual(cfg.get_datadir(), "/tmp/wilma")
        self.assertEqual(cfg.get_dbname(), "dino.db")
        self.assertTrue(cfg.get_version() != "")
        self.assertTrue(cfg.needs_db() == False)

    def test_set_user(self):
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        cfg.set_username("blimpy")
        self.assertEqual(cfg.get_username(), "blimpy")

    def test_set_fullname(self):
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        cfg.set_fullname("blimpy")
        self.assertEqual(cfg.get_fullname(), "blimpy")

    def test_set_configdir(self):
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        cfg.set_configdir("blimpy")
        self.assertEqual(cfg.get_configdir(), "blimpy")

    def test_set_datadir(self):
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        cfg.set_datadir("blimpy")
        self.assertEqual(cfg.get_datadir(), "blimpy")

    def test_set_dbname(self):
        plorn_config.close()
        cfg_file = "completely_bogus_test.cfg"
        cfg = plorn_config.get_config(cfg_file)
        cfg.set_dbname("blimpy")
        self.assertEqual(cfg.get_dbname(), "blimpy")

