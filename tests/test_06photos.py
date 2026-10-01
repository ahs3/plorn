
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import datetime
import os
import random
import string

from PyQt6.QtGui import (
    QAction,
    QStandardItem,
)

from PyQt6.QtCore import (
    Qt,
    QPoint,
    QTimer,
)

from PyQt6.QtSql import (
    QSqlQuery,
)

from PyQt6 import QtTest

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QWidget,
)

from plorn import (
    AlbumFields,
    AttrFields,
    ConfigFields,
    PlornAlbum,
    PlornName,
    PlornPlace,
    PlornPhoto,
    PlornTag,
)

from plorn.config import PlornConfig

from plorn.gui import (
    PlornAboutDialog,
    PlornNewCatalogDialog,
    user_interface,
)

from plorn.models.attrs import PlornAttrModel
from plorn.models.dbops import PlornDbOperations
from plorn.models.albums import PlornAlbumModel

from plorn.widgets import (
    PlornAttrView,
    PlornCatalogView,
)

from plorn.widgets.albums import (
    PlornAlbumDialog,
)

from plorn.widgets.photos import (
    PlornPhotoDialog,
    PlornViewPhotoDialog,
)


####################################################################
#
#   test photo operations
#
def search_attr_tree(node, value):
    if node and node.hasChildren():
        for ii in range(node.rowCount()):
            found = search_attr_tree(node.child(ii), value)
            if found:
                return found
    if node and node.text() == value:
        return True
    return False

def isValueInDb(db, table, value):
    sql = f'SELECT * FROM {table} WHERE value = "{value}";'
    query = QSqlQuery(sql, db=db)
    query.next()
    if query.value(AttrFields.VALUE) == value:
        return True
    return False

def random_string(tree_root):
    count = 100                     # ... just in case ....
    clist = []
    for ii in range(16):
        clist.append(random.choice(string.ascii_letters + string.digits))
    randstr = ''.join(clist)
    while True and count > 0:
        found = search_attr_tree(tree_root, randstr)
        if not found:
            return randstr
        clist = []
        for ii in range(16):
            clist.append(random.choice(string.ascii_letters + string.digits))
        randstr = ''.join(clist)
        count -= 1
    return 'foobar'

def add_an_album(tree_root):
    name  = random_string(tree_root)
    dated = random_string(tree_root)
    notes = random_string(tree_root)
    album = PlornAlbum(name, id=None, dated=dated, notes=notes)
    album = PlornDbOperations.add_album(album)
    return album

def test_view_photo1(initial_db, monkeypatch):
    '''
    use the dialog directly to add a simple photo with no attributes;
    we're really just testing the dialog itself
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    assert tree.model != None

    tree_root = tree.model.invisibleRootItem()
    album = add_an_album(tree_root)
    name  = random_string(tree_root)
    album_id = album.get_id()
    path  = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)
    photo = PlornPhoto(name, id=None, album_id=album_id,
                       path=path, dated=dated, notes=notes)
    photo = PlornDbOperations.add_photo(photo)
    assert photo != None

    dlg = PlornViewPhotoDialog(tree=tree, allow_edit=False)
    dlg.set_inputs(photo)

    dlginfo = dlg.get_inputs()
    assert name  == dlginfo['photo']
    assert path  == dlginfo['path']
    assert dated == dlginfo['dated']
    assert notes == dlginfo['notes']

def test_view_photo2(initial_db, monkeypatch):
    '''
    use the dialog directly to add a simple photo with at least
    one attribute of each type; we're really just testing the 
    dialog itself
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    assert tree.model != None

    tree_root = tree.model.invisibleRootItem()
    album = add_an_album(tree_root)
    photo_name  = random_string(tree_root)
    album_id = album.get_id()
    path  = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    assert name_attr.get_id() != 0

    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    assert place_attr.get_id() != 0

    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)
    assert tag_attr.get_id() != 0

    photo = PlornPhoto(photo_name, id=None, album_id=album_id,
                       path=path, dated=dated, notes=notes,
                       names=[name_attr],
                       places=[place_attr],
                       tags=[tag_attr])
    photo = PlornDbOperations.add_photo(photo)
    assert photo != None

    dlg = PlornViewPhotoDialog(tree=tree, allow_edit=False)
    dlg.set_inputs(photo)
    assert dlg.name_list.rowCount() > 0
    assert dlg.place_list.rowCount() > 0
    assert dlg.tag_list.rowCount() > 0

    dlginfo = dlg.get_inputs()
    assert photo_name == dlginfo['photo']
    assert path  == dlginfo['path']
    assert dated == dlginfo['dated']
    assert notes == dlginfo['notes']
    assert dlginfo['names'][0].get_value() == name
    assert dlginfo['places'][0].get_value() == place
    assert dlginfo['tags'][0].get_value() == tag

