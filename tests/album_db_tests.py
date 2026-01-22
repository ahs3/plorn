import copy
import os
import shutil
import sys
import unittest

import plorn_album
import plorn_attr
import plorn_config
import plorn_db
import plorn_photo


class TestDbAlbumMethods(unittest.TestCase):

    def write_test_config(self, name):
        data = [
            '[plorn]',
            'user = fred',
            'full_name = Fred Flintstone',
            'config_dir = /tmp/plorn_barney',
            f'data_dir = {os.path.expanduser('~/.local/share/plorn')}',
            'dbname = completely_bogus.db',
        ]
        with open(name, 'w') as cfg:
            for ii in data:
                cfg.write(ii + '\n')
        cfg.close()

    def get_test_dbname(self):
        dbpath = os.path.expanduser('~/.local/share/plorn')
        return os.path.join(dbpath, 'completely_bogus.db')

    def get_test_cfgname(self):
        path = os.path.expanduser('~/.config/plorn')
        return os.path.join(path, 'completely_bogus.cfg')

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

    def make_album(self, name, id, dated, notes, nphotos):
        return plorn_album.PlornAlbum(name, id, dated, notes, nphotos)

    def make_name(self, name, parent_id=0):
        return plorn_attr.PlornName(name)

    def make_place(self, place, parent_id=0):
        return plorn_attr.PlornPlace(place)

    def make_tag(self, tag, parent_id=0):
        return plorn_attr.PlornTag(tag)

    def test_album_exists(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', None, 'now', 'note1', '1')
        album = db.add_album(tmp)
        self.assertTrue(db.album_exists(album))
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', None, 'now', 'note1', '42')
        orig = db.add_album(tmp)
        album = db.get_album_by_name('fred')

        self.assertEqual(album.get_id(), orig.get_id())
        self.assertEqual(album.get_name(), 'fred')
        self.assertEqual(album.get_dated(), 'now')
        self.assertEqual(album.get_notes(), 'note1')
        self.assertEqual(album.get_photo_count(), 42)
        plorn_db.close()
        plorn_config.close()

    def test_albums_table_by_id(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', None, 'now', 'note1', '42')
        orig = db.add_album(tmp)
        album = db.get_album_by_id(orig.get_id())

        self.assertEqual(album.get_id(), orig.get_id())
        self.assertEqual(album.get_name(), 'fred')
        self.assertEqual(album.get_dated(), 'now')
        self.assertEqual(album.get_notes(), 'note1')
        self.assertEqual(album.get_photo_count(), 42)
        plorn_db.close()
        plorn_config.close()

    def test_remove_by_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album = self.make_album('fred', None, 'now', 'note1', '1')
        id = db.add_album(album)
        self.assertTrue(db.album_exists(album))
        db.remove_album_by_name('fred')
        self.assertFalse(db.album_exists(album))
        plorn_db.close()
        plorn_config.close()

    def test_get_all_albums(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        album1 = self.make_album('fred', None, 'now', 'note1', '1')
        album2 = self.make_album('barney', None, 'now', 'note2', '2')
        album1 = db.add_album(album1)
        album2 = db.add_album(album2)
        album_cursor = db.get_album_cursor()
        ids = []
        album = None
        for ii in album_cursor:
            if not album:
                album = ii
            ids.append(ii['id'])
        self.assertEqual(len(ids), 2)
        self.assertTrue(album1.get_id() in ids)
        self.assertTrue(album2.get_id() in ids)
        self.assertTrue(album['id'] in ids)
        self.assertEqual(album['name'], 'fred')
        plorn_db.close()
        plorn_config.close()

    def test_album_count(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp1 = self.make_album('fred', None, 'now', 'note1', '1')
        tmp2 = self.make_album('barney', None, 'now', 'note2', '2')
        album1 = db.add_album(tmp1)
        album2 = db.add_album(tmp2)
        album_cursor = db.get_album_cursor()
        rows = []
        for ii in album_cursor:
            rows.append(ii)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows), db.album_count())
        plorn_db.close()
        plorn_config.close()

    def test_add_album(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', None, 'now', 'note1', '42')

        #-- add some names
        nlist = []
        for ii in range(0,3):
            ntmp = self.make_name(f'name{ii:04}', parent_id=0)
            if ii > 0:
                ntmp.set_parent_id(ii-1)
            name = db.add_name(ntmp)
            nlist.append(name)
        tmp.set_name_list(nlist)

        #-- add some places
        plist = []
        for ii in range(0,3):
            ptmp = self.make_place(f'place{ii:04}', parent_id=0)
            if ii > 0:
                ptmp.set_parent_id(ii-1)
            place = db.add_place(ptmp)
            plist.append(place)
        tmp.set_place_list(plist)

        #-- add some tags
        tlist = []
        for ii in range(0,3):
            ttmp = self.make_tag(f'tag{ii:04}', parent_id=0)
            if ii > 0:
                ttmp.set_parent_id(ii-1)
            tag = db.add_tag(ttmp)
            tlist.append(tag)
        tmp.set_tag_list(tlist)

        album = db.add_album(tmp)
        #-- DEBUG
        #print('-- ORIGINAL VALUES:')
        #alist = album.get_name_list()
        #print(f'test: names len {len(alist)}')
        #for ii in alist:
        #    print(f'test: name: {ii}')
        #alist = album.get_place_list()
        #print(f'test: places len {len(alist)}')
        #for ii in alist:
        #    print(f'test: place: {ii}')
        #alist = album.get_tag_list()
        #print(f'test: tags len {len(alist)}')
        #for ii in alist:
        #    print(f'test: tag: {ii}')
        #
        #print('-- raw names table:')
        #for ii in db.get_raw_names_table():
        #    print(f'   {str(ii)}')
        #print('-- raw places table:')
        #for ii in db.get_raw_places_table():
        #    print(f'   {str(ii)}')
        #print('-- raw tags table:')
        #for ii in db.get_raw_tags_table():
        #    print(f'   {str(ii)}')
        #-- END DEBUG

        new_album = db.get_album(album.get_id())
        #-- DEBUG
        #print(f'-- NEW_ALBUM VALUES: album_id {album.get_id()}')
        #alist = new_album.get_name_list()
        #print(f'test: names len {len(alist)}')
        #for ii in alist:
        #    print(f'test: name: {ii}')
        #alist = new_album.get_place_list()
        #print(f'test: places len {len(alist)}')
        #for ii in alist:
        #    print(f'test: place: {ii}')
        #alist = new_album.get_tag_list()
        #print(f'test: tags len {len(alist)}')
        #for ii in alist:
        #    print(f'test: tag: {ii}')

        #print('-- raw names table:')
        #for ii in db.get_raw_names_table():
        #    print(f'   {str(ii)}')
        #print('-- raw places table:')
        #for ii in db.get_raw_places_table():
        #    print(f'   {str(ii)}')
        #print('-- raw tags table:')
        #for ii in db.get_raw_tags_table():
        #    print(f'   {str(ii)}')
        #-- END DEBUG

        self.assertEqual(album.get_id(), new_album.get_id())
        self.assertEqual(new_album.get_name(), 'fred')
        self.assertEqual(new_album.get_notes(), 'note1')
        self.assertEqual(new_album.get_photo_count(), 42)

        alist = db.get_names_for_album(new_album)
        for ii in alist:
            found = False
            for jj in nlist:
                #print(f'{ii.get_value()}, {jj.get_value()}')
                if ii.get_value() == jj.get_value():
                    found = True
                    break
            self.assertTrue(found)

        alist.clear()
        alist = db.get_places_for_album(new_album)
        for ii in alist:
            found = False
            for jj in plist:
                #print(f'{ii.get_value()}, {jj.get_value()}')
                if ii.get_value() == jj.get_value():
                    found = True
                    break
            self.assertTrue(found)

        alist.clear()
        alist = db.get_tags_for_album(new_album)
        for ii in alist:
            found = False
            for jj in tlist:
                #print(f'{ii.get_value()}, {jj.get_value()}')
                if ii.get_value() == jj.get_value():
                    found = True
                    break
            self.assertTrue(found)

        plorn_db.close()
        plorn_config.close()

    def test_update_album(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        tmp = self.make_album('fred', None, 'now', 'note1', '1')
        album = db.add_album(tmp)
        album2 = album
        album2.set_notes('lots of notes')
        album2.set_photo_count(12)
        new_album = db.update_album(album, album2)
        self.assertEqual(album.get_id(), new_album.get_id())
        a = db.get_album_by_id(new_album.get_id())
        self.assertEqual(a.get_name(), 'fred')
        self.assertEqual(a.get_notes(), 'lots of notes')
        self.assertEqual(a.get_photo_count(), 12)
        plorn_db.close()
        plorn_config.close()

