
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

from plorn.model import (
    PlornAlbumModel,
    PlornAttrModel,
    PlornDbOperations,
)

from plorn.widgets import (
    PlornAttrView,
    PlornCatalogView,
)

from plorn.widgets.albums import (
    PlornAlbumDialog,
    PlornViewAlbumDialog,
)


####################################################################
#
#   basic main window tests
#
def test_left_header(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.left_header != None
    assert root.left_header.text() == '***plorn: catalog photos***'

def test_mid_header(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.mid_header != None
    assert root.mid_header.text() == ''

def test_right_header(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.right_header != None
    config = PlornConfig()
    msg = f'***version {config.get_version()}***'
    assert root.right_header.text() == msg

def test_clean_album_view(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.album_tree != None

def test_statusbar(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.statusBar() != None
    msg = root.statusBar().currentMessage()
    assert msg != ''
    assert msg[:len('ready')] == 'ready'
    config = PlornConfig()
    config.set_current_catalog('Plorn')
    config.write_config()

    catalog, datadir, dbname = config.get_current_catalog()
    assert root.catname.text() == f'database: {dbname}'
    db = root.get_db()
    albums = root.album_tree.model.rowCount()
    asuf = 's'
    if albums == 1:
        asuf = ''
    assert root.sbcounts != None
    expected = f'{albums} album{asuf}, '
    assert str(root.sbcounts.text()).find(expected) >= 0

def test_menubar(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = [action.text() for action in root.menuBar().actions() 
             if action.menu()]
    for ii in ['Catalogs', 'Albums', 'Photos', 'Tools', 'Help']:
        assert f'&{ii}' in menus

def menu_list(w):
    mlist = []
    for action in w.actions():
        if action.menu():
            mlist.append(action.text())
    return mlist

def action_list(w):
    alist = []
    for action in w.actions():
        alist.append(action.text())
    return alist

def test_catalogs_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Catalogs' in menus
    assert root.catalogs_menu != None
    actions = action_list(root.catalogs_menu)
    assert '&New' in actions
    assert '&Open' in actions
    assert '&Delete' in actions
    assert 'Quit' in actions

def test_catalog_new1(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newcat = root.findChild(QAction, 'new_catalog_action')
    assert newcat != None

    monkeypatch.setattr(
        PlornNewCatalogDialog, 'ask', 
        classmethod(lambda *args: dlg.get_inputs()))
    dlg = PlornNewCatalogDialog()
    assert dlg != None
    catinfo = dlg.ask(info['root'])
    assert dlg.ask() != None
    assert catinfo['catalog'] == ''
    assert catinfo['datadir'] == None or len(catinfo['datadir']) > 0
    assert catinfo['dbname'] == ''
    assert catinfo['make_current'] == True
    assert catinfo['make_default'] == False
    dlg.close()

def test_catalog_new2(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newcat = root.findChild(QAction, 'new_catalog_action')
    assert newcat != None

    monkeypatch.setattr(
        PlornNewCatalogDialog, 'ask', classmethod(lambda *args: True))
    dlg = PlornNewCatalogDialog()
    assert dlg != None
    dlg.name_edit.setText('Wilma')
    dlg.ddir_edit.setText('/tmp/wilma')
    dlg.dbname_edit.setText('wilma.catalog')
    dlg.make_current.setChecked(False)
    dlg.make_default.setChecked(True)
    assert dlg.ask() == True
    catinfo = dlg.get_inputs()
    assert catinfo['catalog'] == 'Wilma' and catinfo['catalog'] != None
    assert catinfo['datadir'] == '/tmp/wilma' and catinfo['datadir'] != None
    assert catinfo['dbname'] == 'wilma.catalog' and catinfo['dbname'] != None
    assert catinfo['make_current'] == False
    assert catinfo['make_default'] == True

def test_catalog_new3(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newcat = root.findChild(QAction, 'new_catalog_action')
    assert newcat != None

    monkeypatch.setattr(
        PlornNewCatalogDialog, 'ask', classmethod(lambda *args: True))
    dlg = PlornNewCatalogDialog()
    assert dlg != None
    dlg.name_edit.setText('Wilma')
    dlg.ddir_edit.setText('/tmp/wilma')
    dlg.dbname_edit.setText('wilma.catalog')
    assert dlg.ask() == True
    catinfo = dlg.get_inputs()
    config = PlornConfig()
    config.set_catalog(name=catinfo['catalog'],
                       datadir=catinfo['datadir'],
                       dbname=catinfo['dbname'])
    config.write_config()

    c, d, db = config.get_catalog('Wilma')
    assert c == 'Wilma'
    assert d == '/tmp/wilma'
    assert db == 'wilma.catalog'

def test_catalog_quit(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Catalogs' in menus
    quit_item = root.findChild(QAction, 'quit_action')
    assert quit_item != None

def test_attrs_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Attrbutes' in menus
    assert root.attrs_menu != None
    actions = action_list(root.attrs_menu)
    assert '&Names' in actions
    assert '&Places' in actions
    assert '&Tags' in actions

def test_tools_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Tools' in menus
    assert root.catalogs_menu != None
    actions = action_list(root.tools_menu)
    assert 'Preferences' in actions

def test_help_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Help' in menus
    assert root.catalogs_menu != None
    actions = action_list(root.help_menu)
    assert 'Help' in actions
    assert 'About' in actions

def test_about_window(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    about = root.findChild(QAction, 'about_action')
    assert about != None

    monkeypatch.setattr(
        PlornAboutDialog, 'ask', classmethod(lambda *args: True))
    mbox = PlornAboutDialog()
    assert mbox.ask() == True


####################################################################
#
#   test catalog operations
#
def test_catalog_new(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newcat = root.findChild(QAction, 'new_catalog_action')
    assert newcat != None

    #-- create a new catalog
    monkeypatch.setattr(
        PlornNewCatalogDialog, 'ask', classmethod(lambda *args: True))
    dlg = PlornNewCatalogDialog()
    assert dlg != None
    dlg.name_edit.setText('Wilma')
    dlg.ddir_edit.setText('')
    dlg.dbname_edit.setText('wilma.catalog')
    dlg.make_current.setChecked(False)
    dlg.make_default.setChecked(False)
    assert dlg.ask() == True
    catinfo = dlg.get_inputs()
    config = PlornConfig()
    config.set_catalog(name=catinfo['catalog'],
                       datadir=catinfo['datadir'],
                       dbname=catinfo['dbname'])
    config.write_config()

    #-- and was the catalog saved propery?
    c, d, db = config.get_catalog('Wilma')
    assert c == 'Wilma'
    assert d == config.get_datadir()
    assert db == 'wilma.catalog'

    c, d, db = config.get_current_catalog()
    assert c != 'Wilma'
    assert d == config.get_datadir()
    assert db != 'wilma.catalog'

    c, d, db = config.get_default_catalog()
    assert c != 'Wilma'
    assert d == config.get_datadir()
    assert db != 'wilma.catalog'

def test_catalog_switch_to_new(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newcat = root.findChild(QAction, 'new_catalog_action')
    assert newcat != None

    #-- add an album
    config = PlornConfig()
    catalog, dirpath, dbname = config.get_current_catalog()
    assert catalog == 'Plorn'

    db = info['db']
    assert db.isOpen() and db.isValid()
    if root.album_tree.model.rowCount() < 2:
        album1 = PlornAlbum('bogus album', id=None, dated='now', notes='nada')
        album2 = PlornAlbum('another one', id=None, dated='later', notes='med')
        tree_root = root.album_tree.model.invisibleRootItem()
        res = PlornAlbumModel.add_album(tree_root, album1, db=db)
        assert res == 'okay'
        res = PlornAlbumModel.add_album(tree_root, album2, db=db)
        assert res == 'okay'
    assert root.album_tree.model.rowCount() >= 2

    #-- create a new catalog
    monkeypatch.setattr(
        PlornNewCatalogDialog, 'ask',
        classmethod(lambda *args: {'catalog': 'Wilma',
                                   'datadir': '~/.local/share/plorn',
                                   'dbname': 'wilma.catalog',
                                   'make_current': True,
                                   'make_default': False,
                                  }
        )
    )
    root.new_catalog_action()
    config = PlornConfig()

    #-- was the catalog saved propery?
    c, d, db = config.get_current_catalog()
    assert c == 'Wilma'
    assert d == config.get_datadir()
    assert db == 'wilma.catalog'

    #-- was the db switched to the new current?
    assert root.db.connectionName() == 'Wilma'
    assert root.album_tree.model.rowCount() == 0

def test_catalog_switching(initial_db, monkeypatch):
    '''
    this test assumes the previous catalog tests have been executed and passed
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    opencat = root.open_catalog_menu
    assert opencat != None
    opencat.show()

    #-- which catalog are we using?
    db = info['db']
    assert db.isOpen() and db.isValid()
    first_album_count = root.album_tree.model.rowCount()
    config = PlornConfig()
    catalog, dirpath, dbname = config.get_current_catalog()
    for action in opencat.actions():
        if action.text() == 'Wilma' and catalog == 'Wilma':
            assert action.isChecked()
        elif action.text() == 'Plorn' and catalog == 'Plorn':
            assert action.isChecked()
        else:
            assert action.isChecked() == False

    switch_to = None
    if catalog != 'Plorn':
        switch_to = 'Plorn'
    elif catalog == 'Plorn':
        switch_to = 'Wilma'
    if switch_to:
        config.set_current_catalog(switch_to)
        config.write_config()
        root.album_tree.switch_model()
    new_count = root.album_tree.model.rowCount()
    assert new_count == 0

def test_catalog_deletion(initial_db, monkeypatch):
    '''
    this test assumes the previous catalog tests have been executed and passed
    '''
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    qtbot = info['qtbot']
    assert root.menuBar() != None
    delcat = root.delete_catalog_menu
    assert delcat != None

    #-- which catalog are we using?
    config = PlornConfig()
    c, d, d = config.get_catalog('Wilma')
    assert c == 'Wilma'
    catalog, dirpath, dbname = config.get_current_catalog()
    assert catalog != c
    assert 'Wilma' in config.get_catalog_list()

    monkeypatch.setattr(QMessageBox, 'exec',
                        lambda *args: QMessageBox.StandardButton.Yes)
    del_action = None
    root.update_removable_catalogs()
    qtbot.mouseClick(delcat, Qt.MouseButton.LeftButton)
    assert len(delcat.actions()) > 0
    for action in delcat.actions():
        if action.text() == catalog:
            assert False, 'current catalog name should not be in menu'
        else:
            assert action.isChecked() == False
            del_action = action

    assert del_action != None
    remove_cat = del_action.text()
    del_action.trigger()
    config.remove_catalog(remove_cat)
    catalog, dirpath, dbname = config.get_catalog('Wilma')
    assert catalog == None
    assert dirpath == None
    assert dbname == None
    catalog, dirpath, dbname = config.get_current_catalog()
    assert catalog == 'Plorn'


####################################################################
#
#   test attribute operations
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

def test_new_name_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='Names', table='names', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

def test_new_child_name_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='Names', table='names', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)
    assert tree_root.hasChildren()

    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: ('Barney', True))
    name = random_string(tree_root)
    found = search_attr_tree(tree_root, 'Barney')
    assert not found
    node = tree_root.child(1)
    dlg.add_attr_child(node)
    found = search_attr_tree(tree_root, 'Barney')
    assert found
    assert isValueInDb(info['db'], 'names', 'Barney')

def test_remove_name_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='Names', table='names', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'names', name)

def test_remove_child_name_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='Names', table='names', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_child(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'names', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'names', name)

def test_new_place_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='places', table='places', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

def test_new_child_place_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='places', table='places', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)
    assert tree_root.hasChildren()

    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: ('Barney', True))
    name = random_string(tree_root)
    found = search_attr_tree(tree_root, 'Barney')
    assert not found
    node = tree_root.child(1)
    dlg.add_attr_child(node)
    found = search_attr_tree(tree_root, 'Barney')
    assert found
    assert isValueInDb(info['db'], 'places', 'Barney')

def test_remove_place_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='places', table='places', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'places', name)

def test_remove_child_place_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='places', table='places', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_child(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'places', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'places', name)

def test_new_tag_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='tags', table='tags', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

def test_new_child_tag_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='tags', table='tags', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)
    assert tree_root.hasChildren()

    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: ('Barney', True))
    name = random_string(tree_root)
    found = search_attr_tree(tree_root, 'Barney')
    assert not found
    node = tree_root.child(1)
    dlg.add_attr_child(node)
    found = search_attr_tree(tree_root, 'Barney')
    assert found
    assert isValueInDb(info['db'], 'tags', 'Barney')

def test_remove_tag_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='tags', table='tags', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'tags', name)

def test_remove_child_tag_attr(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    newattr = root.attrs_menu
    assert newattr != None

    #-- create a new name
    dlg = PlornAttrView(title='tags', table='tags', db=info['db'])
    tree_root = dlg.tree.model().invisibleRootItem()
    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    assert dlg != None
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_sib(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    name = random_string(tree_root)
    monkeypatch.setattr(QInputDialog, 'getText', lambda *args: (name, True))
    found = search_attr_tree(tree_root, name)
    assert not found
    dlg.add_attr_child(tree_root)
    found = search_attr_tree(tree_root, name)
    assert found
    assert isValueInDb(info['db'], 'tags', name)

    monkeypatch.setattr(QMessageBox, 'question',
                        lambda *args: QMessageBox.StandardButton.Yes)
    item = tree_root.child(1)
    assert item != None
    name = item.text()
    res = dlg.remove_attr(item)
    found = search_attr_tree(tree_root, name)
    assert not found
    assert not isValueInDb(info['db'], 'tags', name)

####################################################################
#
#   test album operations
#
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

    dlg = PlornAlbumDialog(tree=tree)
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

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

    dlg = PlornAlbumDialog(tree=tree)
    tree_root = tree.model.invisibleRootItem()
    album = random_string(tree_root)
    dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    notes = random_string(tree_root)

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

    #album = PlornDbOperations.add_album(album)
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

    dlg = PlornViewAlbumDialog(tree=tree, title='View Album', allow_edit=False)
    dlg.set_inputs(album)
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
    dlg = PlornViewAlbumDialog(tree=tree, title='Edit Album', allow_edit=True)
    dlg.set_inputs(album)
    assert dlg.name_edit.text() == album_name
    assert dlg.dated_edit.text() == dated
    assert dlg.notes_edit.toPlainText() == notes
    assert dlg.count.text() == str(count)

    new_dated = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')
    new_notes = random_string(tree_root)
    new_count = 54
    dlg.dated_edit.setText(new_dated)
    dlg.notes_edit.setPlainText(new_notes)
    dlg.count.setText(str(new_count))
    assert dlg.dated_edit.text() == new_dated
    assert dlg.notes_edit.toPlainText() == new_notes
    assert dlg.count.text() == str(new_count)

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

