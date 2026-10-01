
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import getpass
import os
import pwd
import sys

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
)

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

from plorn import PlornAlbum, PlornPhoto, PlornName, PlornPlace, PlornTag
from plorn.db import (
    AlbumFields,
    ConfigFields,
)
from plorn.rawdb import PlornRawDb


#-- basic db tests
def test_open1(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    assert db != None
    db.close()

def test_open2(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db1 = PlornRawDb(dbpath)
    db2 = PlornRawDb(dbpath)
    assert db1 != None
    assert db2 != None
    db1.close()
    db2.close()

def test_config(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    row = db.get_config()
    assert row['name'] == 'plorn'
    assert row['username'] == 'guest'
    assert row['fullname'] == 'No Body'
    datadir = '.'
    assert row['datadir'] == datadir

#-- tests for albums in the db
def make_album(name, id, dated, notes, nphotos):
    return PlornAlbum(name, id=id, dated=dated, notes=notes,
                      photo_count=nphotos)

def make_name(name, parent_id=0):
    return PlornName(name)

def make_place(place, parent_id=0):
    return PlornPlace(place)

def make_tag(tag, parent_id=0):
    return PlornTag(tag)

def test_album_exists(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = db.add_album(tmp)
    assert db.album_exists(album)

def test_album_does_not_exist(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '1')
    assert db.album_exists(tmp) == False

def test_albums_table_by_name(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', 42)
    orig = db.add_album(tmp)
    album = db.get_album_by_name('fred')

    assert album.get_id() == orig.get_id()
    assert album.get_name() == 'fred'
    assert album.get_dated() == 'now'
    assert album.get_notes() == 'note1'
    assert album.get_photo_count() == 42

def test_albums_table_by_id(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '42')
    orig = db.add_album(tmp)
    album = db.get_album_by_id(orig.get_id())

    assert album.get_id() == orig.get_id()
    assert album.get_name() == 'fred'
    assert album.get_dated() == 'now'
    assert album.get_notes() == 'note1'
    assert album.get_photo_count() == 42

def test_remove_album_by_id(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = db.add_album(tmp)
    assert album.get_id() != None and album.get_id() != 0
    assert db.album_exists(album) == True
    db.remove_album_by_id(album.get_id())
    assert db.album_exists(album) == False

def test_remove_album(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = db.add_album(tmp)
    assert db.album_exists(album) == True
    db.remove_album(album)
    assert db.album_exists(album) == False

def test_get_all_albums(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    album1 = make_album('fred', None, 'now', 'note1', '1')
    album2 = make_album('barney', None, 'now', 'note2', '2')
    album1 = db.add_album(album1)
    album2 = db.add_album(album2)
    cursor = db.get_album_cursor()
    ids = []
    for row in cursor:
        ids.append(row['id'])
    assert len(ids) == 2
    assert album1.get_id() in ids
    assert album2.get_id() in ids

def test_album_count(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp1 = make_album('fred', None, 'now', 'note1', '1')
    tmp2 = make_album('barney', None, 'now', 'note2', '2')
    album1 = db.add_album(tmp1)
    album2 = db.add_album(tmp2)
    cursor = db.get_album_cursor()
    rows = []
    for data in cursor:
        rows.append(data)
    assert len(rows) == 2
    assert len(rows) == db.album_count()

def test_add_album(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '42')

    #-- add some names
    nlist = []
    for ii in range(0,3):
        ntmp = make_name(f'name{ii:04}', parent_id=0)
        if ii > 0:
            ntmp.set_parent_id(ii-1)
        name = db.add_name(ntmp)
        nlist.append(name)
    tmp.set_name_list(nlist)

    #-- add some places
    plist = []
    for ii in range(0,3):
        ptmp = make_place(f'place{ii:04}', parent_id=0)
        if ii > 0:
            ptmp.set_parent_id(ii-1)
        place = db.add_place(ptmp)
        plist.append(place)
    tmp.set_place_list(plist)

    #-- add some tags
    tlist = []
    for ii in range(0,3):
        ttmp = make_tag(f'tag{ii:04}', parent_id=0)
        if ii > 0:
            ttmp.set_parent_id(ii-1)
        tag = db.add_tag(ttmp)
        tlist.append(tag)
    tmp.set_tag_list(tlist)

    album = db.add_album(tmp)
    new_album = db.get_album(album.get_id())

    assert album.get_id() == new_album.get_id()
    assert new_album.get_name() == 'fred'
    assert new_album.get_notes() == 'note1'
    assert new_album.get_photo_count() == 42

    alist = db.get_names_for_album(new_album)
    for ii in alist:
        found = False
        for jj in nlist:
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found == True

    alist.clear()
    alist = db.get_places_for_album(new_album)
    for ii in alist:
        found = False
        for jj in plist:
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found == True

    alist.clear()
    alist = db.get_tags_for_album(new_album)
    for ii in alist:
        found = False
        for jj in tlist:
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found

def test_update_album(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = db.add_album(tmp)
    album2 = album
    album2.set_notes('lots of notes')
    album2.set_photo_count(12)
    new_album = db.update_album(album, album2)
    assert album.get_id() == new_album.get_id()
    a = db.get_album_by_id(new_album.get_id())
    assert a.get_name() == 'fred'
    assert a.get_notes() == 'lots of notes'
    assert a.get_photo_count() == 12


#-- tests for photos in the db
def get_test_photo_path():
    return os.path.join(os.getcwd(), 'tests/photos')

def make_photo(name, path, photo_id, album_id, dated, notes):
    return PlornPhoto(name, id=photo_id, album_id=album_id,
                      path=path, dated=dated, notes=notes)

def test_get_all_photos(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = db.add_album(tmp)
    assert album != None
    album = db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0

    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = db.add_photo(tmp2)
    assert photo1 != photo2
    assert photo1.get_id() != photo2.get_id()

    album = db.get_album_by_id(album_id)
    assert album.get_photo_count() == 2

def test_photo_count(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = db.add_album(tmp)
    album_row = db.get_album_by_name('fred')
    assert album_row != None
    assert album.get_id() == album_row.get_id()
    assert album_row.get_photo_count() == 0
    nphotos = db.photo_count()
    assert nphotos == 0

    # add some photos here ....
    # make sure total photo count is correct
    album_id = album.get_id()
    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = db.add_photo(tmp2)
    nphotos = db.photo_count()
    assert nphotos == 2

def test_add_one_photo(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = db.add_album(tmp)
    album = db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0
    nphotos = db.photo_count()
    assert nphotos == 0

    photo_path = os.path.join(get_test_photo_path(), 'vespa001.jpg')
    tmp = make_photo('bilbo', photo_path, None, album_id, 'now', '')
    orig = db.add_photo(tmp)

    # can i get back what i added?
    photo = db.get_photo_by_id(orig.get_id())
    assert photo.get_id() == orig.get_id()
    assert photo.get_name() == 'bilbo'
    assert photo.get_path() == photo_path
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    # photo counts should have changed
    more_photos = db.photo_count()
    assert nphotos + 1 == more_photos
    album_row = db.get_album_by_name('fred')
    assert album_row.get_photo_count() == 1

def test_add_photos(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = db.add_album(tmp)
    album = db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0
    nphotos = db.photo_count()
    assert nphotos == 0

    # add some photos
    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = db.add_photo(tmp2)
    assert photo1 != photo2
    assert photo1.get_id() != photo2.get_id()

    # can i get back what i added?
    photo = db.get_photo_by_id(photo1.get_id())
    assert photo.get_id() == photo1.get_id()
    assert photo.get_name() == 'bilbo'
    assert photo.get_path() == photo_path1
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    photo = db.get_photo_by_id(photo2.get_id())
    assert photo.get_id() == photo2.get_id()
    assert photo.get_name() == 'frodo'
    assert photo.get_path() == photo_path2
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    # photo counts should have changed
    more_photos = db.photo_count()
    assert more_photos == 2
    assert nphotos + 2 == more_photos
    album = db.get_album_by_name('fred')
    assert album.get_photo_count() == 2


#-- tests for names in the db
def make_name(name, parent_id=None):
    return PlornName(name, parent_id=parent_id)

def test_add_name(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('fred')
    name = db.add_name(tmp)
    assert db.name_exists(name)

def test_add_subname(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('Flintstone')
    parent = db.add_name(tmp)
    assert db.name_exists(parent)

    p = db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = db.add_name(tmp)
    assert db.name_exists(child)

    c = db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_name_children(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('Flintstone')
    parent = db.add_name(tmp)
    assert db.name_exists(parent)

    p = db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = db.add_name(tmp)
    assert db.name_exists(child)

    c = db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = db.get_name_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_name(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('Flintstone')
    parent = db.add_name(tmp)
    assert db.name_exists(parent)

    tmp = make_name('Fred', parent_id=parent.get_id())
    child = db.add_name(tmp)
    assert db.name_exists(child)

    c = db.get_name(child.get_id())
    assert c.get_parent_id() == parent.get_id()
    fullname = db.get_full_name(c)
    assert fullname == ['Flintstone', 'Fred']
    assert ', '.join(fullname) == 'Flintstone, Fred'

def test_get_all_names(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('Flintstone')
    parent = db.add_name(tmp)
    assert db.name_exists(parent)

    p = db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = db.add_name(tmp)
    assert db.name_exists(child)

    c = db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullname = db.get_full_name(c)
    assert fullname == ['Flintstone', 'Fred']
    assert ', '.join(fullname) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_names = db.get_all_names()
    assert len(all_names) == 2
    id_list = []
    for ii in all_names:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_name(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('fred')
    name = db.add_name(tmp)
    assert db.name_exists(name)

    db.remove_name(name)
    assert not db.name_exists(name)

    names = db.get_all_names()
    assert len(names) == 0

def test_update_name(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_name('fred')
    name = db.add_name(tmp)
    assert db.name_exists(name)

    name_copy = copy.deepcopy(name)
    assert name.get_value() == name_copy.get_value()

    name_copy.set_value('barney')
    tid = db.update_name(name, name_copy)
    updated_name = db.get_name(tid)
    assert updated_name.get_value() == 'barney'
    assert updated_name.get_value() != 'fred'

    names = db.get_all_names()
    assert len(names) == 1


#-- tests for places in the db
def make_place(place, parent_id=None):
    return PlornPlace(place, parent_id=parent_id)

def test_add_place(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('fred')
    place = db.add_place(tmp)
    assert db.place_exists(place)

def test_add_subplace(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('Flintstone')
    parent = db.add_place(tmp)
    assert db.place_exists(parent)

    p = db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = db.add_place(tmp)
    assert db.place_exists(child)

    c = db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_place_children(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('Flintstone')
    parent = db.add_place(tmp)
    assert db.place_exists(parent)

    p = db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = db.add_place(tmp)
    assert db.place_exists(child)

    c = db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = db.get_place_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_place(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('Flintstone')
    parent = db.add_place(tmp)
    assert db.place_exists(parent)

    p = db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = db.add_place(tmp)
    assert db.place_exists(child)

    c = db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullplace = db.get_full_place(c)
    assert fullplace == ['Flintstone', 'Fred']
    assert ', '.join(fullplace) == 'Flintstone, Fred'

def test_get_all_places(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('Flintstone')
    parent = db.add_place(tmp)
    assert db.place_exists(parent)

    p = db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = db.add_place(tmp)
    assert db.place_exists(child)

    c = db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullplace = db.get_full_place(c)
    assert fullplace == ['Flintstone', 'Fred']
    assert ', '.join(fullplace) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_places = db.get_all_places()
    assert len(all_places) == 2
    id_list = []
    for ii in all_places:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_place(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('fred')
    place = db.add_place(tmp)
    assert db.place_exists(place)

    db.remove_place(place)
    assert not db.place_exists(place)

    places = db.get_all_places()
    assert len(places) == 0

def test_update_place(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_place('fred')
    place = db.add_place(tmp)
    assert db.place_exists(place)

    place_copy = copy.deepcopy(place)
    assert place.get_value() == place_copy.get_value()

    place_copy.set_value('barney')
    tid = db.update_place(place, place_copy)
    updated_place = db.get_place(tid)
    assert updated_place.get_value() == 'barney'
    assert updated_place.get_value() != 'fred'

    places = db.get_all_places()
    assert len(places) == 1


#-- tests for tags in the db
def make_tag(tag, parent_id=None):
    return PlornTag(tag, parent_id=parent_id)

def test_add_tag(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('fred')
    tag = db.add_tag(tmp)
    assert db.tag_exists(tag)

def test_add_subtag(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('Flintstone')
    parent = db.add_tag(tmp)
    assert db.tag_exists(parent)

    p = db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = db.add_tag(tmp)
    assert db.tag_exists(child)

    c = db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_tag_children(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('Flintstone')
    parent = db.add_tag(tmp)
    assert db.tag_exists(parent)

    p = db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = db.add_tag(tmp)
    assert db.tag_exists(child)

    c = db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = db.get_tag_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_tag(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('Flintstone')
    parent = db.add_tag(tmp)
    assert db.tag_exists(parent)

    p = db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = db.add_tag(tmp)
    assert db.tag_exists(child)

    c = db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fulltag = db.get_full_tag(c)
    assert fulltag == ['Flintstone', 'Fred']
    assert ', '.join(fulltag) == 'Flintstone, Fred'

def test_get_all_tags(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('Flintstone')
    parent = db.add_tag(tmp)
    assert db.tag_exists(parent)

    p = db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = db.add_tag(tmp)
    assert db.tag_exists(child)

    c = db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fulltag = db.get_full_tag(c)
    assert fulltag == ['Flintstone', 'Fred']
    assert ', '.join(fulltag) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_tags = db.get_all_tags()
    assert len(all_tags) == 2
    id_list = []
    for ii in all_tags:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_tag(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('fred')
    tag = db.add_tag(tmp)
    assert db.tag_exists(tag)

    db.remove_tag(tag)
    assert not db.tag_exists(tag)

    tags = db.get_all_tags()
    assert len(tags) == 0

def test_update_tag(tmp_path):
    dbpath = os.path.join(tmp_path, 'testing.db')
    db = PlornRawDb(dbpath)
    db.truncate_tables()
    tmp = make_tag('fred')
    tag = db.add_tag(tmp)
    assert db.tag_exists(tag)

    tag_copy = copy.deepcopy(tag)
    assert tag.get_value() == tag_copy.get_value()

    tag_copy.set_value('barney')
    tid = db.update_tag(tag, tag_copy)
    updated_tag = db.get_tag(tid)
    assert updated_tag.get_value() == 'barney'
    assert updated_tag.get_value() != 'fred'

    tags = db.get_all_tags()
    assert len(tags) == 1

