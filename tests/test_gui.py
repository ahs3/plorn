
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os

from PyQt6.QtGui import (
    QAction,
)
from PyQt6.QtCore import (
    Qt,
)
from PyQt6.QtWidgets import (
    QMessageBox,
)

from plorn import (
    AlbumFields,
    ConfigFields,
    PlornAlbum,
)
from plorn.config import PlornConfig
from plorn.gui import (
    PlornAboutDialog,
    PlornNewCatalogDialog,
    user_interface,
)
from plorn.model import model_add_album


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
        res = model_add_album(tree_root, album1, db=db)
        assert res == 'okay'
        res = model_add_album(tree_root, album2, db=db)
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
#   test album operations
#
