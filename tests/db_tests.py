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
        plorn_config.close()

    def test_multiple_opens(self):
        db1 = plorn_db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        db2 = plorn_db.open(self.get_test_dbname(),
                            self.get_test_cfgname())
        self.assertTrue(db1 == db2)
        db1.close()
        db2.close()
        plorn_db.close()
        plorn_config.close()

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
        tmp = self.make_album("fred", "barney", None, "now", "note1", "1")
        album = db.add_album(tmp)
        self.assertTrue(db.album_exists(album))
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album("fred", "barney", None, "now", "note1", "42")
        orig = db.add_album(tmp)
        album = db.get_album_by_name("fred")

        self.assertEqual(album.get_id(), orig.get_id())
        self.assertEqual(album.get_name(), "fred")
        self.assertEqual(album.get_path(), "barney")
        self.assertEqual(album.get_dated(), "now")
        self.assertEqual(album.get_notes(), "note1")
        self.assertEqual(album.get_photo_count(), 42)
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_id(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album("fred", "barney", None, "now", "note1", "42")
        orig = db.add_album(tmp)
        album = db.get_album_by_id(orig.get_id())

        self.assertEqual(album.get_id(), orig.get_id())
        self.assertEqual(album.get_name(), "fred")
        self.assertEqual(album.get_path(), "barney")
        self.assertEqual(album.get_dated(), "now")
        self.assertEqual(album.get_notes(), "note1")
        self.assertEqual(album.get_photo_count(), 42)
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
        album1 = db.add_album(album1)
        album2 = db.add_album(album2)
        albums = db.get_albums()
        self.assertEqual(len(albums), 2)
        album = albums[0]
        ids = []
        for ii in albums:
            ids.append(ii.get_id())
        self.assertTrue(album1.get_id() in ids)
        self.assertTrue(album2.get_id() in ids)
        self.assertTrue(album.get_id() in ids)
        self.assertEqual(album.get_name(), "fred")
        self.assertEqual(album.get_path(), "barney")
        plorn_db.close()
        plorn_config.close()

    def test_album_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp1 = self.make_album("fred", "barney", None, "now", "note1", "1")
        tmp2 = self.make_album("barney", "barney", None, "now", "note2", "2")
        album1 = db.add_album(tmp1)
        album2 = db.add_album(tmp2)
        albums = db.get_albums()
        self.assertEqual(len(albums), 2)
        self.assertEqual(len(albums), db.album_count())
        plorn_db.close()
        plorn_config.close()

    def test_update_album(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album("fred", "barney", None, "now", "note1", "1")
        album = db.add_album(tmp)
        album2 = album
        album2.set_path("wilma")
        album2.set_notes("lots of notes")
        album2.set_photo_count(12)
        new_album = db.update_album(album, album2)
        self.assertEqual(album.get_id(), new_album.get_id())
        a = db.get_album_by_id(new_album.get_id())
        self.assertEqual(a.get_name(), "fred")
        self.assertEqual(a.get_path(), "wilma")
        self.assertEqual(a.get_notes(), "lots of notes")
        self.assertEqual(a.get_photo_count(), 12)
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
        plorn_db.close()
        plorn_config.close()
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
        album = db.get_album_by_name("fred")
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)
        # add some photos here ....
        # make sure they belong to the album
        # make sure album photo count is correct
        plorn_db.close()
        plorn_config.close()

    def test_photo_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album("fred", "barney", None, "now", "note1", "0")
        album = db.add_album(tmp)
        album_row = db.get_album_by_name("fred")
        self.assertTrue(album_row != None)
        self.assertEqual(album.get_id(), album_row.get_id())
        self.assertEqual(album_row.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos here ....
        # make sure total photo count is correct
        album_id = album.get_id()
        tmp1 = self.make_photo("bilbo", "shire", None, album_id, "now", "")
        photo1 = db.add_photo(tmp1, album_id)
        tmp2 = self.make_photo("frodo", "shire", None, album_id, "now", "")
        photo1 = db.add_photo(tmp2, album_id)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)

        plorn_db.close()
        plorn_config.close()

    def test_add_one_photo(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = db.get_album_by_name("fred")
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        tmp = self.make_photo("bilbo", "shire", None, album_id, "now", "")
        orig = db.add_photo(tmp, album_id)

        # can i get back what i added?
        photo = db.get_photo_by_id(orig.get_id())
        self.assertEqual(photo.get_id(), orig.get_id())
        self.assertEqual(photo.get_name(), "bilbo")
        self.assertEqual(photo.get_path(), "shire")
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), "now")
        self.assertEqual(photo.get_notes(), "")

        # photo counts should have changed
        rows = db.get_photos(album_id)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 1)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 1)
        album_row = db.get_album_by_name("fred")
        self.assertEqual(album_row.get_photo_count(), 1)

        plorn_db.close()
        plorn_config.close()

    def test_add_photos(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = db.get_album_by_name("fred")
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos
        tmp1 = self.make_photo("bilbo", "shire1", None, album_id, "now", "")
        photo1 = db.add_photo(tmp1, album_id)
        tmp2 = self.make_photo("frodo", "shire2", None, album_id, "now", "")
        photo2 = db.add_photo(tmp2, album_id)
        self.assertTrue(photo1 != photo2)
        self.assertTrue(photo1.get_id() != photo2.get_id())

        # can i get back what i added?
        photo = db.get_photo_by_id(photo1.get_id())
        self.assertEqual(photo.get_id(), photo1.get_id())
        self.assertEqual(photo.get_name(), "bilbo")
        self.assertEqual(photo.get_path(), "shire1")
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), "now")
        self.assertEqual(photo.get_notes(), "")

        photo = db.get_photo_by_id(photo2.get_id())
        self.assertEqual(photo.get_id(), photo2.get_id())
        self.assertEqual(photo.get_name(), "frodo")
        self.assertEqual(photo.get_path(), "shire2")
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), "now")
        self.assertEqual(photo.get_notes(), "")

        # photo counts should have changed
        rows = db.get_photos(album_id)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 2)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)
        album = db.get_album_by_name("fred")
        self.assertEqual(album.get_photo_count(), 2)

        plorn_db.close()
        plorn_config.close()