def test_add_photo1(initial_db, monkeypatch):
    '''
    use the menubar to make sure we can invoke the add photo dialog
    and create a new photo
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    tree = root.album_tree
    assert tree != None
    assert tree.model != None
    assert root.menuBar() != None
    tree_root = tree.model.invisibleRootItem()
    assert tree_root != None
    album = add_an_album(tree_root)
    tree.add_album(album.get_name(), album.get_dated(), album.get_notes())

    name  = random_string(tree_root)
    path  = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

    dlginfo = {}
    dlginfo['photo'] = name 
    dlginfo['album_id'] = album.get_id()
    dlginfo['path'] = path
    dlginfo['dated'] = dated
    dlginfo['notes'] = notes
    dlginfo['names'] = []
    dlginfo['places'] = []
    dlginfo['tags'] = []
    monkeypatch.setattr(PlornPhotoDialog, 'ask',
                        lambda *args: dlginfo)
    new_action = root.findChild(QAction, 'new_photo_action')
    assert new_action != None
    new_action.trigger()

    photo = PlornDbOperations.get_photo_by_album_and_path(album.get_id(), path)
    assert photo != None
    assert photo.get_name() == name
    assert photo.get_path() == path
    assert photo.get_dated() == dated
    assert photo.get_notes() == notes
    assert len(photo.get_name_list()) < 1
    assert len(photo.get_place_list()) < 1
    assert len(photo.get_tag_list()) < 1

def test_add_photo2(initial_db, monkeypatch):
    '''
    use the menubar to make sure we can invoke the add photo dialog
    and create a new photo but this time with attributes, too
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    tree = root.album_tree
    assert tree != None
    assert tree.model != None
    assert root.menuBar() != None
    tree_root = tree.model.invisibleRootItem()
    assert tree_root != None
    album = add_an_album(tree_root)
    tree.add_album(album.get_name(), album.get_dated(), album.get_notes())

    photo_name  = random_string(tree_root)
    path  = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)
    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)

    dlginfo = {}
    dlginfo['photo'] = photo_name 
    dlginfo['album_id'] = album.get_id()
    dlginfo['path'] = path
    dlginfo['dated'] = dated
    dlginfo['notes'] = notes
    dlginfo['names'] = [name_attr]
    dlginfo['places'] = [place_attr]
    dlginfo['tags'] = [tag_attr]
    monkeypatch.setattr(PlornPhotoDialog, 'ask',
                        lambda *args: dlginfo)
    new_action = root.findChild(QAction, 'new_photo_action')
    assert new_action != None
    new_action.trigger()

    photo = PlornDbOperations.get_photo_by_album_and_path(album.get_id(), path)
    assert photo != None
    assert photo.get_name() == photo_name
    assert photo.get_path() == path
    assert photo.get_dated() == dated
    assert photo.get_notes() == notes
    assert len(photo.get_name_list()) > 0
    assert photo.get_name_list()[0].get_value() == name
    assert len(photo.get_place_list()) > 0
    assert photo.get_place_list()[0].get_value() == place
    assert len(photo.get_tag_list()) > 0
    assert photo.get_tag_list()[0].get_value() == tag

