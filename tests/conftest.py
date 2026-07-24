
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
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtWidgets import (
    QLabel,
    QMenu,
)

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

from plorn.config import PlornConfig
from plorn.gui import user_interface

def get_test_cfgname(tmpdir):
    return os.path.join(tmpdir, 'completely_bogus.cfg')

bogus_config_data = [
         '[plorn]',
         'user = fred',
         'full_name = Fred Flintstone',
         'config_dir = /tmp/test_plorn_barney',
         'data_dir = /tmp/wilma',
         'default_catalog = Default',
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
         'default_catalog = Default',
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
    #-- ... and let pytest handle the cleanup

@pytest.fixture(scope='session')
def monkeymodule():
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()

@pytest.fixture(scope='session')
def plorn_db_test_env(monkeymodule):
    print('================ plorn_db_test_env =========================')
    tmpdirobj = tempfile.TemporaryDirectory(delete=False)
    tmpdir = tmpdirobj.name
    print(f'==> TEST ENV: {tmpdir}')
    if 'PLORN_CONFIG' in os.environ.keys():
        monkeymodule.delenv('PLORN_CONFIG')
        print(f'=> PLORN_CONFIG: "{os.environ["PLORN_CONFIG"]}"')
    else:
        print('=> PLORN_CONFIG: None')
    if 'HOME' in os.environ.keys():
        monkeymodule.setenv('HOME', str(tmpdir))
        print(f'=> HOME: "{os.environ["HOME"]}"')
    else:
        print('=> HOME: None')

    cfgdir = os.path.join(tmpdir, '.config', 'plorn')
    if not os.path.exists(cfgdir):
        print(f'=> making cfgdir: {cfgdir}')
        os.makedirs(cfgdir)
    datadir = os.path.join(tmpdir, '.local', 'share', 'plorn')
    if not os.path.exists(datadir):
        print(f'=> making datadir: {datadir}')
        os.makedirs(datadir)
    cfgname = os.path.join(cfgdir, 'plorn.cfg')
    if os.path.exists(cfgname):
        os.remove(cfgname)
    dataname = os.path.join(datadir, 'plorn.db')
    if os.path.exists(dataname):
        os.remove(dataname)

    yield tmpdir, cfgdir, datadir

    #-- paranoid cleanup
    # DO NOTHING for now -- still useful for debugging
    #cfgname = os.path.join(cfgdir, 'plorn.cfg')
    #if os.path.exists(cfgname):
    #    os.remove(cfgname)
    #dataname = os.path.join(datadir, 'plorn.db')
    #if os.path.exists(dataname):
    #    os.remove(dataname)
    #if not os.path.exists(cfgdir):
    #    os.remove(cfgdir)
    #if not os.path.exists(datadir):
    #    os.remove(datadir)

@pytest.fixture(scope='session')
def qapp_cls():
    return Plorn

@pytest.fixture
def qtbot_session(qapp, request):
    print('=> setting up qtbot')
    result = QtBot(qapp)
    with capture_exceptions() as exceptions:
        yield result
    print('=> tearing down qtbot')

@pytest.fixture
def GUI(request):
    print('=> setting up GUI')
    app, root = user_interface()
    qtbotbis = QtBot(app)
    QtTest.QTest.qWait(2)

    yield app, root, qtbotbis
    app.closeAllWindows()
    app.exit(0)

@pytest.fixture(scope='session')
def initial_db(plorn_db_test_env, monkeymodule):
    tmpdir, cfgdir, datadir = plorn_db_test_env
    monkeymodule.setenv('HOME', tmpdir)
    dbname = os.path.join(datadir, 'plorn.db')
    if os.path.exists(dbname):
        os.remove(dbname)
    cfgname = os.path.join(cfgdir, 'plorn.cfg')
    if os.path.exists(cfgname):
        os.remove(cfgname)
    info = {}
    info['dbname'] = dbname
    info['homedir'] = tmpdir
    info['cfgdir'] = cfgdir
    info['datadir'] = datadir

    app, root = user_interface()
    qtbotbis = QtBot(app)
    info['db'] = QSqlDatabase.database()
    info['app'] = app
    info['root'] = root
    info['qtbot'] = qtbotbis
    QtTest.QTest.qWait(2)

    yield info
    #info['app'].exit(0)
    #info['db'].close()

