
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

def test_remove_photo1(initial_db, monkeypatch):
    '''
    use the model functions directly to remove a photo with at least
    one attribute of each type; we're really just testing the 
    methods themselves
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

    dlginfo = {}
    dlginfo['album'] = random_string(tree_root)
    dlginfo['dated'] = random_string(tree_root)
    dlginfo['notes'] = random_string(tree_root)
    dlginfo['names'] = []
    dlginfo['places'] = []
    dlginfo['tags'] = []
    monkeypatch.setattr(PlornAlbumDialog, 'ask',
                        lambda *args: dlginfo)
    root.add_album()
    album_index = tree.model.index(0, 0, tree.root_index())
    assert album_index.isValid()
    album_id = int(tree.model.itemFromIndex(album_index).text())

    photo_name  = random_string(tree_root)
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

    dlginfo.clear()
    dlginfo['photo'] = photo_name
    dlginfo['album_id'] = album_id
    dlginfo['path'] = path
    dlginfo['dated'] = dated
    dlginfo['notes'] = notes
    dlginfo['names'] = [name_attr]
    dlginfo['places'] = [place_attr]
    dlginfo['tags'] = [tag_attr]
    monkeypatch.setattr(PlornPhotoDialog, 'ask',
                        lambda *args: dlginfo)
    root.add_photo()
    pindex = tree.model.index(0, 0, album_index)
    assert pindex.isValid()
    tree.set_current_index(pindex)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    root.remove_photo()
    pindex = tree.model.index(0, 0, album_index)
    assert not pindex.isValid()

    photo = PlornDbOperations.get_photo_by_album_and_path(album_id, path)
    assert photo == None

