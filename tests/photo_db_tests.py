import os
import shutil
import sys
import unittest

import plorn_album
import plorn_config
import plorn_db
import plorn_photo


class TestDbPhotoMethods(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            '[plorn]',
            'user = fred',
            'full_name = Fred Flintstone',
            'config_dir = /tmp/plorn_barney',
            'data_dir = /tmp/plorn_barney',
            'dbname = completely_bogus.db',
        ]
        with open(name, 'w') as cfg:
            for ii in data:
                cfg.write(ii + '\n')
        cfg.close()

    def get_test_dbname(self):
        return 'completely_bogus.db'

    def get_test_cfgname(self):
        return os.path.join('/tmp/plorn_barney', 'completely_bogus.cfg')

    def get_test_photo_path(self):
        return os.path.join(os.getcwd(), 'tests/fred')

    def make_album(self, name, path, id, dated, notes, nphotos):
        return plorn_album.PlornAlbum(name, id, dated, notes, nphotos)

    def setUp(self):
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

        os.makedirs('/tmp/plorn_barney', exist_ok=True)
        self.write_test_config(self.get_test_cfgname())
        cfg = plorn_config.get_config(self.get_test_cfgname())
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        photo_dir = os.path.join(os.getcwd(), 'tests/test_album')
        tmp = self.make_album('fred', photo_dir, None, 'now', 'note1', '0')
        album = db.add_album(tmp)
        plorn_db.close()
        plorn_config.close()

    def tearDown(self):
        plorn_db.close()
        plorn_config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(os.path.join(cfg, dbname)):
            os.remove(os.path.join(cfg, dbname))
        if os.path.exists(cfg):
            os.remove(cfg)
        shutil.rmtree('/tmp/plorn_barney')

    def make_photo(self, name, path, photo_id, album_id,
                   dated, notes):
        return plorn_photo.PlornPhoto(name, id=photo_id, album_id=album_id,
                                      path=path, dated=dated, notes=notes)

    def test_get_all_photos(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = db.get_album_by_name('fred')
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)

        photo_path1 = os.path.join(self.get_test_photo_path(), 'vespa002.jpg')
        tmp1 = self.make_photo('bilbo', photo_path1, None, album_id, 'now', '')
        photo1 = db.add_photo(tmp1)
        photo_path2 = os.path.join(self.get_test_photo_path(), 'vespa004.jpg')
        tmp2 = self.make_photo('frodo', photo_path2, None, album_id, 'now', '')
        photo2 = db.add_photo(tmp2)
        self.assertTrue(photo1 != photo2)
        self.assertTrue(photo1.get_id() != photo2.get_id())

        album = db.get_album_by_id(album_id)
        self.assertEqual(album.get_photo_count(), 2)
        plorn_db.close()
        plorn_config.close()

    def test_photo_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', 'barney', None, 'now', 'note1', '0')
        album = db.add_album(tmp)
        album_row = db.get_album_by_name('fred')
        self.assertTrue(album_row != None)
        self.assertEqual(album.get_id(), album_row.get_id())
        self.assertEqual(album_row.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos here ....
        # make sure total photo count is correct
        album_id = album.get_id()
        photo_path1 = os.path.join(self.get_test_photo_path(), 'vespa002.jpg')
        tmp1 = self.make_photo('bilbo', photo_path1, None, album_id, 'now', '')
        photo1 = db.add_photo(tmp1)
        photo_path2 = os.path.join(self.get_test_photo_path(), 'vespa004.jpg')
        tmp2 = self.make_photo('frodo', photo_path2, None, album_id, 'now', '')
        photo2 = db.add_photo(tmp2)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)

        plorn_db.close()
        plorn_config.close()

    def test_add_one_photo(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = db.get_album_by_name('fred')
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        photo_path = os.path.join(self.get_test_photo_path(), 'vespa001.jpg')
        tmp = self.make_photo('bilbo', photo_path, None, album_id, 'now', '')
        orig = db.add_photo(tmp)

        # can i get back what i added?
        photo = db.get_photo_by_id(orig.get_id())
        self.assertEqual(photo.get_id(), orig.get_id())
        self.assertEqual(photo.get_name(), 'bilbo')
        self.assertEqual(photo.get_path(), photo_path)
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), 'now')
        self.assertEqual(photo.get_notes(), '')

        # photo counts should have changed
        rows = []
        cursor = db.get_photo_cursor(int(album_id))
        for ii in cursor:
            rows.append(ii)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 1)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 1)
        album_row = db.get_album_by_name('fred')
        self.assertEqual(album_row.get_photo_count(), 1)

        plorn_db.close()
        plorn_config.close()

    def test_add_photos(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = db.get_album_by_name('fred')
        self.assertTrue(album != None)
        album_id = album.get_id()
        self.assertEqual(album.get_photo_count(), 0)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 0)

        # add some photos
        photo_path1 = os.path.join(self.get_test_photo_path(), 'vespa002.jpg')
        tmp1 = self.make_photo('bilbo', photo_path1, None, album_id, 'now', '')
        photo1 = db.add_photo(tmp1)
        photo_path2 = os.path.join(self.get_test_photo_path(), 'vespa004.jpg')
        tmp2 = self.make_photo('frodo', photo_path2, None, album_id, 'now', '')
        photo2 = db.add_photo(tmp2)
        self.assertTrue(photo1 != photo2)
        self.assertTrue(photo1.get_id() != photo2.get_id())

        # can i get back what i added?
        photo = db.get_photo_by_id(photo1.get_id())
        self.assertEqual(photo.get_id(), photo1.get_id())
        self.assertEqual(photo.get_name(), 'bilbo')
        self.assertEqual(photo.get_path(), photo_path1)
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), 'now')
        self.assertEqual(photo.get_notes(), '')

        photo = db.get_photo_by_id(photo2.get_id())
        self.assertEqual(photo.get_id(), photo2.get_id())
        self.assertEqual(photo.get_name(), 'frodo')
        self.assertEqual(photo.get_path(), photo_path2)
        self.assertEqual(photo.get_album_id(), album_id)
        self.assertEqual(photo.get_dated(), 'now')
        self.assertEqual(photo.get_notes(), '')

        # photo counts should have changed
        rows = []
        cursor = db.get_photo_cursor(album_id)
        for ii in cursor:
            rows.append(ii)
        self.assertTrue(rows != None)
        self.assertEqual(len(rows), 2)
        nphotos = db.photo_count()
        self.assertEqual(nphotos, 2)
        album = db.get_album_by_name('fred')
        self.assertEqual(album.get_photo_count(), 2)

        plorn_db.close()
        plorn_config.close()

