
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import getpass
import os
import pwd
import sys
import unittest

import pytest

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)
    print(sys.path)
        
import plorn.config

class TestConfig:
     def write_test_config(self, name):
         data = [
             '[plorn]',
             'user = fred',
             'full_name = Fred Flintstone',
             'config_dir = /tmp/barney',
             'data_dir = /tmp/wilma',
             'dbname = dino.db',
             '',
             '[gui]',
             'theme = kinda darkly',
             'fontsize = 61',
             'default_photo = plorn_app.png',
         ]
         with open(name, 'w') as cfg:
             for ii in data:
                 cfg.write(ii + '\n')
         cfg.close()
 
#    def setUp(self):
#        cfg_file = os.path.expanduser('~/.config/plorn/.bogus_test.cfg')
#        if os.path.exists(cfg_file):
#            os.remove(cfg_file)
#        db_file = os.path.expanduser('~/.local/share/plorn/.bogus_test.db')
#        if os.path.exists(db_file):
#            os.remove(db_file)
#
#        cfg_file = 'completely_bogus_test.cfg'
#        if os.path.exists(cfg_file):
#            os.remove(cfg_file)
#        db_file = '/tmp/wilma/dino.db'
#        if os.path.exists(db_file):
#            os.remove(db_file)
#        self.write_test_config(cfg_file)
#
#    def tearDown(self):
#        cfg_file = os.path.expanduser('~/.config/plorn/.bogus_test.cfg')
#        if os.path.exists(cfg_file):
#            os.remove(cfg_file)
#        db_file = os.path.expanduser('~/.local/share/plorn/.bogus_test.db')
#        if os.path.exists(db_file):
#            os.remove(db_file)
#
#        cfg_file = 'completely_bogus_test.cfg'
#        if os.path.exists(cfg_file):
#            os.remove(cfg_file)
#        db_file = '/tmp/wilma/dino.db'
#        if os.path.exists(db_file):
#            os.remove(db_file)

     def test_open_new(self):
         '''
         Assume defaults for most things
         '''
         cfg = plorn.config.PlornConfig('.bogus_test.cfg')
         user = getpass.getuser()
         assert cfg.get_username() == user
         fullname = pwd.getpwnam(user).pw_gecos
         assert cfg.get_fullname() == fullname
         cfg_dir = os.path.expanduser('~/.config/plorn')
         assert cfg.get_configdir() == cfg_dir
         data_dir = os.path.expanduser('~/.local/share/plorn')
         assert cfg.get_datadir() == data_dir
         dbname = '.bogus_test.db'
         assert cfg.get_dbname() == dbname
         assert cfg.get_version() != ''
         assert cfg.get_theme() == 'darkly'
         assert cfg.get_fontsize() == 16
         assert cfg.get_default_photo() == 'plorn_app.png'

     def test_open_existing(self):
         '''
         Try a completely made up config file
         '''
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         assert cfg.get_filename() == cfg_file
         assert cfg.get_username() == 'fred'
         assert cfg.get_fullname() == 'Fred Flintstone'
         assert cfg.get_configdir() == '/tmp/barney'
         assert cfg.get_datadir() == '/tmp/wilma'
         assert cfg.get_dbname() == 'dino.db'
         assert cfg.get_version() != ''
         assert cfg.get_theme() == 'kinda darkly'
         assert cfg.get_fontsize() == 61
         assert cfg.get_default_photo() == 'plorn_app.png'
 
     def test_write_config(self):
         '''
         Try a rewritten config file
         '''
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_username('foobar')
         cfg.set_fullname('foobar')
         cfg.set_configdir('foobar')
         cfg.set_datadir('foobar')
         cfg.set_dbname('foobar')
         cfg.set_theme('foobar')
         cfg.set_fontsize(42)
         cfg.set_default_photo('foobar')
         assert cfg.get_filename() == cfg_file
         assert cfg.get_username() == 'foobar'
         assert cfg.get_fullname() == 'foobar'
         assert cfg.get_configdir() == 'foobar'
         assert cfg.get_datadir() == 'foobar'
         assert cfg.get_dbname() == 'foobar'
         assert cfg.get_version() != ''
         assert cfg.get_theme() == 'foobar'
         assert cfg.get_fontsize() == 42
         assert cfg.get_default_photo() == 'foobar'
 
     def test_set_user(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_username('blimpy')
         assert cfg.get_username() == 'blimpy'
 
     def test_set_fullname(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_fullname('blimpy')
         assert cfg.get_fullname() == 'blimpy'
 
     def test_set_configdir(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_configdir('blimpy')
         assert cfg.get_configdir() == 'blimpy'
 
     def test_set_datadir(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_datadir('blimpy')
         assert cfg.get_datadir() == 'blimpy'
 
     def test_set_dbname(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_dbname('blimpy')
         assert cfg.get_dbname() == 'blimpy'

     def test_set_theme(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_theme('blimpy')
         assert cfg.get_theme() == 'blimpy'

     def test_set_fontsize(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         cfg.set_fontsize(972)
         assert cfg.get_fontsize() == 972

     def test_set_bad_fontsize(self):
         cfg_file = 'completely_bogus_test.cfg'
         if os.path.exists(cfg_file):
             os.remove(cfg_file)
         self.write_test_config(cfg_file)
         cfg = plorn.config.PlornConfig(cfg_file)
         with pytest.raises(TypeError) as excinfo:
            cfg.set_fontsize('blimpy')
         assert str(excinfo.value) == 'fontsize must be an integer'
         assert cfg.get_fontsize() == 61

