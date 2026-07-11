
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
MINOR = 25
BUGFIX = 5
__version__ = str(MAJOR) + '.' + str(MINOR) + '.' + str(BUGFIX)

module_logger = logging.getLogger('plorn.config')
module_logger.setLevel(logging.INFO)

class PlornConfig:
    def __init__(self, name='plorn.cfg'):
        global module_logger, config

        module_logger.debug('looking for config file')
        config_home=os.path.join(os.environ['HOME'], '.config', 'plorn')
        data_home=os.path.join(os.environ['HOME'], '.local', 'share', 'plorn')
        self.config = configparser.ConfigParser()
        if name and os.path.exists(name):
            self.filename = name
            self.config.read(self.filename)
            module_logger.debug(f'reusing ./{self.filename}')
        elif name and os.path.exists(os.path.join(config_home, name)):
            self.filename = os.path.join(config_home, name)
            self.config.read(self.filename)
            module_logger.debug(f'reusing $cfg/{self.filename}')
        else:
            if not name:
                name = 'plorn.cfg'
            module_logger.debug('config file not found, creating one')
            self.config['plorn'] = {}
            uname = getpass.getuser()
            self.config['plorn']['user'] = uname
            fullname = pwd.getpwnam(uname).pw_gecos
            self.config['plorn']['full_name'] = fullname
            self.config['plorn']['config_dir'] = config_home
            self.config['plorn']['data_dir'] = data_home
            self.config['plorn']['dbname'] = name.replace('.cfg', '.db')

            self.config['gui'] = {}
            self.config['gui']['theme'] = 'darkly'
            self.config['gui']['fontsize'] = '16'
            self.config['gui']['default_photo'] = "plorn_app.png"

            self.filename = os.path.join(config_home, name)

            if not os.path.exists(self.config['plorn']['config_dir']):
                os.makedirs(self.config['plorn']['config_dir'])
            elif not os.path.isdir(self.config['plorn']['config_dir']):
                print(f'? {self.config['plorn']['config_dir']} is not a directory')
                sys.exit(1)

            if not os.path.exists(self.config['plorn']['data_dir']):
                os.makedirs(self.config['plorn']['data_dir'])
            elif not os.path.isdir(self.config['plorn']['data_dir']):
                print(f'? {self.config['plorn']['data_dir']} is not a directory')
                sys.exit(1)

            module_logger.debug(f'creating {self.filename}')
            self.write_config()

        config = self.config
        module_logger.debug('config initialized')

    def write_config(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
        configfile.close()

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

    def get_dbname(self):
        return self.config['plorn']['dbname']

    def set_dbname(self, dbname):
        self.config['plorn']['dbname'] = dbname

    def get_version(self):
        global __version__
        return __version__

    def get_theme(self):
        return self.config['gui']['theme']

    def set_theme(self, themename):
        self.config['gui']['theme'] = themename
        
    def get_fontsize(self):
        return int(self.config['gui']['fontsize'])

    def set_fontsize(self, fontsize):
        if not isinstance(fontsize, int):
            raise TypeError('fontsize must be an integer')
        self.config['gui']['fontsize'] = str(fontsize)
        
    def get_default_photo(self):
        return self.config['gui']['default_photo']

    def set_default_photo(self, default_photo):
        self.config['gui']['default_photo'] = default_photo
        
    def __str__(self):
        return self.filename

config = PlornConfig()

