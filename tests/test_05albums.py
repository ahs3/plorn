
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


####################################################################
#
#   test album operations
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

def test_add_album1(initial_db, monkeypatch):
    '''
    use the dialog directly to add a simple album with no attributes;
    we're really just testing the dialog itself
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    assert tree.model.rowCount() == 0

    dlg = PlornAlbumDialog(tree=tree, select_album=True)
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

    dlg.album_selection.setCurrentIndex(1)
    dlg.name_edit.setText(album)
    dlg.dated_edit.setText(dated)
    dlg.notes_edit.insertPlainText(notes)

    dlginfo = dlg.get_inputs()
    assert album == dlginfo['album']
    assert dated == dlginfo['dated']
    assert notes == dlginfo['notes']

def test_add_album2(initial_db, monkeypatch):
    '''
    use the dialog directly to add a simple album with at least
    one attribute of each type; we're really just testing the 
    dialog itself
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    assert tree.model.rowCount() == 0

    dlg = PlornAlbumDialog(tree=tree, select_album=True)
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

    dlg.album_selection.setCurrentIndex(1)
    dlg.name_edit.setText(album)
    dlg.dated_edit.setText(dated)
    dlg.notes_edit.insertPlainText(notes)

    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    assert name_attr.get_id() != 0
    item = QStandardItem(name)
    item.setData([name_attr.get_id(), name_attr.get_parent_id(),
                  name_attr.get_value()])
    dlg.name_list.appendRow(item)
    assert dlg.name_list.rowCount() > 0

    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    assert place_attr.get_id() != 0
    item = QStandardItem(place)
    item.setData([place_attr.get_id(), place_attr.get_parent_id(),
                  place_attr.get_value()])
    dlg.place_list.appendRow(item)
    assert dlg.place_list.rowCount() > 0

    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)
    assert tag_attr.get_id() != 0
    item = QStandardItem(tag)
    item.setData([tag_attr.get_id(), tag_attr.get_parent_id(),
                  tag_attr.get_value()])
    dlg.tag_list.appendRow(item)
    assert dlg.tag_list.rowCount() > 0

    dlginfo = dlg.get_inputs()
    assert album  == dlginfo['album']
    assert dated  == dlginfo['dated']
    assert notes  == dlginfo['notes']
    found = False
    for ii in dlginfo['names']:
        if ii.get_value() == name:
            found = True
            break
    assert found, 'name list is not correct'
    found = False
    for ii in dlginfo['places']:
        if ii.get_value() == place:
            found = True
            break
    assert found, 'place list is not correct'
    for ii in dlginfo['tags']:
        if ii.get_value() == tag:
            found = True
            break
    assert found, 'tags list is not correct'

def test_add_album3(initial_db, monkeypatch):
    '''
    use the menubar to make sure we can invoke the add album dialog
    and create a new album
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    tree = root.album_tree
    assert tree != None
    assert tree.model.rowCount() == 0
    assert root.menuBar() != None
    tree_root = tree.model.invisibleRootItem()
    assert tree_root != None

    name  = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

    dlginfo = {}
    dlginfo['album'] = name 
    dlginfo['dated'] = dated
    dlginfo['notes'] = notes
    dlginfo['names'] = []
    dlginfo['places'] = []
    dlginfo['tags'] = []
    monkeypatch.setattr(PlornAlbumDialog, 'ask',
                        lambda *args: dlginfo)
    new_action = root.findChild(QAction, 'new_album_action')
    assert new_action != None
    new_action.trigger()

    album = PlornDbOperations.get_album_by_name(name)
    assert album != None
    assert album.get_name() == name
    assert album.get_dated() == dated
    assert album.get_notes() == notes

def test_add_album4(initial_db, monkeypatch):
    '''
    use the menubar to make sure we can invoke the add album dialog
    and create a new album but this time with attributes, too
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    tree = root.album_tree
    assert tree != None
    row_count = tree.model.rowCount()
    assert root.menuBar() != None
    tree_root = tree.model.invisibleRootItem()
    assert tree_root != None

    album_name  = random_string(tree_root)
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
    dlginfo['album'] = album_name 
    dlginfo['dated'] = dated
    dlginfo['notes'] = notes
    dlginfo['names'] = [name_attr]
    dlginfo['places'] = [place_attr]
    dlginfo['tags'] = [tag_attr]
    monkeypatch.setattr(PlornAlbumDialog, 'ask',
                        lambda *args: dlginfo)
    new_action = root.findChild(QAction, 'new_album_action')
    assert new_action != None
    new_action.trigger()

    all_names = PlornDbOperations.get_all_attrs(table_name='names')
    all_places = PlornDbOperations.get_all_attrs(table_name='places')
    all_tags = PlornDbOperations.get_all_attrs(table_name='tags')
    album = PlornDbOperations.get_album_by_name(album_name)

    assert album != None
    assert album.get_name() == album_name
    assert album.get_dated() == dated
    assert album.get_notes() == notes
    assert len(album.get_name_list()) > 0
    assert len(album.get_place_list()) > 0
    assert len(album.get_tag_list()) > 0
    assert row_count+1 == tree.model.rowCount()

