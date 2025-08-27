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

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class PlornDb:
    def __init__(self, dbname):
        global module_logger, config, current_db

        self.dbname = dbname
        self.db = sqlite3.connect(dbname)
        self.db.row_factory = dict_factory
        self.cursor = self.db.cursor()

    def create_tables(self):
        global module_logger
        
        module_logger.debug("called create_tables")
        self.create_config_table()
        self.create_albums_table()
        self.create_photos_table()

    def create_config_table(self):
        global module_logger, config

        sql_stmt = """
            CREATE TABLE IF NOT EXISTS config (
                name text NOT NULL,
                version text,
                username text,
                fullname text,
                datadir text
            );
        """
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug("added table: " + str(row))

        sql = "INSERT INTO config VALUES (\"plorn\", "
        sql += f"\"{config.get_version()}\", \"{config.get_username()}\", "
        sql += f"\"{config.get_fullname()}\", \"{config.get_datadir()}\")"
        self.cursor.execute(sql)
        self.db.commit()

    def create_albums_table(self):
        global module_logger, config

        sql_stmt = """
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY,
                name text NOT NULL,
                path text NOT NULL,
                dated text,
                notes text,
                photo_count INT
            );
        """
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 1
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug("added table: " + str(row))
        self.db.commit()

    def create_photos_table(self):
        global module_logger, config

        sql_stmt = """
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                album_id INT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                dated TEXT,
                notes TEXT,
                FOREIGN KEY (album_id)
                REFERENCES albums (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f"SELECT name FROM sqlite_master WHERE rowid = {rowid}"
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug("added table: " + str(row))
        self.db.commit()

    def album_exists(self, album):
        sql = f"SELECT * FROM albums WHERE name = \"{album.get_name()}\""
        res = self.cursor.execute(sql)
        return res.fetchall() == None

    def add_album(self, album):
        sql = "INSERT INTO albums (name,path,dated,notes,photo_count) VALUES "
        sql += f"(\"{album.get_name()}\", \"{album.get_path()}\", "
        sql += f"\"{album.get_dated()}\", \"{album.get_notes()}\", "
        sql += f"{album.get_photo_count()})"
        res = self.cursor.execute(sql)
        self.db.commit()
        sql = f"SELECT id FROM albums WHERE name = \"{album.get_name()}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"added album {str(row)}")
        return row["id"]

    def get_album_by_name(self, album_name):
        sql = f"SELECT * FROM albums WHERE name = \"{album_name}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"got by name: {str(row)}")
        return row

    def remove_album_by_name(self, album_name):
        sql = f"DELETE FROM albums WHERE name = \"{album_name}\""
        res = self.cursor.execute(sql)
        self.db.commit()
        module_logger.debug(f"removed by name: {album_name}")
        return 

    def get_albums(self):
        sql = f"SELECT id, name, path, photo_count FROM albums"
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        module_logger.debug(f"get_albums: {rows}")
        return rows

    def album_count(self):
        sql = f"SELECT id FROM albums"
        res = self.cursor.execute(sql)
        return len(res.fetchall())

    def photo_count(self):
        sql = f"SELECT id FROM photos"
        res = self.cursor.execute(sql)
        return len(res.fetchall())

    def update_album(self, album, updated_album):
        sql  = f"UPDATE albums"
        sql += f" SET name = \"{updated_album.get_name()}\","
        sql += f" path = \"{updated_album.get_path()}\","
        sql += f" dated = \"{updated_album.get_dated()}\","
        sql += f" notes = \"{updated_album.get_notes()}\","
        sql += f" photo_count = \"{updated_album.get_photo_count()}\""
        sql += f" WHERE name = \"{album.get_name()}\""
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = "SELECT id FROM albums"
        sql += f" WHERE name = \"{updated_album.get_name()}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f"updated album: from {album.get_name()}"
        msg += f" to {row["id"]}"
        module_logger.debug(msg)
        return row["id"]


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
        module_logger.debug(f"open existing db \"{get_dbname()}\"")
        current_db = PlornDb(get_dbname())

    return current_db

