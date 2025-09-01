import os
import unittest

import plorn_album
import plorn_config
import plorn_db
import plorn_photo

class TestDbBasics(unittest.TestCase):

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

    def tearDown(self):
        plorn_db.close()
        plorn_config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def test_open(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        self.assertTrue(db != None)
        plorn_db.close()

    def test_multiple_opens(self):
        db1 = plorn_db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        db2 = plorn_db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        self.assertTrue(db1 == db2)
        db1.close()
        db2.close()
        plorn_db.close()

    def test_config_table(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        row = db.get_config()
        self.assertEqual(row["name"], "plorn")
        self.assertEqual(row["username"], "fred")
        self.assertEqual(row["fullname"], "Fred Flintstone")
        dbfile = os.path.join(row["datadir"], self.get_test_dbname())
        datadir = os.path.expanduser("~/.local/share/plorn")
        self.assertEqual(row["datadir"], datadir)
        plorn_db.close()
        plorn_config.close()


class TestDbAlbumMethods(unittest.TestCase):

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

    def make_album(self, name, path, id, dated, notes, nphotos):
        return plorn_album.PlornAlbum(name, path, id, dated, notes, nphotos)

    def test_album_exists(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "1")
        id = db.add_album(album)
        self.assertTrue(db.album_exists(album))
        plorn_db.close()
        plorn_config.close()

    def test_last_album_id(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album1 = self.make_album("fred", "barney", None, "now", "note1", "1")
        album2 = self.make_album("barney", "barney", None, "now", "note2", "2")
        id1 = db.add_album(album1)
        id2 = db.add_album(album2)
        lastid = db.get_last_album_id()
        self.assertEqual(id2, lastid)
        album3 = self.make_album("dino", "barney", None, "now", "note2", "2")
        id3 = db.add_album(album3)
        lastid = db.get_last_album_id()
        self.assertEqual(id3, lastid)
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "42")
        id = db.add_album(album)
        row = db.get_album_by_name("fred")

        self.assertEqual(row["id"], id)
        self.assertEqual(row["name"], "fred")
        self.assertEqual(row["path"], "barney")
        self.assertEqual(row["dated"], "now")
        self.assertEqual(row["notes"], "note1")
        self.assertEqual(row["photo_count"], 42)
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_id(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "42")
        id = db.add_album(album)
        row = db.get_album_by_id(id)

        self.assertEqual(row["id"], id)
        self.assertEqual(row["name"], "fred")
        self.assertEqual(row["path"], "barney")
        self.assertEqual(row["dated"], "now")
        self.assertEqual(row["notes"], "note1")
        self.assertEqual(row["photo_count"], 42)
        plorn_db.close()
        plorn_config.close()

    def test_remove_by_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "1")
        id = db.add_album(album)
        self.assertTrue(db.album_exists(album))
        db.remove_album_by_name("fred")
        self.assertFalse(db.album_exists(album))
        plorn_db.close()
        plorn_config.close()

    def test_get_albums(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album1 = self.make_album("fred", "barney", None, "now", "note1", "1")
        album2 = self.make_album("barney", "barney", None, "now", "note2", "2")
        id1 = db.add_album(album1)
        id2 = db.add_album(album2)
        rows = db.get_albums()
        self.assertEqual(len(rows), 2)
        row = rows[1]
        self.assertEqual(row["id"], id2)
        self.assertEqual(row["name"], "barney")
        self.assertEqual(row["path"], "barney")
        plorn_db.close()
        plorn_config.close()

    def test_album_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album1 = self.make_album("fred", "barney", None, "now", "note1", "1")
        album2 = self.make_album("barney", "barney", None, "now", "note2", "2")
        id1 = db.add_album(album1)
        id2 = db.add_album(album2)
        rows = db.get_albums()
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows), db.album_count())
        plorn_db.close()
        plorn_config.close()

    def test_update_album(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "1")
        album_id = db.add_album(album)
        album2 = album
        album2.set_path("wilma")
        album2.set_notes("lots of notes")
        album2.set_photo_count(12)
        new_id = db.update_album(album, album2)
        self.assertEqual(album_id, new_id)
        row = db.get_album_by_id(album_id)
        self.assertEqual(row["path"], "wilma")
        self.assertEqual(row["notes"], "lots of notes")
        self.assertEqual(row["photo_count"], 12)
        plorn_db.close()
        plorn_config.close()

