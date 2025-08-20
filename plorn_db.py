import logging
import os
import sqlite3
import sys

import plorn_config

module_logger = logging.getLogger("plorn.db")
module_logger.setLevel(logging.DEBUG)

config = None
current_db = None

def get_dbname():
    global module_logger, config

    #config = plorn_config.get_config()
    dbpath = config.get_datadir()
    dbname = config.get_dbname()
    return os.path.join(dbpath, dbname)

class PlornDb:

    def __init__(self, dbname):
        global module_logger, config, current_db

        self.dbname = dbname
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()
        self.createdb()

    def createdb(self):
        global module_logger
        
        module_logger.debug("called createdb")
        self.create_config_table()
        self.create_albums_table()

    def create_config_table(self):
        global module_logger, config

        table_desc = "config(version, username, fullname, datadir)"
        self.cursor.execute("CREATE TABLE " + table_desc)
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        module_logger.debug("added table: " + str(res.fetchone()))

        sql = "INSERT INTO config VALUES "
        sql += f"(\"{config.get_version()}\", \"{config.get_username()}\", "
        sql += f"\"{config.get_fullname()}\", \"{config.get_datadir()}\")"
        self.cursor.execute(sql)
        self.db.commit()

    def create_albums_table(self):
        global module_logger, config

        table_desc = "albums(name, path, date, notes)"
        self.cursor.execute("CREATE TABLE " + table_desc)
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        module_logger.debug("added table: " + str(res.fetchone()))
        self.db.commit()


def open():
    global module_logger, config, current_db

    if not config:
        config = plorn_config.get_config()
    if not current_db:
        current_db = PlornDb(get_dbname())
    return current_db

