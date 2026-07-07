
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os
import sys

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

import pytest
from pytestqt.plugin import QtBot
from PyQt6 import QtTest
from PyQt6.QtWidgets import (
    QLabel,
    QMenu,
)

from plorn.config import config
from plorn.gui import user_interface

@pytest.fixture(scope='module')
def qtbot_session(qapp, request):
    print('=> setting up qtbot')
    result = QtBot(qapp)
    with capture_exceptions() as exceptions:
        yield result
    print('=> tearing down qtbot')

@pytest.fixture(scope='module')
def GUI(request):
    print('=> setting up GUI')
    app, root = user_interface()
    qtbotbis = QtBot(app)
    QtTest.QTest.qWait(2)

    return app, root, qtbotbis

def test_left_header(GUI):
    app, root, qtbot = GUI
    assert root.left_header != None
    assert root.left_header.text() == '***plorn: catalog photos***'

def test_mid_header(GUI):
    app, root, qtbot = GUI
    assert root.mid_header != None
    assert root.mid_header.text() == ''

def test_right_header(GUI):
    app, root, qtbot = GUI
    assert root.right_header != None
    msg = f'***version {config.get_version()}***'
    assert root.right_header.text() == msg

def test_catalog(GUI):
    app, root, qtbot = GUI
    assert root.catalog != None
    assert root.tree != None
    assert root.tree_data != None
    assert root.expand_all != None
    assert root.expand_all.isEnabled() == False
    assert root.collapse_all != None
    assert root.collapse_all.isEnabled() == True

def test_catalog_headers(GUI):
    app, root, qtbot = GUI
    assert root.catalog != None
    assert root.tree != None
    item = root.tree.headerItem()
    assert item.text(0) == 'Name'
    assert item.text(1) == 'Photos'
    assert item.text(2) == 'Type'
    assert item.text(3) == 'ID'

def test_controls(GUI):
    app, root, qtbot = GUI
    assert root.controls != None

def test_statusbar(GUI):
    app, root, qtbot = GUI
    assert root.statusbar != None
    assert root.statusbar.currentMessage() != 'no album is currently open'