def test_remove_album1(initial_db, monkeypatch):
    '''
    use the menubar directly to remove an album with at least
    one attribute of each type; we're really just testing the 
    removal function
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    row_count = tree.model.rowCount()

    #-- add an album directly to the db
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)
    album = PlornAlbum(album, id=None, dated=dated, notes=notes)

    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    assert name_attr.get_id() != 0
    album.set_name_list([name_attr])

    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    assert place_attr.get_id() != 0
    album.set_place_list([place_attr])

    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)
    assert tag_attr.get_id() != 0
    album.set_tag_list([tag_attr])

    res = PlornAlbumModel.add_album(tree_root, album, db=info['db'])
    assert res, 'album did not get added'
    assert album.get_id() != 0

    #-- make sure the album is in the view
    items = tree.model.findItems(album.get_name(), column=2)
    assert len(items) > 0
    row_count = tree.model.rowCount()

    #-- select the album and remove it
    id_item = tree_root.child(0, 0)
    id_index = id_item.index()
    id = int(id_item.text())
    name_item = tree_root.child(0, 2)
    name_index = name_item.index()
    name = name_item.text()
    indices = [id_index, name_index]
    monkeypatch.setattr(PlornCatalogView,'selected_rows',lambda *args: indices)

    monkeypatch.setattr(QMessageBox,'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    root.remove_album()
    assert tree.model.rowCount() + 1 == row_count
    album = PlornDbOperations.get_album_by_id(id)
    assert album == None
    album = PlornDbOperations.get_album_by_name(name)
    assert album == None
    names = PlornDbOperations.get_names_for_album_by_id(id)
    assert len(names) <= 0
    places = PlornDbOperations.get_places_for_album_by_id(id)
    assert len(places) <= 0
    tags = PlornDbOperations.get_tags_for_album_by_id(id)
    assert len(tags) <= 0

def test_view_album1(initial_db, monkeypatch):
    '''
    we're really just testing the view dialog to make sure it shows
    the right stuff 
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    tree = root.album_tree
    assert tree != None
    row_count = tree.model.rowCount()

    #-- add an album directly to the db
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)
    album = PlornAlbum(album, id=None, dated=dated, notes=notes)

    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    assert name_attr.get_id() != 0
    album.set_name_list([name_attr])

    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    assert place_attr.get_id() != 0
    album.set_place_list([place_attr])

    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)
    assert tag_attr.get_id() != 0
    album.set_tag_list([tag_attr])

    res = PlornAlbumModel.add_album(tree_root, album, db=info['db'])
    assert res, 'album did not get added'
    assert album.get_id() != 0

    #-- make sure the album is in the view
    items = tree.model.findItems(album.get_name(), column=2)
    assert len(items) > 0

    dlg = PlornAlbumDialog(tree=tree, title='View Album', allow_edit=False,
                           select_album=False)
    dlg.set_inputs(album.get_id())
    assert album.get_name() == dlg.name_edit.text()
    assert album.get_dated() == dlg.dated_edit.text()
    assert album.get_notes() == dlg.notes_edit.toPlainText()

def test_update_album1(initial_db, monkeypatch):
    '''
    use the menubar to make sure we can invoke the update album dialog
    and modify an album with attributes
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    tree = root.album_tree
    assert tree != None
    assert root.menuBar() != None
    tree_root = tree.model.invisibleRootItem()
    assert tree_root != None

    #-- create an album with attributes
    album_name  = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)
    count = 42
    name = random_string(tree_root)
    name_attr = PlornName(name)
    name_attr = PlornDbOperations.add_name(name_attr)
    place = random_string(tree_root)
    place_attr = PlornPlace(place)
    place_attr = PlornDbOperations.add_place(place_attr)
    tag = random_string(tree_root)
    tag_attr = PlornTag(tag)
    tag_attr = PlornDbOperations.add_tag(tag_attr)
    album = PlornAlbum(album_name, id=None,
                       dated=dated, notes=notes, photo_count=count,
                       names=[name_attr], places=[place_attr], tags=[tag_attr])
    album = PlornDbOperations.add_album(album)
    assert album != None
    album_id = album.get_id()
    assert album_id != 0
    assert album.get_name() == album_name
    assert album.get_dated() == dated
    assert album.get_notes() == notes
    assert album.get_photo_count() == count
    assert len(album.get_name_list()) > 0
    assert len(album.get_place_list()) > 0
    assert len(album.get_tag_list()) > 0

    #-- invoke the edit dialog, change some things and save them
    dlg = PlornAlbumDialog(tree=tree, title='Edit Album', allow_edit=True,
                           select_album=False)
    dlg.set_inputs(album_id)
    assert dlg.name_edit.text() == album_name
    assert dlg.dated_edit.text() == dated
    assert dlg.notes_edit.toPlainText() == notes

    new_dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    new_notes = random_string(tree_root)
    dlg.dated_edit.setText(new_dated)
    dlg.notes_edit.setPlainText(new_notes)
    assert dlg.dated_edit.text() == new_dated
    assert dlg.notes_edit.toPlainText() == new_notes

    bbox = dlg.findChild(QDialogButtonBox, 'album_dlg_bbox')
    assert bbox != None

    info = dlg.get_inputs()
    assert len(info) > 0

    updated_album = PlornDbOperations.get_album_by_id(album_id)
    assert updated_album != None
    assert updated_album.get_id() == album_id, 'album_id is wrong'
    assert updated_album.get_name() == album_name, 'album_name is wrong'
    assert updated_album.get_dated() == dated, 'dated is wrong'
    assert updated_album.get_notes() == notes, 'notes are wrong'
    assert updated_album.get_photo_count() == count, 'count is wrong'

