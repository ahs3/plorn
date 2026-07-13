
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import getpass
import os
import pwd
import sys
import tempfile

import pytest

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

from plorn.config import PlornConfig

def write_test_config(path):
    data = [
             '[plorn]',
             'user = fred',
             'full_name = Fred Flintstone',
             'config_dir = /tmp/barney',
             'data_dir = /tmp/wilma',
             'current_catalog = default',
             '',
             '[gui]',
             'default_photo = silly-photo.png',
             '',
             '[default]',
             'dbname = default.catalog',
             '',
             '[Betty]',
             'data_dir = /tmp/betty',
             'dbname = betty.catalog',
    ]
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'w') as cfg:
        for ii in data:
            cfg.write(ii + '\n')
        cfg.close()
 
@pytest.fixture
def bogus_config():
    tmpdir = tempfile.mkdtemp()
    cfg_file = 'completely_bogus_test.cfg'
    path = os.path.join(tmpdir, cfg_file)
    if os.path.exists(path):
        os.remove(path)
    write_test_config(path)
    yield path

    #-- always clean up your mess
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(tmpdir):
        os.rmdir(tmpdir)

def test_open_new1():
    '''
    Test all defaults for a new default config file
    '''
    fname = os.path.join(os.environ['HOME'], '.config', 'plorn', 'plorn.cfg')
    if os.path.exists(fname):
        os.rename(fname, f'{fname}..TMP')
    cfg = PlornConfig()
    user = getpass.getuser()
    assert cfg.get_username() == user
    fullname = pwd.getpwnam(user).pw_gecos
    assert cfg.get_fullname() == fullname
    cfg_dir = os.path.expanduser('~/.config/plorn')
    assert cfg.get_configdir() == cfg_dir
    data_dir = os.path.expanduser('~/.local/share/plorn')
    assert cfg.get_datadir() == data_dir
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'plorn_app.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert data_dir == cfg.get_datadir()
    assert cfg.get_dbname() == 'plorn.db'
    if os.path.exists(f'{fname}..TMP'):
        os.remove(fname)
        os.rename(f'{fname}..TMP', fname)

def test_open_new2():
    '''
    Test defaults for a brand new named config file
    '''
    fname = os.path.join('.', 'bogus_test.cfg')
    if os.path.exists(fname):
        os.rename(fname, f'{fname}..TMP')
    cfg = PlornConfig(fname)
    user = getpass.getuser()
    assert cfg.get_username() == user
    fullname = pwd.getpwnam(user).pw_gecos
    assert cfg.get_fullname() == fullname
    cfg_dir = os.path.expanduser('~/.config/plorn')
    assert cfg.get_configdir() == cfg_dir
    data_dir = os.path.expanduser('~/.local/share/plorn')
    assert cfg.get_datadir() == data_dir
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'plorn_app.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert data_dir == cfg.get_datadir()
    assert cfg.get_dbname() == 'plorn.db'
    os.remove(fname)
    if os.path.exists(f'{fname}..TMP'):
        os.rename(f'{fname}..TMP', fname)

def test_open_path1():
    '''
    Make sure we can write a non-default config to ~/.local/plorn
    '''
    path1 = os.path.join(os.environ['HOME'], '.config', 'plorn', 'plorn.cfg')
    path2 = os.path.join(os.environ['HOME'], '.plorn.cfg')
    path3 = os.path.join('.', 'plorn.cfg')
    for ii in [path1, path2, path3]:
        if os.path.exists(ii):
            os.rename(ii, f'{ii}..TMP')
    assert os.path.exists(path1) == False
    assert os.path.exists(path2) == False
    assert os.path.exists(path3) == False
    write_test_config(path1)
    assert os.path.exists(path1)
    cfg = PlornConfig(path1)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'
    
    assert os.path.exists(path1)
    os.remove(path1)
    for ii in [path1, path2, path3]:
        if os.path.exists(f'{ii}..TMP'):
            os.rename(f'{ii}..TMP', ii)

def test_open_path2():
    '''
    Make sure we can write a non-default config to ~/.plorn.cfg
    '''
    path1 = os.path.join(os.environ['HOME'], '.plorn.cfg')
    path2 = os.path.join('.', 'plorn.cfg')
    for ii in [path1, path2]:
        if os.path.exists(ii):
            os.rename(ii, f'{ii}..TMP')
    assert os.path.exists(path1) == False
    assert os.path.exists(path2) == False
    write_test_config(path1)
    assert os.path.exists(path1)
    cfg = PlornConfig(path1)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    
    assert os.path.exists(path1)
    os.remove(path1)
    for ii in [path1, path2]:
        if os.path.exists(f'{ii}..TMP'):
            os.rename(f'{ii}..TMP', ii)

