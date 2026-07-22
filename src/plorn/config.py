
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import configparser
import getpass
import logging
import os
import pwd
import sys

MAJOR = 0
MINOR = 27
BUGFIX = 12
__version__ = str(MAJOR) + '.' + str(MINOR) + '.' + str(BUGFIX)

module_logger = logging.getLogger('plorn.config')
module_logger.setLevel(logging.DEBUG)

'''
Config files:
    -- can be located anywhere, but if no name given, search for, in order:
       -- environment variable PLORN_CONFIG with a non-empty path, OR ...
       -- ~/.config/plorn/plorn.cfg (the default)
       First one found is used.
    -- if tbe file can't be found, create the default
    -- ini file format, more or less
    -- [plorn] section is for global items:
        -- user: default is current user
        -- full_name: optional, from system if possible
        -- config_dir: default ~/.config/plorn
        -- data_dir: default ~/.local/share/plorn
        -- current_catalog: default "default"
    -- [gui] section is for appearance items
        -- default_photo: plorn_app.png -- used as an icon and a placeholder
           when an image needs to be shown, and in 'about' window
    -- [default] section is for the default catalog
        -- data_dir: default ~/.local/share/plorn (overrides global)
        -- dbname: default $data_dir/plorn.db; if first character of path
           is '/', '~', or '.', do not prepend $data_dir
    -- [<name>] section is for one or more catalogs that have been created
           and used at some point
        -- data_dir: default ~/.local/share/plorn (overrides global)
        -- dbname: default $data_dir/plorn.db; if first character of path
           is '/', '~', or '.', do not prepend $data_dir

'''

CURRENT_CONFIG = None

class PlornConfig:
    def __init__(self):
        global module_logger, CURRENT_CONFIG

        if CURRENT_CONFIG:
            return CURRENT_CONFIG

        home_dir = os.environ['HOME']
        config_dir = os.path.join('.config', 'plorn')
        data_dir = os.path.join('.local', 'share', 'plorn')

        self.default_path = True
        if 'PLORN_CONFIG' in os.environ.keys():
            name = os.environ['PLORN_CONFIG']
            if len(name) > 0:
                self.filename = name
                self.default_path = False
        else:
            self.filename = 'plorn.cfg'
        module_logger.debug(f'using config file "{self.filename}"')

        self.config = configparser.ConfigParser()
        if os.path.exists(os.path.join(home_dir, config_dir, self.filename)):
            self.config.read(os.path.join(home_dir, config_dir, self.filename))
        else:
            module_logger.debug('config file not found, creating one')
            self.config['plorn'] = {}
            uname = getpass.getuser()
            self.config['plorn']['user'] = uname
            fullname = pwd.getpwnam(uname).pw_gecos
            self.config['plorn']['full_name'] = fullname
            self.config['plorn']['config_dir'] = os.path.join('~', config_dir)
            self.config['plorn']['data_dir'] = os.path.join('~', data_dir)
            self.config['plorn']['current_catalog'] = 'default'

            self.config['gui'] = {}
            self.config['gui']['default_photo'] = "plorn_app.png"

            self.config['default'] = {}
            self.config['default']['name'] = 'Default'
            self.config['default']['dbname'] = 'plorn.db'

            module_logger.debug(f'creating {self.filename}')
            self.write_config()

        module_logger.debug('config initialized')

    def write_config(self):
        home_dir = os.environ['HOME']
        config_dir = os.path.join('.config', 'plorn')
        if self.default_path == True:
            fname = os.path.join(home_dir, config_dir, self.filename)
        else:
            fname = self.filename
        with open(fname, 'w') as configfile:
            self.config.write(configfile)
        configfile.close()
        self.reread()

    def reread(self):
        self.config.read(self.filename)

    def get_filename(self):
        return self.filename

    def get_username(self):
        return self.config['plorn']['user']

    def set_username(self, name):
        self.config['plorn']['user'] = name

    def get_fullname(self):
        return self.config['plorn']['full_name']

    def set_fullname(self, name):
        self.config['plorn']['full_name'] = name

    def get_configdir(self):
        return self.config['plorn']['config_dir']

    def set_configdir(self, path):
        self.config['plorn']['config_dir'] = path

    def get_datadir(self):
        return self.config['plorn']['data_dir']

    def set_datadir(self, path):
        self.config['plorn']['data_dir'] = path

    def get_version(self):
        global __version__
        return __version__

    def get_default_photo(self):
        return self.config['gui']['default_photo']

    def set_default_photo(self, default_photo):
        self.config['gui']['default_photo'] = default_photo
        
    def _get_catalog(self, catalog):
        global module_logger

        result = None
        datadir = self.config['plorn']['data_dir']
        dbname = 'plorn.db'
        #if catalog in self.config.keys() and len(self.config[catalog]) > 0:
        if catalog in self.config.keys():
            result = self.config[catalog]['name']
            if self.config[catalog].get('data_dir') == None:
                datadir = self.config['plorn']['data_dir']
            else:
                datadir = self.config[catalog]['data_dir']
            if self.config[catalog].get('dbname') != None:
                dbname = self.config[catalog]['dbname']
        else:
            result = None
            datadir = None
            dbname = None
        module_logger.info(f'_get_catalog: {result}, {datadir}, {dbname}')
        return result, datadir, dbname

    def get_catalog(self, catalog):
        return self._get_catalog(catalog)

    def get_current_catalog(self):
        catalog = self.config['plorn']['current_catalog']
        return self._get_catalog(catalog)

    def get_default_catalog(self):
        return self._get_catalog('Default')

    def _set_catalog(self, catalog, datadir=None, dbname=None):
        '''
        create the catalog entry if there isn't one already
        '''
        global module_logger

        if catalog not in self.config.keys():
            self.config[catalog] = {}
        self.config[catalog]['name'] = catalog
        if datadir:
            self.config[catalog]['data_dir'] = datadir
        else:
            if 'data_dir' in self.config[catalog].keys():
                del self.config[catalog]['data_dir']
        if dbname:
            self.config[catalog]['dbname'] = dbname
        elif self.config[catalog].get('dbname') == None:
            self.config[catalog]['dbname'] = f'{catalog}.catalog'
        if datadir:
            msg  = f'set: {catalog}, {self.config[catalog]['data_dir']}'
        else:
            msg  = f'set: {catalog}, None'
        msg += f', {self.config[catalog]['dbname']}'
        module_logger.info(msg)

    def set_current_catalog(self, name, datadir=None, dbname=None):
        self.config['plorn']['current_catalog'] = name

    def set_catalog(self, name, datadir=None, dbname=None):
        self._set_catalog(name, datadir, dbname)

    def set_default_catalog(self, name, datadir=None, dbname=None):
        self._set_catalog('Default', datadir, dbname)

    def __str__(self):
        return self.filename

