import os
import unittest

import plorn_album
import plorn_config
import plorn_db
import plorn_name
import plorn_photo
import plorn_place


class TestDbNameMethods(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            "[plorn]",
            "user = fred",
            "full_name = Fred Flintstone",
            "config_dir = /tmp/barney",
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
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        plorn_db.close()

    def tearDown(self):
        plorn_db.close()
        plorn_config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def make_name(self, name, parent_id=None):
        return plorn_name.PlornName(name, parent_id)

    def test_add_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_name("fred")
        name = db.add_name(tmp.get_name())
        self.assertTrue(db.name_exists(name.get_name()))
        plorn_db.close()
        plorn_config.close()

    def test_add_subname(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_name("Flintstone")
        parent = db.add_name(tmp.get_name())
        self.assertTrue(db.name_exists(parent.get_name()))
        p = db.get_name(parent.get_id())

        tmp = self.make_name("Fred")
        child = db.add_name(tmp.get_name(), p.get_id())
        self.assertTrue(db.name_exists(child.get_name(), p.get_id()))
        c = db.get_name(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        plorn_db.close()
        plorn_config.close()

    def test_get_name_children(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_name("Flintstone")
        parent = db.add_name(tmp.get_name())
        self.assertTrue(db.name_exists(parent.get_name()))
        p = db.get_name(parent.get_id())

        tmp = self.make_name("Fred")
        child = db.add_name(tmp.get_name(), parent_id=p.get_id())
        self.assertTrue(db.name_exists(child.get_name(), p.get_id()))
        c = db.get_name(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        kids = db.get_name_children(p.get_id())
        found = False
        for ii in kids:
            if ii.get_name() == c.get_name():
                found = True
                break
        self.assertTrue(found)

        plorn_db.close()
        plorn_config.close()

    def test_get_full_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_name("Flintstone")
        parent = db.add_name(tmp.get_name())
        self.assertTrue(db.name_exists(parent.get_name()))
        p = db.get_name(parent.get_id())

        tmp = self.make_name("Fred")
        child = db.add_name(tmp.get_name(), parent_id=parent.get_id())
        self.assertTrue(db.name_exists(child.get_name(), parent.get_id()))
        c = db.get_name(child.get_id(), parent.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        fullname = db.get_full_name(c.get_id())
        #print(fullname)
        self.assertTrue(fullname == ["Flintstone", "Fred"])
        self.assertTrue(", ".join(fullname) == "Flintstone, Fred")

        plorn_db.close()
        plorn_config.close()


class TestDbPlaceMethods(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            "[plorn]",
            "user = fred",
            "full_name = Fred Flintstone",
            "config_dir = /tmp/barney",
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
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        plorn_db.close()

    def tearDown(self):
        plorn_db.close()
        plorn_config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def make_place(self, place, parent_id=None):
        return plorn_place.PlornPlace(place, parent_id)

    def test_add_place(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        place = self.make_place("Bedrock")
        id = db.add_place(place.get_place())
        self.assertTrue(db.place_exists(place.get_place()))
        plorn_db.close()
        plorn_config.close()

    def test_add_subplace(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_place("Stone Age")
        parent = db.add_place(tmp.get_place())
        self.assertTrue(db.place_exists(parent.get_place()))
        p = db.get_place(parent.get_id())

        tmp = self.make_place("Bedrock")
        child = db.add_place(tmp.get_place(), p.get_id())
        self.assertTrue(db.place_exists(child.get_place(), p.get_id()))
        c = db.get_place(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        plorn_db.close()
        plorn_config.close()

    def test_get_place_children(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_place("Stone Age")
        parent = db.add_place(tmp.get_place())
        self.assertTrue(db.place_exists(parent.get_place()))
        p = db.get_place(parent.get_id())

        tmp = self.make_place("Bedrock")
        child = db.add_place(tmp.get_place(), parent_id=p.get_id())
        self.assertTrue(db.place_exists(child.get_place(), p.get_id()))
        c = db.get_place(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        kids = db.get_place_children(p.get_id())
        found = False
        for ii in kids:
            if ii.get_place() == c.get_place():
                found = True
                break
        self.assertTrue(found)

        plorn_db.close()
        plorn_config.close()

    def test_get_full_place(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_place("Stone Age")
        parent = db.add_place(tmp.get_place())
        self.assertTrue(db.place_exists(parent.get_place()))
        p = db.get_place(parent.get_id())

        tmp = self.make_place("Bedrock")
        child = db.add_place(tmp.get_place(), parent_id=p.get_id())
        self.assertTrue(db.place_exists(child.get_place(), p.get_id()))
        c = db.get_place(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        fullplace = db.get_full_place(c.get_id(), p.get_id())
        self.assertTrue(fullplace == ["Stone Age", "Bedrock"])
        self.assertTrue(", ".join(fullplace) == "Stone Age, Bedrock")

        plorn_db.close()
        plorn_config.close()