def test_open_path3():
    '''
    Make sure we can write a non-default config to ./plorn.cfg
    '''
    path = os.path.join('.', 'plorn.cfg')
    if os.path.exists(path):
        os.rename(path, f'{path}..TMP')
    assert os.path.exists(path) == False
    write_test_config(path)
    assert os.path.exists(path)
    cfg = PlornConfig(path)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    
    assert os.path.exists(path)
    os.remove(path)
    if os.path.exists(f'{path}..TMP'):
        os.rename(f'{path}..TMP', path)

def test_open_path4():
    '''
    We should be able to find any old config file in ~/.config/plorn
    '''
    fname = 'blunderbuss.config'
    path = os.path.join(os.environ['HOME'], '.config', 'plorn', fname)
    if os.path.exists(path):
        os.rename(path, f'{path}..TMP')
    assert os.path.exists(path) == False
    write_test_config(path)
    assert os.path.exists(path)
    cfg = PlornConfig(fname)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'

    assert os.path.exists(path)
    os.remove(path)
    if os.path.exists(f'{path}..TMP'):
        os.rename(f'{path}..TMP', path)

def test_open_path5():
    '''
    We should be able to find any old config file anywhere
    '''
    fname = 'blunderbuss.config'
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, fname)
    assert os.path.exists(path) == False
    write_test_config(path)
    assert os.path.exists(path)
    cfg = PlornConfig(path)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'

    assert os.path.exists(path)
    os.remove(path)
    assert os.path.exists(tmpdir)
    os.rmdir(tmpdir)

def test_write_config(bogus_config):
    '''
    Try a rewritten config file
    '''
    #-- check the defaults
    cfg = PlornConfig(bogus_config)
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'

    #-- change everything
    cfg.set_username('foobar')
    cfg.set_fullname('foobar')
    cfg.set_configdir('foobar')
    cfg.set_datadir('foobar')
    cfg.set_default_photo('foobar')
    cfg.write_config()

    assert cfg.get_filename() == bogus_config
    assert cfg.get_username() == 'foobar'
    assert cfg.get_fullname() == 'foobar'
    assert cfg.get_configdir() == 'foobar'
    assert cfg.get_datadir() == 'foobar'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'foobar'

    cfg.reread()
    assert cfg.get_filename() == bogus_config
    assert cfg.get_username() == 'foobar'
    assert cfg.get_fullname() == 'foobar'
    assert cfg.get_configdir() == 'foobar'
    assert cfg.get_datadir() == 'foobar'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'foobar'
 
def test_get_filename(bogus_config):
    cfg = PlornConfig(bogus_config)
    assert cfg.get_filename() == bogus_config
    cfg = PlornConfig('bad.cfg')
    assert cfg.get_filename() == 'bad.cfg'
    os.remove(cfg.get_fullpath())
 
def test_get_fullpath(bogus_config):
    cfg = PlornConfig(bogus_config)
    assert cfg.get_fullpath() == bogus_config
    cfg = PlornConfig('bad.cfg')
    fullpath = os.path.join(os.environ['HOME'], '.config', 'plorn','bad.cfg')
    assert cfg.get_fullpath() == fullpath
    os.remove(cfg.get_fullpath())
 
def test_set_user(bogus_config):
    cfg = PlornConfig(bogus_config)
    cfg.set_username('blimpy')
    assert cfg.get_username() == 'blimpy'
 
def test_set_fullname(bogus_config):
    cfg = PlornConfig(bogus_config)
    cfg.set_fullname('blimpy')
    assert cfg.get_fullname() == 'blimpy'
 
def test_set_configdir(bogus_config):
    cfg = PlornConfig(bogus_config)
    cfg.set_configdir('blimpy')
    assert cfg.get_configdir() == 'blimpy'
 
def test_set_datadir(bogus_config):
    cfg = PlornConfig(bogus_config)
    cfg.set_datadir('blimpy')
    assert cfg.get_datadir() == 'blimpy'
 
def test_get_default_catalog(bogus_config):
    cfg = PlornConfig(bogus_config)
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

def test_get_catalog(bogus_config):
    cfg = PlornConfig(bogus_config)
    catalog, datadir, dbname = cfg.get_catalog('default')
    assert catalog == 'default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

def test_get_catalog2(bogus_config):
    cfg = PlornConfig(bogus_config)
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

def test_set_default_catalog(bogus_config):
    cfg = PlornConfig(bogus_config)
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

    cfg.set_current_catalog('Betty')
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

def test_set_catalog(bogus_config):
    cfg = PlornConfig(bogus_config)
    catalog, datadir, dbname = cfg.get_current_catalog()

    cfg.set_catalog(name='Wilma', datadir='/tmp/foobar', dbname='omg.db')

    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

    catalog, datadir, dbname = cfg.get_catalog('Wilma')
    assert catalog == 'Wilma'
    assert datadir == '/tmp/foobar'
    assert dbname == 'omg.db'

    cfg.set_current_catalog('Wilma')
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Wilma'
    assert datadir == '/tmp/foobar'
    assert dbname == 'omg.db'

