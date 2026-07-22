
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os

from PyQt6.QtGui import (
    QAction,
)

from plorn.config import PlornConfig
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
    assert root.tree != None
    assert root.tree_data != None
    assert root.expand_all != None
    assert root.expand_all.isEnabled() == False
    assert root.collapse_all != None
    assert root.collapse_all.isEnabled() == True

def test_catalog_headers(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.catalog != None
    assert root.tree != None
    item = root.tree.headerItem()
    assert item.text(0) == 'Name'
    assert item.text(1) == 'Photos'
    assert item.text(2) == 'Type'
    assert item.text(3) == 'ID'

def test_statusbar(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.statusBar() != None
    msg = root.statusBar().currentMessage()
    assert msg != ''
    assert msg[:8] == 'catalog:'
    config = PlornConfig()
    catalog, datadir, dbname = config.get_current_catalog()
    assert msg == f'catalog: {catalog}'
    db = info['root'].get_db()
    albums = db.album_count()
    photos = db.photo_count()
    asuf = 's'
    if albums == 1:
        asuf = ''
    psuf = 's'
    if photos == 1:
        psuf = ''
    assert root.sbcounts != None
    assert root.sbcounts.text() == f'{albums} album{asuf}, {photos} photo{psuf}'

def test_menubar(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = [action.text() for action in root.menuBar().actions() 
             if action.menu()]
    assert '&Catalogs' in menus
    assert '&Edit' in menus
    assert '&Help' in menus

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

def test_catalog_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Catalogs' in menus
    assert root.catalog_menu != None
    actions = action_list(root.catalog_menu)
    assert 'New' in actions
    assert 'Open' in actions
    assert 'Close' in actions
    assert 'Quit' in actions

def test_catalog_new1(initial_db, monkeypatch):
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
    assert dlg.ask() == True
    catalog, datadir, dbname = dlg.get_inputs()
    assert catalog == ''
    assert datadir == None or len(datadir) > 0
    assert dbname == ''
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
    catalog, datadir, dbname = dlg.get_inputs()
    assert catalog == 'Wilma' and catalog != None
    assert datadir == '/tmp/wilma' and datadir != None
    assert dbname == 'wilma.catalog' and dbname != None

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
    catalog, datadir, dbname = dlg.get_inputs()
    config = PlornConfig()
    config.set_catalog(name=catalog, datadir=datadir, dbname=dbname)
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

def test_edit_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Edit' in menus
    assert root.catalog_menu != None
    actions = action_list(root.edit_menu)
    assert 'Preferences' in actions

def test_help_menu(initial_db, monkeypatch):
    info = initial_db
    monkeypatch.setenv('HOME', info['homedir'])
    root = info['root']
    assert root.menuBar() != None
    menus = menu_list(root.menuBar())
    assert '&Help' in menus
    assert root.catalog_menu != None
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

