import os
import unittest

import plorn_album
import plorn_config
import plorn_db
import plorn_name
import plorn_photo
import plorn_place
import plorn_tag


class TestDbTagMethods(unittest.TestCase):

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

    def make_tag(self, tag, parent_id=None):
        return plorn_tag.PlornTag(tag, parent_id)

    def test_add_tag(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_tag("fred")
        tag = db.add_tag(tmp.get_tag())
        self.assertTrue(db.tag_exists(tag.get_tag()))
        plorn_db.close()
        plorn_config.close()

    def test_add_subtag(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_tag("Flintstone")
        parent = db.add_tag(tmp.get_tag())
        self.assertTrue(db.tag_exists(parent.get_tag()))
        p = db.get_tag(parent.get_id())

        tmp = self.make_tag("Fred")
        child = db.add_tag(tmp.get_tag(), p.get_id())
        self.assertTrue(db.tag_exists(child.get_tag(), p.get_id()))
        c = db.get_tag(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        plorn_db.close()
        plorn_config.close()

    def test_get_tag_children(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_tag("Flintstone")
        parent = db.add_tag(tmp.get_tag())
        self.assertTrue(db.tag_exists(parent.get_tag()))
        p = db.get_tag(parent.get_id())

        tmp = self.make_tag("Fred")
        child = db.add_tag(tmp.get_tag(), parent_id=p.get_id())
        self.assertTrue(db.tag_exists(child.get_tag(), p.get_id()))
        c = db.get_tag(child.get_id(), p.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        kids = db.get_tag_children(p.get_id())
        found = False
        for ii in kids:
            if ii.get_tag() == c.get_tag():
                found = True
                break
        self.assertTrue(found)

        plorn_db.close()
        plorn_config.close()

    def test_get_full_tag(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_tag("Flintstone")
        parent = db.add_tag(tmp.get_tag())
        self.assertTrue(db.tag_exists(parent.get_tag()))
        p = db.get_tag(parent.get_id())

        tmp = self.make_tag("Fred")
        child = db.add_tag(tmp.get_tag(), parent_id=parent.get_id())
        self.assertTrue(db.tag_exists(child.get_tag(), parent.get_id()))
        c = db.get_tag(child.get_id(), parent.get_id())

        self.assertTrue(c.get_parent_id(), p.get_id())
        fulltag = db.get_full_tag(c.get_id())
        #print(fulltag)
        self.assertTrue(fulltag == ["Flintstone", "Fred"])
        self.assertTrue(", ".join(fulltag) == "Flintstone, Fred")

        plorn_db.close()
        plorn_config.close()