class TestDbPhotoMethods(unittest.TestCase):

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

    def make_album(self, name, path, id, dated, notes, nphotos):
        return plorn_album.PlornAlbum(name, path, id, dated, notes, nphotos)

    def setUp(self):
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

        self.write_test_config(self.get_test_cfgname())
        cfg = plorn_config.get_config(self.get_test_cfgname())
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "0")
        album_id = db.add_album(album)
        plorn_db.close()
        plorn_config.close()

    def tearDown(self):
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def make_photo(self, name, path, photo_id, album_id,
                   dated, notes):
        return plorn_photo.PlornPhoto(name, path, photo_id, album_id,
                                      dated, notes)

    def test_get_photos(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album_row = db.get_album_by_name("fred")
        self.assertTrue(album_row != None)
        album_id = album_row["id"]
        self.assertEqual(album_row["photo_count"], 0)
        # add some photos here ....
        # make sure they belong to the album
        # make sure album photo count is correct
        plorn_db.close()
        plorn_config.close()

    def test_photo_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album("fred", "barney", None, "now", "note1", "0")
        album_id = db.add_album(album)
        album_row = db.get_album_by_name("fred")
        self.assertTrue(album_row != None)
        self.assertEqual(album_id, album_row["id"])
        self.assertEqual(album_row["photo_count"], 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos here ....
        # make sure total photo count is correct
        photo1 = self.make_photo("bilbo", "shire", None, album_id, "now", "")
        photo_id1 = db.add_photo(photo1, album_id)
        photo2 = self.make_photo("frodo", "shire", None, album_id, "now", "")
        photo_id1 = db.add_photo(photo2, album_id)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)

        plorn_db.close()
        plorn_config.close()

    def test_add_one_photo(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album_row = db.get_album_by_name("fred")
        self.assertTrue(album_row != None)
        album_id = album_row["id"]
        self.assertEqual(album_row["photo_count"], 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        photo1 = self.make_photo("bilbo", "shire", None, album_id, "now", "")
        photo_id1 = db.add_photo(photo1, album_id)

        # can i get back what i added?
        row = db.get_photo_by_id(photo_id1)
        self.assertEqual(row["id"], photo_id1)
        self.assertEqual(row["name"], "bilbo")
        self.assertEqual(row["path"], "shire")
        self.assertEqual(row["album_id"], album_id)
        self.assertEqual(row["dated"], "now")
        self.assertEqual(row["notes"], "")

        # photo counts should have changed
        rows = db.get_photos(album_id)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 1)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 1)
        album_row = db.get_album_by_name("fred")
        self.assertEqual(album_row["photo_count"], 1)

        plorn_db.close()
        plorn_config.close()

    def test_add_photos(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album_row = db.get_album_by_name("fred")
        self.assertTrue(album_row != None)
        album_id = album_row["id"]
        self.assertEqual(album_row["photo_count"], 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos
        photo1 = self.make_photo("bilbo", "shire1", None, album_id, "now", "")
        photo_id1 = db.add_photo(photo1, album_id)
        photo2 = self.make_photo("frodo", "shire2", None, album_id, "now", "")
        photo_id2 = db.add_photo(photo2, album_id)
        self.assertTrue(photo1 != photo2)
        self.assertTrue(photo_id1 != photo_id2)

        # can i get back what i added?
        row = db.get_photo_by_id(photo_id1)
        self.assertEqual(row["id"], photo_id1)
        self.assertEqual(row["name"], "bilbo")
        self.assertEqual(row["path"], "shire1")
        self.assertEqual(row["album_id"], album_id)
        self.assertEqual(row["dated"], "now")
        self.assertEqual(row["notes"], "")

        row = db.get_photo_by_id(photo_id2)
        self.assertEqual(row["id"], photo_id2)
        self.assertEqual(row["name"], "frodo")
        self.assertEqual(row["path"], "shire2")
        self.assertEqual(row["album_id"], album_id)
        self.assertEqual(row["dated"], "now")
        self.assertEqual(row["notes"], "")

        # photo counts should have changed
        rows = db.get_photos(album_id)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 2)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)
        album_row = db.get_album_by_name("fred")
        self.assertEqual(album_row["photo_count"], 2)

        plorn_db.close()
        plorn_config.close()

