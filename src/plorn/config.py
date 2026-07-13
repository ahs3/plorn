
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
MINOR = 26
BUGFIX = 2
__version__ = str(MAJOR) + '.' + str(MINOR) + '.' + str(BUGFIX)

module_logger = logging.getLogger('plorn.config')
module_logger.setLevel(logging.DEBUG)

'''
Config files:
    -- can be located anywhere, but if no name given, search for, in order:
       -- ~/.config/plorn/plorn.cfg, './plorn.cfg'
       -- ~/.plorn.cfg,
       -- ./plorn.cfg
       then ~/.config/plorn/plorn.cfg, './plorn.cfg', if no path provided.
       First one found is used.
    -- if no directory is given, assume the file is in ~/.config/plorn
    -- if '.', '~' or '/' is the first character in the name, assume it
       is already a complete path and search only for that
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

class PlornConfig:
    def __init__(self, filename=None):
        global module_logger, config

        self.filename = filename
        module_logger.debug(f'looking for config file "{filename}"')
        config_home = os.path.join(os.environ['HOME'], '.config', 'plorn')
        data_home = os.path.join(os.environ['HOME'], '.local', 'share', 'plorn')
        self.fullpath = self.find_config(filename, config_home)
        module_logger.debug(f'using {self.fullpath}')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.fullpath):
            self.config.read(self.fullpath)
        else:
            module_logger.debug('config file not found, creating one')
            self.config['plorn'] = {}
            uname = getpass.getuser()
            self.config['plorn']['user'] = uname
            fullname = pwd.getpwnam(uname).pw_gecos
            self.config['plorn']['full_name'] = fullname
            self.config['plorn']['config_dir'] = config_home
            self.config['plorn']['data_dir'] = data_home
            self.config['plorn']['current_catalog'] = 'default'

            self.config['gui'] = {}
            self.config['gui']['default_photo'] = "plorn_app.png"

            self.config['default'] = {}
            self.config['default']['dbname'] = 'plorn.db'

            if not os.path.isdir(self.config['plorn']['config_dir']):
                print(f'? {self.config['plorn']['config_dir']} is not a directory')
                sys.exit(1)

            if not os.path.exists(self.config['plorn']['data_dir']):
                os.makedirs(self.config['plorn']['data_dir'])
            elif not os.path.isdir(self.config['plorn']['data_dir']):
                print(f'? {self.config['plorn']['data_dir']} is not a directory')
                sys.exit(1)

            module_logger.debug(f'creating {self.fullpath}')
            self.write_config()

        config = self.config
        module_logger.debug('config initialized')

    def find_config(self, filename, config_home):
        global module_logger

        #-- assume a full path was given
        if filename and filename[0] in ['/', '~', '.']:
            return os.path.expanduser(os.path.expandvars(filename))

        #-- assume a specific config file is wanted
        if filename:
            if os.path.dirname(filename) != '':
                return os.path.expanduser(os.path.expandvars(filename))
            else:
                #-- ... but maybe without a path provided
                return os.path.join(config_home, filename)

        #-- look for the default name in the proper places
        fname = 'plorn.cfg'
        cfg_std = os.path.join(config_home, fname)
        if not os.path.exists(cfg_std):
            cfg_user = os.path.join(os.environ['HOME'], f'.{fname}')
            if not os.path.exists(cfg_user):
                cfg_local = os.path.join('.', fname)
                if not os.path.exists(cfg_local):
                    if not os.path.exists(config_home):
                        os.makedirs(config_home)
                    cfg_local = os.path.join(config_home, fname)
                return cfg_local
            else:
                return cfg_user
        else:
            return cfg_std

    def write_config(self):
        with open(self.fullpath, 'w') as configfile:
            self.config.write(configfile)
        configfile.close()

    def reread(self):
        self.config.read(self.fullpath)

    def get_filename(self):
        return self.filename

    def get_fullpath(self):
        return self.fullpath

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

        datadir = self.config['plorn']['data_dir']
        dbname = 'plorn.db'
        if self.config[catalog] and len(self.config[catalog]) > 0:
            if self.config[catalog].get('data_dir') == None:
                datadir = self.config['plorn']['data_dir']
            else:
                datadir = self.config[catalog]['data_dir']
            if self.config[catalog].get('dbname') != None:
                dbname = self.config[catalog]['dbname']
        module_logger.info(f'get: {catalog}, {datadir}, {dbname}')
        return catalog, datadir, dbname

    def get_catalog(self, catalog):
        return self._get_catalog(catalog)

    def get_current_catalog(self):
        catalog = self.config['plorn']['current_catalog']
        return self._get_catalog(catalog)

    def _set_catalog(self, catalog='default', datadir=None, dbname=None):
        '''
        create the catalog entry if there isn't one already
        '''
        global module_logger

        if catalog not in self.config.keys():
            self.config[catalog] = {}
        if datadir:
            self.config[catalog]['data_dir'] = datadir
        if dbname:
            self.config[catalog]['dbname'] = dbname
        elif self.config[catalog].get('dbname') == None:
            self.config[catalog]['dbname'] = f'{catalog}.catalog'
        msg  = f'set: {catalog}, {self.config[catalog]['data_dir']}'
        msg += f', {self.config[catalog]['dbname']}'
        module_logger.info(msg)

    def set_current_catalog(self, name='default', datadir=None, dbname=None):
        self._set_catalog(name, datadir, dbname)
        self.config['plorn']['current_catalog'] = name

    def set_catalog(self, name='default', datadir=None, dbname=None):
        self._set_catalog(name, datadir, dbname)

    def get_dbname(self, catalog='default'):
        res = None
        if self.config[catalog]:
            if self.config[catalog]['dbname']:
                res = self.config[catalog]['dbname']
        return res

    def set_dbname(self, dbname, catalog='default'):
        if not self.config[catalog]['dbname']:
            self.config[catalog] = {}
        self.config[catalog]['dbname'] = dbname

    def __str__(self):
        return self.fullpath

config = PlornConfig()

