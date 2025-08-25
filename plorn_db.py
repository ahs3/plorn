import logging
import os
import sqlite3
import sys

import plorn_album
import plorn_config

module_logger = logging.getLogger("plorn.db")
module_logger.setLevel(logging.DEBUG)

config = plorn_config.get_config()
current_db = None

def get_dbname():
    dbpath = config.get_datadir()
    dbname = config.get_dbname()
    return os.path.join(dbpath, dbname)

class PlornDb:
    def __init__(self, dbname):
        global module_logger, config, current_db

        self.dbname = dbname
        self.db = sqlite3.connect(dbname)
        self.cursor = self.db.cursor()

    def create_tables(self):
        global module_logger
        
        module_logger.debug("called create_tables")
        self.create_config_table()
        self.create_albums_table()

    def create_config_table(self):
        global module_logger, config

        table_desc = "config(name, version, username, fullname, datadir)"
        self.cursor.execute("CREATE TABLE " + table_desc)
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        module_logger.debug("added table: " + str(res.fetchone()))

        sql = "INSERT INTO config VALUES (\"plorn\", "
        sql += f"\"{config.get_version()}\", \"{config.get_username()}\", "
        sql += f"\"{config.get_fullname()}\", \"{config.get_datadir()}\")"
        self.cursor.execute(sql)
        self.db.commit()

    def create_albums_table(self):
        global module_logger, config

        table_desc = "albums(name, path, date, notes, photo_count)"
        self.cursor.execute("CREATE TABLE " + table_desc)
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        module_logger.debug("added table: " + str(res.fetchone()))
        self.db.commit()

    def album_exists(self, album):
        sql = f"SELECT * FROM albums WHERE name = \"{album.get_name()}\""
        res = self.cursor.execute(sql)
        return res.fetchall() == None

    def add_album(self, album):
        sql = "INSERT INTO albums VALUES "
        sql += f"(\"{album.get_name()}\", \"{album.get_path()}\", "
        sql += f"\"{album.get_dated()}\", \"{album.get_notes()}\", "
        sql += f"{album.get_photo_count()})"
        res = self.cursor.execute(sql)
        self.db.commit()
        return res.fetchall() == None


def open():
    global module_logger, current_db, config

    module_logger.debug("open db")
    if config == None:
        module_logger.debug("new config")
        config = get_config()
    module_logger.debug(f"config is \"{str(config)}\"")

    if config.needs_db():
        module_logger.debug("need to create tables")
        current_db = PlornDb(get_dbname())
        current_db.create_tables()
        config.db_done()

    elif current_db == None:
        module_logger.debug("open existing db")
        current_db = PlornDb(get_dbname())

    return current_db

