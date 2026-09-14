
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
MINOR = 34
BUGFIX = 16
__version__ = str(MAJOR) + '.' + str(MINOR) + '.' + str(BUGFIX)

module_logger = logging.getLogger('plorn.config')
module_logger.setLevel(logging.INFO)

'''
Config files:
    -- can be located anywhere, but if no name given, search for, in order:
       -- environment variable PLORN_CONFIG with a non-empty path, OR ...
       -- ~/.config/plorn/plorn.cfg (the default)
       First one found is used.
    -- if tbe file can't be found, create the default
    -- ini file format, more or less
    -- [DEFAULT] section is for global items:
        -- user: default is current user
        -- full_name: optional, from system if possible
        -- config_dir: default ~/.config/plorn
        -- data_dir: default ~/.local/share/plorn
        -- current_catalog: default "default"
    -- [gui] section is for appearance items
        -- default_photo: plorn_app.png -- used as an icon and a placeholder
           when an image needs to be shown, and in 'about' window
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
            self.config['DEFAULT'] = {}
            uname = getpass.getuser()
            self.config['DEFAULT']['user'] = uname
            fullname = pwd.getpwnam(uname).pw_gecos
            self.config['DEFAULT']['full_name'] = fullname
            self.config['DEFAULT']['config_dir'] = os.path.join('~', config_dir)
            self.config['DEFAULT']['data_dir'] = os.path.join('~', data_dir)
            self.config['DEFAULT']['default_catalog'] = 'Plorn'
            self.config['DEFAULT']['current_catalog'] = 'Plorn'
            self.config['DEFAULT']['last_directory_selected'] = os.environ['HOME']

            self.config['gui'] = {}
            self.config['gui']['default_photo'] = "plorn_app.png"

            self.config['Plorn'] = {}
            self.config['Plorn']['name'] = 'Plorn'
            self.config['Plorn']['dbname'] = 'plorn.db'

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
        return self.config['DEFAULT']['user']

    def set_username(self, name):
        self.config['DEFAULT']['user'] = name

    def get_fullname(self):
        return self.config['DEFAULT']['full_name']

    def set_fullname(self, name):
        self.config['DEFAULT']['full_name'] = name

    def get_configdir(self):
        return self.config['DEFAULT']['config_dir']

    def set_configdir(self, path):
        self.config['DEFAULT']['config_dir'] = path

    def get_datadir(self):
        return self.config['DEFAULT']['data_dir']

    def set_datadir(self, path):
        self.config['DEFAULT']['data_dir'] = path

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
        datadir = self.config['DEFAULT']['data_dir']
        dbname = 'plorn.db'
        if catalog in self.config.keys():
            result = self.config[catalog]['name']
            datadir = self.config[catalog]['data_dir']
            dbname = self.config[catalog]['dbname']
        else:
            result = None
            datadir = None
            dbname = None
        module_logger.debug(f'_get_catalog: {result}, {datadir}, {dbname}')
        return result, datadir, dbname

    def get_catalog(self, catalog):
        return self._get_catalog(catalog)

    def get_current_catalog(self):
        catalog = self.config['DEFAULT']['current_catalog']
        return self._get_catalog(catalog)

    def get_default_catalog(self):
        catalog = self.config['DEFAULT']['default_catalog']
        return self._get_catalog(catalog)

    def get_catalog_list(self):
        res = []
        for ii in self.config.keys():
            if ii not in ['DEFAULT', 'gui']:
                res.append(ii)
        return sorted(res)

    def _set_catalog(self, catalog, datadir=None, dbname=None):
        '''
        create the catalog entry if there isn't one already
        '''
        global module_logger

        if catalog not in self.config.keys():
            self.config[catalog] = {}
        self.config[catalog]['name'] = catalog
        if datadir == None:
            val = self.config.get(catalog, 'data_dir', fallback=None)
            if val != self.config['DEFAULT']['data_dir']:
                del self.config[catalog]['data_dir']
        else:
            self.config[catalog]['data_dir'] = datadir
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
        self.config['DEFAULT']['current_catalog'] = name

    def set_catalog(self, name, datadir=None, dbname=None):
        self._set_catalog(name, datadir, dbname)

    def set_default_catalog(self, name, datadir=None, dbname=None):
        self.config['DEFAULT']['default_catalog'] = name
        self._set_catalog(name, datadir, dbname)

    def remove_catalog(self, catalog):
        current = self.config['DEFAULT']['current_catalog']
        if catalog == current:
            #-- let's not do that ....
            return
        self.config.remove_section(catalog)

    def get_last_directory_selected(self):
        lds = 'last_directory_selected'
        if self.config.get('DEFAULT', lds, fallback=None) == None:
            self.config['DEFAULT'][lds] = os.environ['HOME']
            self.write_config()
        return self.config['DEFAULT'][lds]

    def set_last_directory_selected(self, directory):
        if os.path.isdir(directory):
            self.config['DEFAULT']['last_directory_selected'] = directory
            self.write_config()

    def __str__(self):
        return self.filename

