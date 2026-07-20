
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import getpass
import logging
import os
import pwd
import shutil
import sys
import tempfile

import pytest
from conftest import write_test_config, bogus_config_data

from plorn.config import PlornConfig


def test_find1(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(tmpdir, 'foobar.cfg')
    monkeypatch.setenv('PLORN_CONFIG', fname)
    cfg = PlornConfig()
    assert cfg.get_filename() == fname
    if os.path.exists(fname):
        os.remove(fname)

def test_find2(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    cfg = PlornConfig()
    assert cfg != None
    assert cfg.get_filename() == 'plorn.cfg'

def test_open_new1(plorn_test_env, monkeypatch):
    '''
    Test all defaults for a new default config file
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    homedir = os.environ['HOME']
    normal_fname = os.path.join(homedir, '.config', 'plorn', 'plorn.cfg')
    cfg = PlornConfig()
    user = getpass.getuser()
    assert cfg.get_username() == user
    fullname = pwd.getpwnam(user).pw_gecos
    assert cfg.get_fullname() == fullname
    assert cfg.get_filename() == 'plorn.cfg'
    assert cfg.get_configdir() == '~/.config/plorn'
    assert cfg.get_datadir() == '~/.local/share/plorn'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'plorn_app.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'plorn.db'

def test_open_new2(plorn_test_env, monkeypatch):
    '''
    Test defaults for a brand new named config file
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(tmpdir, 'bogus_test.cfg')
    monkeypatch.setenv('PLORN_CONFIG', fname)
    cfg = PlornConfig()
    user = getpass.getuser()
    assert cfg.get_username() == user
    fullname = pwd.getpwnam(user).pw_gecos
    assert cfg.get_fullname() == fullname
    assert cfg.get_filename() == fname
    assert cfg.get_configdir() == '~/.config/plorn'
    assert cfg.get_datadir() == '~/.local/share/plorn'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'plorn_app.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'plorn.db'

def test_open_path1(plorn_test_env, monkeypatch):
    '''
    Make sure we can use a non-default config in ~/.config/plorn
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'foobar.cfg')
    write_test_config(fname, bogus_config_data)
    assert os.path.exists(fname)
    monkeypatch.setenv('PLORN_CONFIG', fname)
    cfg = PlornConfig()
    assert cfg != None
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/test_plorn_barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'
    
def test_open_path2(plorn_test_env, monkeypatch):
    '''
    We should be able to find the default config file in ~/.config/plorn
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    assert os.path.exists(fname)
    cfg = PlornConfig()
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/test_plorn_barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

def test_open_path3(plorn_test_env, monkeypatch):
    '''
    We should be able to find any old config file anywhere
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    somedir = os.path.join(tmpdir, 'foo', 'bar')
    os.makedirs(somedir)
    fname = os.path.join(somedir, 'blunderbuss.cfg')
    write_test_config(fname, bogus_config_data)
    assert os.path.exists(fname)
    monkeypatch.setenv('PLORN_CONFIG', fname)
    cfg = PlornConfig()
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/test_plorn_barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

def test_write_config(plorn_test_env, monkeypatch):
    '''
    Try a rewritten config file
    '''
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    assert os.path.exists(fname)

    #-- check the defaults
    cfg = PlornConfig()
    assert cfg.get_username() == 'fred'
    assert cfg.get_fullname() == 'Fred Flintstone'
    assert cfg.get_configdir() == '/tmp/test_plorn_barney'
    assert cfg.get_datadir() == '/tmp/wilma'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'silly-photo.png'

    #-- change everything
    cfg.set_username('foobar')
    cfg.set_fullname('foobar')
    cfg.set_configdir('foobar')
    cfg.set_datadir('foobar')
    cfg.set_default_photo('foobar')
    cfg.set_current_catalog('Betty')
    cfg.set_default_catalog('Betty', None, 'betty_too.catalog')
    cfg.set_catalog('Betty', None, 'new_betty.catalog')

    assert cfg.get_username() == 'foobar'
    assert cfg.get_fullname() == 'foobar'
    assert cfg.get_configdir() == 'foobar'
    assert cfg.get_datadir() == 'foobar'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'foobar'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Betty'
    assert datadir == 'foobar'
    assert dbname == 'new_betty.catalog'
    catalog, datadir, dbname = cfg.get_default_catalog()
    assert catalog == 'Default'
    assert datadir == 'foobar'
    assert dbname == 'betty_too.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == 'foobar'
    assert dbname == 'new_betty.catalog'

    cfg.write_config()
    assert cfg.get_username() == 'foobar'
    assert cfg.get_fullname() == 'foobar'
    assert cfg.get_configdir() == 'foobar'
    assert cfg.get_datadir() == 'foobar'
    assert cfg.get_version() != ''
    assert cfg.get_default_photo() == 'foobar'
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Betty'
    assert datadir == 'foobar'
    assert dbname == 'new_betty.catalog'
    catalog, datadir, dbname = cfg.get_default_catalog()
    assert catalog == 'Default'
    assert datadir == 'foobar'
    assert dbname == 'betty_too.catalog'
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == 'foobar'
    assert dbname == 'new_betty.catalog'
 
def test_get_filename(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    assert os.path.exists(fname)
    cfg = PlornConfig()
    assert cfg.get_filename() == 'plorn.cfg'

    monkeypatch.setenv('PLORN_CONFIG', os.path.join(tmpdir, 'bad.cfg'))
    cfg = PlornConfig()
    assert cfg.get_filename() == os.path.join(tmpdir, 'bad.cfg')
 
def test_set_user(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    cfg = PlornConfig()
    cfg.set_username('blimpy')
    assert cfg.get_username() == 'blimpy'
 
def test_set_configdir(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    cfg = PlornConfig()
    cfg.set_configdir('blimpy')
    assert cfg.get_configdir() == 'blimpy'
 
def test_set_datadir(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    cfg = PlornConfig()
    cfg.set_datadir('blimpy')
    assert cfg.get_datadir() == 'blimpy'
 
def test_get_default_catalog(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    cfg = PlornConfig()
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

def test_get_catalog1(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    cfg = PlornConfig()
    catalog, datadir, dbname = cfg.get_catalog('Default')
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

def test_get_catalog2(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    cfg = PlornConfig()
    catalog, datadir, dbname = cfg.get_catalog('Betty')
    assert catalog == 'Betty'
    assert datadir == '/tmp/betty'
    assert dbname == 'betty.catalog'

def test_set_default_catalog(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    cfg = PlornConfig()
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
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

def test_set_catalog(plorn_test_env, monkeypatch):
    tmpdir, cfgdir, datadir = plorn_test_env
    monkeypatch.setenv('HOME', tmpdir)
    fname = os.path.join(cfgdir, 'plorn.cfg')
    write_test_config(fname, bogus_config_data)
    cfg = PlornConfig()
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
    assert datadir == cfg.get_datadir()
    assert dbname == 'default.catalog'

    cfg.set_catalog(name='Wilma', datadir='/tmp/foobar', dbname='omg.db')
    catalog, datadir, dbname = cfg.get_current_catalog()
    assert catalog == 'Default'
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

