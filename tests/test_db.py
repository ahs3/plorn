
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import os

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
)

from conftest import get_test_dbname

from plorn import PlornAlbum, PlornPhoto, PlornName, PlornPlace, PlornTag

from plorn.db import (
    PlornDb,
    AlbumFields,
    ConfigFields,
)

from plorn.config import PlornConfig


#-- basic db tests
def test_open(initial_db):
    assert initial_db != None

def test_multiple_opens(initial_db, bogus_config):
    db1 = QSqlDatabase.database()
    db2 = QSqlDatabase.database()
    assert db1 != None
    assert db2 != None
    db1.close()
    db2.close()

    db1 = PlornDb(get_test_dbname(), bogus_config)
    db2 = PlornDb(get_test_dbname(), bogus_config)
    assert db1 != None
    assert db2 != None
    db1.close()
    db2.close()

def test_config(bogus_config, GUI, initial_db):
    cfg = PlornConfig(bogus_config)
    cfg.open(bogus_config)
    row = initial_db.get_config()
    assert row.value(ConfigFields.NAME) == 'plorn'
    assert row.value(ConfigFields.USERNAME) == 'fred'
    assert row.value(ConfigFields.FULLNAME) == 'Fred Flintstone'
    dbfile = os.path.join(row.value(ConfigFields.DATADIR), get_test_dbname())
    datadir = os.path.expanduser('/tmp/plorn_barney')
    assert row.value(ConfigFields.DATADIR) == datadir

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

