
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import getpass
import os
import pwd
import shutil
import sys
import tempfile

import pytest
from pytestqt.plugin import QtBot

from PyQt6 import QtTest

from PyQt6.QtWidgets import (
    QLabel,
    QMenu,
)

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

from plorn.config import PlornConfig
from plorn.db import PlornDb
from plorn.gui import user_interface

def get_test_cfgname():
    path = os.path.expanduser(TMPDIR)
    return os.path.join(path, 'completely_bogus.cfg')

def get_test_dbname():
    dbpath = os.path.expanduser(TMPDIR)
    return os.path.join(dbpath, 'completely_bogus.db')

bogus_config_data = [
         '[plorn]',
         'user = fred',
         'full_name = Fred Flintstone',
         'config_dir = /tmp/test_plorn_barney',
         'data_dir = /tmp/wilma',
         'current_catalog = Default',
         '',
         '[gui]',
         'default_photo = silly-photo.png',
         '',
         '[Default]',
         'name = Default',
         'dbname = default.catalog',
         '',
         '[Betty]',
         'name = Betty',
         'data_dir = /tmp/betty',
         'dbname = betty.catalog',
]

default_config_data = [
         '[plorn]',
         'user = fred',
         'full_name = Fred Flintstone',
         'config_dir = TMP_CFG_DIR',
         'data_dir = TMP_DATA_DIR',
         'current_catalog = Default',
         '',
         '[gui]',
         'default_photo = silly-photo.png',
         '',
         '[Default]',
         'name = Default',
         'dbname = default.catalog',
         '',
         '[Betty]',
         'name = Betty',
         'data_dir = /tmp/betty',
         'dbname = betty.catalog',
]
def write_test_config(path, data):
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'w') as cfg:
        for ii in data:
            cfg.write(ii + '\n')
        cfg.close()
 
@pytest.fixture(scope='function')
def plorn_test_env(tmp_path, monkeypatch):
    print('================ plorn_test_env =========================')
    if 'PLORN_CONFIG' in os.environ.keys():
        monkeypatch.delenv('PLORN_CONFIG')
        print(f'=> PLORN_CONFIG: "{os.environ["PLORN_CONFIG"]}"')
    else:
        print('=> PLORN_CONFIG: None')
    if 'HOME' in os.environ.keys():
        monkeypatch.setenv('HOME', str(tmp_path))
        print(f'=> HOME: "{os.environ["HOME"]}"')
    else:
        print('=> HOME: None')

    cfgdir = os.path.join(tmp_path, '.config', 'plorn')
    if not os.path.exists(cfgdir):
        print(f'=> making cfgdir: {cfgdir}')
        os.makedirs(cfgdir)
    datadir = os.path.join(tmp_path, '.local', 'share', 'plorn')
    if not os.path.exists(datadir):
        print(f'=> making datadir: {datadir}')
        os.makedirs(datadir)
    cfgname = os.path.join(cfgdir, 'plorn.cfg')
    if os.path.exists(cfgname):
        os.remove(cfgname)
    dataname = os.path.join(datadir, 'plorn.db')
    if os.path.exists(dataname):
        os.remove(dataname)

    yield str(tmp_path), cfgdir, datadir

    #-- paranoid cleanup
    cfgdir = os.path.join(tmp_path, '.config', 'plorn')
    if not os.path.exists(cfgdir):
        os.makedirs(cfgdir)
    datadir = os.path.join(tmp_path, '.local', 'share', 'plorn')
    if not os.path.exists(datadir):
        os.makedirs(datadir)
    cfgname = os.path.join(cfgdir, 'plorn.cfg')
    if os.path.exists(cfgname):
        os.remove(cfgname)
    dataname = os.path.join(datadir, 'plorn.db')
    if os.path.exists(dataname):
        os.remove(dataname)

@pytest.fixture(scope='function')
def bogus_config(tmp_path, monkeypatch):
    if not os.path.exists(TMPDIR):
        os.makedirs(TMPDIR)
    path = get_test_cfgname()
    if os.path.exists(path):
        os.remove(path)
    write_test_config(path)
    monkeypatch.setenv('PLORN_CONFIG', path)
    yield path

    #-- always clean up your mess
    if os.path.exists(path):
        os.remove(path)

#@pytest.fixture(scope='session')
@pytest.fixture
def qtbot_session(qapp, request):
    print('=> setting up qtbot')
    result = QtBot(qapp)
    with capture_exceptions() as exceptions:
        yield result
    print('=> tearing down qtbot')

#@pytest.fixture(scope='session')
@pytest.fixture
def GUI(request, plorn_test_env):
    print('=> setting up GUI')
    app, root = user_interface()
    qtbotbis = QtBot(app)
    QtTest.QTest.qWait(2)

    return app, root, qtbotbis

@pytest.fixture
def initial_db(GUI, bogus_config):
    if os.path.exists(get_test_dbname()):
        os.remove(get_test_dbname())
    db = PlornDb(get_test_dbname(), bogus_config)
    yield db

    #-- clean up
    db.close()
    os.remove(get_test_dbname())


