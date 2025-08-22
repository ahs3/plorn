import configparser
import getpass
import logging
import os
import pwd
import sys

import plorn_db

version = "0.2.0"
config = None

FONTSIZE = 16

module_logger = logging.getLogger("plorn.config")
module_logger.setLevel(logging.INFO)

class PlornConfig:

    def __init__(self):
        global module_logger, config

        self.new_config = False
        module_logger.debug("looking for config file")
        config_home=os.path.join(os.environ["HOME"], ".config", "plorn")
        data_home=os.path.join(os.environ["HOME"], ".local", "share", "plorn")
        self.config = configparser.ConfigParser()
        if os.path.exists("plorn.cfg"):
            self.filename = "plorn.cfg"
            self.config.read(self.filename)
            module_logger.debug(f"reusing {self.filename}")
        elif os.path.exists(os.path.join(config_home, "plorn.cfg")):
            self.filename = os.path.join(config_home, "plorn.cfg")
            self.config.read(self.filename)
            module_logger.debug(f"reusing {self.filename}")
        else:
            module_logger.debug("config file not found, creating one")
            self.config["plorn"] = {}
            uname = getpass.getuser()
            self.config["plorn"]["user"] = uname
            fullname = pwd.getpwnam(uname).pw_gecos
            self.config["plorn"]["full_name"] = fullname
            self.config["plorn"]["config_dir"] = config_home
            self.config["plorn"]["data_dir"] = data_home
            self.config["plorn"]["dbname"] = "plorn.db"
            self.filename = os.path.join(config_home, "plorn.cfg")

            if not os.path.exists(self.config["plorn"]["config_dir"]):
                os.makedirs(self.config["plorn"]["config_dir"])
            elif not os.path.isdir(self.config["plorn"]["config_dir"]):
                print(f"? {self.config['plorn']['config_dir']} is not a directory")
                sys.exit(1)

            if not os.path.exists(self.config["plorn"]["data_dir"]):
                os.makedirs(self.config["plorn"]["data_dir"])
            elif not os.path.isdir(self.config["plorn"]["data_dir"]):
                print(f"? {self.config['plorn']['data_dir']} is not a directory")
                sys.exit(1)

            module_logger.debug(f"creating {self.filename}")
            self.write_config()
            self.new_config = True
            self.db = plorn_db.open()

        config = self.config
        module_logger.debug("config initialized")

    def write_config(self):
        with open(self.filename, "w") as configfile:
            self.config.write(configfile)

    def get_filename(self):
        return self.filename

    def get_username(self):
        return self.config["plorn"]["user"]

    def get_fullname(self):
        return self.config["plorn"]["full_name"]

    def get_configdir(self):
        return self.config["plorn"]["config_dir"]

    def get_datadir(self):
        return self.config["plorn"]["data_dir"]

    def get_dbname(self):
        return self.config["plorn"]["dbname"]

    def is_new(self):
        return self.new_config

    def get_version(self):
        global version
        return version


def get_config():
    global config

    module_logger.debug("getting config")
    if not config:
        config = PlornConfig()
    return config


