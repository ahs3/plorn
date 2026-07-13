
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

from plorn.gui import user_interface

@pytest.fixture(scope='module')
def qtbot_session(qapp, request):
    print('=> setting up qtbot')
    result = QtBot(qapp)
    with capture_exceptions() as exceptions:
        yield result
    print('=> tearing down qtbot')

@pytest.fixture(scope='module')
def GUI():
    print('=> setting up GUI')
    app, root = user_interface()
    qtbotbis = QtBot(app)
    QtTest.QTest.qWait(2)

    return app, root, qtbotbis

def test_main(GUI):
    app, root, qtbot = GUI
    assert app != None
    assert root != None