#def test_remove_album1(initial_db, monkeypatch):
#    '''
#    use the menubar directly to remove an album with at least
#    one attribute of each type; we're really just testing the 
#    removal function
#    '''
#    info = initial_db
#    monkeypatch.setenv('HOME', info['homedir'])
#    root = info['root']
#    assert root.menuBar() != None
#    tree = root.album_tree
#    assert tree != None
#    row_count = tree.model.rowCount()
#
#    #-- add an album directly to the db
#    tree_root = tree.model.invisibleRootItem()
#    album = random_string(tree_root)
#    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
#    notes = random_string(tree_root)
#    album = PlornAlbum(album, id=None, dated=dated, notes=notes)
#
#    name = random_string(tree_root)
#    name_attr = PlornName(name)
#    name_attr = PlornDbOperations.add_name(name_attr)
#    assert name_attr.get_id() != 0
#    album.set_name_list([name_attr])
#
#    place = random_string(tree_root)
#    place_attr = PlornPlace(place)
#    place_attr = PlornDbOperations.add_place(place_attr)
#    assert place_attr.get_id() != 0
#    album.set_place_list([place_attr])
#
#    tag = random_string(tree_root)
#    tag_attr = PlornTag(tag)
#    tag_attr = PlornDbOperations.add_tag(tag_attr)
#    assert tag_attr.get_id() != 0
#    album.set_tag_list([tag_attr])
#
#    res = PlornAlbumModel.add_album(tree_root, album, db=info['db'])
#    assert res, 'album did not get added'
#    assert album.get_id() != 0
#
#    #-- make sure the album is in the view
#    items = tree.model.findItems(album.get_name(), column=2)
#    assert len(items) > 0
#    row_count = tree.model.rowCount()
#
#    #-- select the album and remove it
#    id_item = tree_root.child(0, 0)
#    id_index = id_item.index()
#    id = int(id_item.text())
#    name_item = tree_root.child(0, 2)
#    name_index = name_item.index()
#    name = name_item.text()
#    indices = [id_index, name_index]
#    monkeypatch.setattr(PlornCatalogView,'selected_rows',lambda *args: indices)
#
#    monkeypatch.setattr(QMessageBox,'question',
#                        lambda *args: QMessageBox.StandardButton.Yes)
#    root.remove_album()
#    assert tree.model.rowCount() + 1 == row_count
#    album = PlornDbOperations.get_album_by_id(id)
#    assert album == None
#    album = PlornDbOperations.get_album_by_name(name)
#    assert album == None
#    names = PlornDbOperations.get_names_for_album_by_id(id)
#    assert len(names) <= 0
#    places = PlornDbOperations.get_places_for_album_by_id(id)
#    assert len(places) <= 0
#    tags = PlornDbOperations.get_tags_for_album_by_id(id)
#    assert len(tags) <= 0
#
#def test_update_album1(initial_db, monkeypatch):
#    '''
#    use the menubar to make sure we can invoke the update album dialog
#    and modify an album with attributes
#    '''
#    info = initial_db
#    monkeypatch.setenv('HOME', info['homedir'])
#    root = info['root']
#    tree = root.album_tree
#    assert tree != None
#    assert root.menuBar() != None
#    tree_root = tree.model.invisibleRootItem()
#    assert tree_root != None
#
#    #-- create an album with attributes
#    album_name  = random_string(tree_root)
#    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
#    notes = random_string(tree_root)
#    count = 42
#    name = random_string(tree_root)
#    name_attr = PlornName(name)
#    name_attr = PlornDbOperations.add_name(name_attr)
#    place = random_string(tree_root)
#    place_attr = PlornPlace(place)
#    place_attr = PlornDbOperations.add_place(place_attr)
#    tag = random_string(tree_root)
#    tag_attr = PlornTag(tag)
#    tag_attr = PlornDbOperations.add_tag(tag_attr)
#    album = PlornAlbum(album_name, id=None,
#                       dated=dated, notes=notes, photo_count=count,
#                       names=[name_attr], places=[place_attr], tags=[tag_attr])
#    album = PlornDbOperations.add_album(album)
#    assert album != None
#    album_id = album.get_id()
#    assert album_id != 0
#    assert album.get_name() == album_name
#    assert album.get_dated() == dated
#    assert album.get_notes() == notes
#    assert album.get_photo_count() == count
#    assert len(album.get_name_list()) > 0
#    assert len(album.get_place_list()) > 0
#    assert len(album.get_tag_list()) > 0
#
#    #-- invoke the edit dialog, change some things and save them
#    dlg = PlornAlbumDialog(tree=tree, title='Edit Album', allow_edit=True,
#                           select_album=False)
#    dlg.set_inputs(album_id)
#    assert dlg.name_edit.text() == album_name
#    assert dlg.dated_edit.text() == dated
#    assert dlg.notes_edit.toPlainText() == notes
#
#    new_dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
#    new_notes = random_string(tree_root)
#    dlg.dated_edit.setText(new_dated)
#    dlg.notes_edit.setPlainText(new_notes)
#    assert dlg.dated_edit.text() == new_dated
#    assert dlg.notes_edit.toPlainText() == new_notes
#
#    bbox = dlg.findChild(QDialogButtonBox, 'album_dlg_bbox')
#    assert bbox != None
#
#    info = dlg.get_inputs()
#    assert len(info) > 0
#
#    updated_album = PlornDbOperations.get_album_by_id(album_id)
#    assert updated_album != None
#    assert updated_album.get_id() == album_id, 'album_id is wrong'
#    assert updated_album.get_name() == album_name, 'album_name is wrong'
#    assert updated_album.get_dated() == dated, 'dated is wrong'
#    assert updated_album.get_notes() == notes, 'notes are wrong'
#    assert updated_album.get_photo_count() == count, 'count is wrong'
#
