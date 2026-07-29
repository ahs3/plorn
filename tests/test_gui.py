
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

from plorn.config import PlornConfig
from plorn.db import (
    ConfigFields,
    AlbumFields,
)
from plorn.gui import (
    PlornAboutDialog,
    PlornNewCatalogDialog,
    user_interface,
)

#-- test the gui components
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

def test_catalog(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.catalog != None
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
    catalog, datadir, dbname = config.get_current_catalog()
    assert root.catname.text() == f'database: {dbname}'
    db = root.get_db()
    albums = root.album_tree.model().rowCount()
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
    assert dlg.ask() == True
    catinfo = dlg.get_inputs()
    assert catinfo['catalog'] == 'Wilma' and catinfo['catalog'] != None
    assert catinfo['datadir'] == '/tmp/wilma' and catinfo['datadir'] != None
    assert catinfo['dbname'] == 'wilma.catalog' and catinfo['dbname'] != None

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