def test_album_exists(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = initial_db.add_album(tmp)
    assert initial_db.album_exists(album)

def test_album_does_not_exist(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '1')
    assert initial_db.album_exists(tmp) == False

def test_albums_table_by_name(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', 42)
    orig = initial_db.add_album(tmp)
    album = initial_db.get_album_by_name('fred')

    assert album.get_id() == orig.get_id()
    assert album.get_name() == 'fred'
    assert album.get_dated() == 'now'
    assert album.get_notes() == 'note1'
    assert album.get_photo_count() == 42

def test_albums_table_by_id(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '42')
    orig = initial_db.add_album(tmp)
    album = initial_db.get_album_by_id(orig.get_id())

    assert album.get_id() == orig.get_id()
    assert album.get_name() == 'fred'
    assert album.get_dated() == 'now'
    assert album.get_notes() == 'note1'
    assert album.get_photo_count() == 42

def test_remove_album_by_id(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = initial_db.add_album(tmp)
    assert album.get_id() != None and album.get_id() != 0
    assert initial_db.album_exists(album) == True
    initial_db.remove_album_by_id(album.get_id())
    assert initial_db.album_exists(album) == False

def test_remove_album(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = initial_db.add_album(tmp)
    assert initial_db.album_exists(album) == True
    initial_db.remove_album(album)
    assert initial_db.album_exists(album) == False

def test_get_all_albums(initial_db, bogus_config):
    album1 = make_album('fred', None, 'now', 'note1', '1')
    album2 = make_album('barney', None, 'now', 'note2', '2')
    album1 = initial_db.add_album(album1)
    album2 = initial_db.add_album(album2)
    query = initial_db.get_all_albums_list()
    ids = []
    while query.next():
        ids.append(query.value(AlbumFields.ID))
    assert len(ids) == 2
    assert album1.get_id() in ids
    assert album2.get_id() in ids

def test_album_count(initial_db, bogus_config):
    tmp1 = make_album('fred', None, 'now', 'note1', '1')
    tmp2 = make_album('barney', None, 'now', 'note2', '2')
    album1 = initial_db.add_album(tmp1)
    album2 = initial_db.add_album(tmp2)
    query = initial_db.get_all_albums_list()
    rows = []
    while query.next():
        rows.append(query.value(AlbumFields.ID))
    assert len(rows) == 2
    assert len(rows) == initial_db.album_count()

def test_add_album(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '42')

    #-- add some names
    nlist = []
    for ii in range(0,3):
        ntmp = make_name(f'name{ii:04}', parent_id=0)
        if ii > 0:
            ntmp.set_parent_id(ii-1)
        name = initial_db.add_name(ntmp)
        nlist.append(name)
    tmp.set_name_list(nlist)

    #-- add some places
    plist = []
    for ii in range(0,3):
        ptmp = make_place(f'place{ii:04}', parent_id=0)
        if ii > 0:
            ptmp.set_parent_id(ii-1)
        place = initial_db.add_place(ptmp)
        plist.append(place)
    tmp.set_place_list(plist)

    #-- add some tags
    tlist = []
    for ii in range(0,3):
        ttmp = make_tag(f'tag{ii:04}', parent_id=0)
        if ii > 0:
            ttmp.set_parent_id(ii-1)
        tag = initial_db.add_tag(ttmp)
        tlist.append(tag)
    tmp.set_tag_list(tlist)

    album = initial_db.add_album(tmp)
    new_album = initial_db.get_album(album.get_id())

    assert album.get_id() == new_album.get_id()
    assert new_album.get_name() == 'fred'
    assert new_album.get_notes() == 'note1'
    assert new_album.get_photo_count() == 42

    alist = initial_db.get_names_for_album(new_album)
    for ii in alist:
        found = False
        for jj in nlist:
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found == True

    alist.clear()
    alist = initial_db.get_places_for_album(new_album)
    for ii in alist:
        found = False
        for jj in plist:
            print(f'ii: {ii.get_value()}, jj: {jj.get_value()}')
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found == True

    alist.clear()
    alist = initial_db.get_tags_for_album(new_album)
    for ii in alist:
        found = False
        for jj in tlist:
            if ii.get_value() == jj.get_value():
                found = True
                break
        assert found

def test_update_album(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '1')
    album = initial_db.add_album(tmp)
    album2 = album
    album2.set_notes('lots of notes')
    album2.set_photo_count(12)
    new_album = initial_db.update_album(album, album2)
    assert album.get_id() == new_album.get_id()
    a = initial_db.get_album_by_id(new_album.get_id())
    assert a.get_name() == 'fred'
    assert a.get_notes() == 'lots of notes'
    assert a.get_photo_count() == 12


#-- tests for photos in the db
def get_test_photo_path():
    return os.path.join(os.getcwd(), 'tests/photos')

def make_photo(name, path, photo_id, album_id, dated, notes):
    return PlornPhoto(name, id=photo_id, album_id=album_id,
                      path=path, dated=dated, notes=notes)

def test_get_all_photos(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = initial_db.add_album(tmp)
    assert album != None
    album = initial_db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0

    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = initial_db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = initial_db.add_photo(tmp2)
    assert photo1 != photo2
    assert photo1.get_id() != photo2.get_id()

    album = initial_db.get_album_by_id(album_id)
    assert album.get_photo_count() == 2

def test_photo_count(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = initial_db.add_album(tmp)
    album_row = initial_db.get_album_by_name('fred')
    assert album_row != None
    assert album.get_id() == album_row.get_id()
    assert album_row.get_photo_count() == 0
    nphotos = initial_db.photo_count()
    assert nphotos == 0

    # add some photos here ....
    # make sure total photo count is correct
    album_id = album.get_id()
    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = initial_db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = initial_db.add_photo(tmp2)
    nphotos = initial_db.photo_count()
    assert nphotos == 2

def test_add_one_photo(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = initial_db.add_album(tmp)
    album = initial_db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0
    nphotos = initial_db.photo_count()
    assert nphotos == 0

    photo_path = os.path.join(get_test_photo_path(), 'vespa001.jpg')
    tmp = make_photo('bilbo', photo_path, None, album_id, 'now', '')
    orig = initial_db.add_photo(tmp)

    # can i get back what i added?
    photo = initial_db.get_photo_by_id(orig.get_id())
    assert photo.get_id() == orig.get_id()
    assert photo.get_name() == 'bilbo'
    assert photo.get_path() == photo_path
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    # photo counts should have changed
    more_photos = initial_db.photo_count()
    assert nphotos + 1 == more_photos
    album_row = initial_db.get_album_by_name('fred')
    assert album_row.get_photo_count() == 1

def test_add_photos(initial_db, bogus_config):
    tmp = make_album('fred', None, 'now', 'note1', '0')
    album = initial_db.add_album(tmp)
    album = initial_db.get_album_by_name('fred')
    assert album != None
    album_id = album.get_id()
    assert album.get_photo_count() == 0
    nphotos = initial_db.photo_count()
    assert nphotos == 0

    # add some photos
    photo_path1 = os.path.join(get_test_photo_path(), 'vespa002.jpg')
    tmp1 = make_photo('bilbo', photo_path1, None, album_id, 'now', '')
    photo1 = initial_db.add_photo(tmp1)
    photo_path2 = os.path.join(get_test_photo_path(), 'vespa004.jpg')
    tmp2 = make_photo('frodo', photo_path2, None, album_id, 'now', '')
    photo2 = initial_db.add_photo(tmp2)
    assert photo1 != photo2
    assert photo1.get_id() != photo2.get_id()

    # can i get back what i added?
    photo = initial_db.get_photo_by_id(photo1.get_id())
    assert photo.get_id() == photo1.get_id()
    assert photo.get_name() == 'bilbo'
    assert photo.get_path() == photo_path1
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    photo = initial_db.get_photo_by_id(photo2.get_id())
    assert photo.get_id() == photo2.get_id()
    assert photo.get_name() == 'frodo'
    assert photo.get_path() == photo_path2
    assert photo.get_album_id() == album_id
    assert photo.get_dated() == 'now'
    assert photo.get_notes() == ''

    # photo counts should have changed
    more_photos = initial_db.photo_count()
    assert more_photos == 2
    assert nphotos + 2 == more_photos
    album = initial_db.get_album_by_name('fred')
    assert album.get_photo_count() == 2


#-- tests for names in the db
def make_name(name, parent_id=None):
    return PlornName(name, parent_id=parent_id)

def test_add_name(initial_db, bogus_config):
    tmp = make_name('fred')
    name = initial_db.add_name(tmp)
    assert initial_db.name_exists(name)

def test_add_subname(initial_db, bogus_config):
    tmp = make_name('Flintstone')
    parent = initial_db.add_name(tmp)
    assert initial_db.name_exists(parent)

    p = initial_db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = initial_db.add_name(tmp)
    assert initial_db.name_exists(child)

    c = initial_db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_name_children(initial_db, bogus_config):
    tmp = make_name('Flintstone')
    parent = initial_db.add_name(tmp)
    assert initial_db.name_exists(parent)

    p = initial_db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = initial_db.add_name(tmp)
    assert initial_db.name_exists(child)

    c = initial_db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = initial_db.get_name_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_name(initial_db, bogus_config):
    tmp = make_name('Flintstone')
    parent = initial_db.add_name(tmp)
    assert initial_db.name_exists(parent)

    tmp = make_name('Fred', parent_id=parent.get_id())
    child = initial_db.add_name(tmp)
    assert initial_db.name_exists(child)

    c = initial_db.get_name(child.get_id())
    assert c.get_parent_id() == parent.get_id()
    fullname = initial_db.get_full_name(c)
    assert fullname == ['Flintstone', 'Fred']
    assert ', '.join(fullname) == 'Flintstone, Fred'

def test_get_all_names(initial_db, bogus_config):
    tmp = make_name('Flintstone')
    parent = initial_db.add_name(tmp)
    assert initial_db.name_exists(parent)

    p = initial_db.get_name(parent.get_id())
    tmp = make_name('Fred', parent_id=p.get_id())
    child = initial_db.add_name(tmp)
    assert initial_db.name_exists(child)

    c = initial_db.get_name(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullname = initial_db.get_full_name(c)
    assert fullname == ['Flintstone', 'Fred']
    assert ', '.join(fullname) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_names = initial_db.get_all_names()
    assert len(all_names) == 2
    id_list = []
    for ii in all_names:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_name(initial_db, bogus_config):
    tmp = make_name('fred')
    name = initial_db.add_name(tmp)
    assert initial_db.name_exists(name)

    initial_db.remove_name(name)
    assert not initial_db.name_exists(name)

    names = initial_db.get_all_names()
    assert len(names) == 0

def test_update_name(initial_db, bogus_config):
    tmp = make_name('fred')
    name = initial_db.add_name(tmp)
    assert initial_db.name_exists(name)

    name_copy = copy.deepcopy(name)
    assert name.get_value() == name_copy.get_value()

    name_copy.set_value('barney')
    tid = initial_db.update_name(name, name_copy)
    updated_name = initial_db.get_name(tid)
    assert updated_name.get_value() == 'barney'
    assert updated_name.get_value() != 'fred'

    names = initial_db.get_all_names()
    assert len(names) == 1


#-- tests for places in the db
def make_place(place, parent_id=None):
    return PlornPlace(place, parent_id=parent_id)

def test_add_place(initial_db, bogus_config):
    tmp = make_place('fred')
    place = initial_db.add_place(tmp)
    assert initial_db.place_exists(place)

def test_add_subplace(initial_db, bogus_config):
    tmp = make_place('Flintstone')
    parent = initial_db.add_place(tmp)
    assert initial_db.place_exists(parent)

    p = initial_db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = initial_db.add_place(tmp)
    assert initial_db.place_exists(child)

    c = initial_db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_place_children(initial_db, bogus_config):
    tmp = make_place('Flintstone')
    parent = initial_db.add_place(tmp)
    assert initial_db.place_exists(parent)

    p = initial_db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = initial_db.add_place(tmp)
    assert initial_db.place_exists(child)

    c = initial_db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = initial_db.get_place_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_place(initial_db, bogus_config):
    tmp = make_place('Flintstone')
    parent = initial_db.add_place(tmp)
    assert initial_db.place_exists(parent)

    p = initial_db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = initial_db.add_place(tmp)
    assert initial_db.place_exists(child)

    c = initial_db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullplace = initial_db.get_full_place(c)
    assert fullplace == ['Flintstone', 'Fred']
    assert ', '.join(fullplace) == 'Flintstone, Fred'

def test_get_all_places(initial_db, bogus_config):
    tmp = make_place('Flintstone')
    parent = initial_db.add_place(tmp)
    assert initial_db.place_exists(parent)

    p = initial_db.get_place(parent.get_id())
    tmp = make_place('Fred', parent_id=p.get_id())
    child = initial_db.add_place(tmp)
    assert initial_db.place_exists(child)

    c = initial_db.get_place(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fullplace = initial_db.get_full_place(c)
    assert fullplace == ['Flintstone', 'Fred']
    assert ', '.join(fullplace) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_places = initial_db.get_all_places()
    assert len(all_places) == 2
    id_list = []
    for ii in all_places:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_place(initial_db, bogus_config):
    tmp = make_place('fred')
    place = initial_db.add_place(tmp)
    assert initial_db.place_exists(place)

    initial_db.remove_place(place)
    assert not initial_db.place_exists(place)

    places = initial_db.get_all_places()
    assert len(places) == 0

def test_update_place(initial_db, bogus_config):
    tmp = make_place('fred')
    place = initial_db.add_place(tmp)
    assert initial_db.place_exists(place)

    place_copy = copy.deepcopy(place)
    assert place.get_value() == place_copy.get_value()

    place_copy.set_value('barney')
    tid = initial_db.update_place(place, place_copy)
    updated_place = initial_db.get_place(tid)
    assert updated_place.get_value() == 'barney'
    assert updated_place.get_value() != 'fred'

    places = initial_db.get_all_places()
    assert len(places) == 1


#-- tests for tags in the db
def make_tag(tag, parent_id=None):
    return PlornTag(tag, parent_id=parent_id)

def test_add_tag(initial_db, bogus_config):
    tmp = make_tag('fred')
    tag = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(tag)

def test_add_subtag(initial_db, bogus_config):
    tmp = make_tag('Flintstone')
    parent = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(parent)

    p = initial_db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(child)

    c = initial_db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()

def test_get_tag_children(initial_db, bogus_config):
    tmp = make_tag('Flintstone')
    parent = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(parent)

    p = initial_db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(child)

    c = initial_db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()

    kids = initial_db.get_tag_children(p)
    found = False
    for ii in kids:
        if ii.get_value() == c.get_value():
            found = True
            break
    assert found

def test_get_full_tag(initial_db, bogus_config):
    tmp = make_tag('Flintstone')
    parent = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(parent)

    p = initial_db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(child)

    c = initial_db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fulltag = initial_db.get_full_tag(c)
    assert fulltag == ['Flintstone', 'Fred']
    assert ', '.join(fulltag) == 'Flintstone, Fred'

def test_get_all_tags(initial_db, bogus_config):
    tmp = make_tag('Flintstone')
    parent = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(parent)

    p = initial_db.get_tag(parent.get_id())
    tmp = make_tag('Fred', parent_id=p.get_id())
    child = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(child)

    c = initial_db.get_tag(child.get_id())
    assert c.get_parent_id() == p.get_id()
    fulltag = initial_db.get_full_tag(c)
    assert fulltag == ['Flintstone', 'Fred']
    assert ', '.join(fulltag) == 'Flintstone, Fred'
    assert c.get_parent_id() == p.get_id()

    all_tags = initial_db.get_all_tags()
    assert len(all_tags) == 2
    id_list = []
    for ii in all_tags:
        id_list.append(ii.get_id())
    assert p.get_id() in id_list
    assert c.get_id() in id_list

def test_remove_tag(initial_db, bogus_config):
    tmp = make_tag('fred')
    tag = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(tag)

    initial_db.remove_tag(tag)
    assert not initial_db.tag_exists(tag)

    tags = initial_db.get_all_tags()
    assert len(tags) == 0

def test_update_tag(initial_db, bogus_config):
    tmp = make_tag('fred')
    tag = initial_db.add_tag(tmp)
    assert initial_db.tag_exists(tag)

    tag_copy = copy.deepcopy(tag)
    assert tag.get_value() == tag_copy.get_value()

    tag_copy.set_value('barney')
    tid = initial_db.update_tag(tag, tag_copy)
    updated_tag = initial_db.get_tag(tid)
    assert updated_tag.get_value() == 'barney'
    assert updated_tag.get_value() != 'fred'

    tags = initial_db.get_all_tags()
    assert len(tags) == 1

