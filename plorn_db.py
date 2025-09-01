import datetime
import logging
import os
import sqlite3
import sys

import plorn_album
import plorn_config
import plorn_photo

module_logger = logging.getLogger("plorn.db")
module_logger.setLevel(logging.DEBUG)

config = None
current_db = None

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class PlornDb:
    def __init__(self, dbname, config):
        global module_logger, current_db

        self.dbname = dbname
        self.config = config
        self.db = sqlite3.connect(dbname)
        self.db.row_factory = dict_factory
        self.cursor = self.db.cursor()
        self.last_album_id = None
        self.last_photo_id = None
        self.create_tables()

    def close(self):
        self.db.close()
        self.config = None

    def create_tables(self):
        global module_logger
        
        module_logger.debug("called create_tables")
        self.create_config_table()
        self.create_albums_table()
        self.create_photos_table()

    def create_config_table(self):
        global module_logger

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

        cfg = self.config
        sql = "INSERT INTO config VALUES (\"plorn\", "
        sql += f"\"{cfg.get_version()}\", \"{cfg.get_username()}\", "
        sql += f"\"{cfg.get_fullname()}\", \"{cfg.get_datadir()}\")"
        self.cursor.execute(sql)
        self.db.commit()

    def create_albums_table(self):
        global module_logger

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
        global module_logger

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

    def get_config(self):
        sql = f"SELECT * FROM config"
        res = self.cursor.execute(sql)
        return res.fetchone()

    def album_exists(self, album):
        sql = f"SELECT * FROM albums WHERE name = \"{album.get_name()}\""
        res = self.cursor.execute(sql)
        rows = res.fetchone()
        return rows != None

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
        self.last_album_id = row["id"]
        return row["id"]

    def get_last_album_id(self):
        return self.last_album_id

    def get_album_by_name(self, album_name):
        sql = f"SELECT * FROM albums WHERE name = \"{album_name}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"got by name: {str(row)}")
        return row

    def get_album_by_id(self, album_id):
        sql = f"SELECT * FROM albums WHERE id = \"{album_id}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"got by id: {str(row)}")
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

    def get_photos(self, album_id):
        sql  = f"SELECT id, name, path FROM photos"
        sql += f" WHERE album_id = \"{album_id}\""
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        module_logger.debug(f"get_photos: {rows}")
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

    def get_album_object(self, album_id):
        row = self.get_album_by_id(album_id)
        if row == None:
            return None
        return plorn_album.PlornAlbum(row["name"], row["path"],
                        id=row["id"], dated=row["dated"],
                        notes=row["notes"],
                        photo_count=row["photo_count"])

    def get_photo_by_id(self, photo_id):
        sql = f"SELECT * FROM photos WHERE id = \"{photo_id}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"got photo by id: {str(row)}")
        return row

    def get_photo_object(self, photo_id):
        row = self.get_photo_by_id(photo_id)
        if row == None:
            return None
        return plorn_photo.PlornPhoto(row["name"], row["path"],
                        id=row["id"], album_id=row["album_id"],
                        dated=row["dated"], notes=row["notes"])

    def increment_photo_count(self, album):
        album_copy = album
        album_copy.set_photo_count(album.get_photo_count() + 1)
        self.update_album(album, album_copy)

    def add_photo(self, photo, album_id):
        sql = "INSERT INTO photos (album_id,name,path,dated,notes) VALUES "
        sql += f"(\"{album_id}\","
        sql += f" \"{photo.get_name()}\", \"{photo.get_path()}\","
        sql += f" \"{photo.get_dated()}\", \"{photo.get_notes()}\")"
        res = self.cursor.execute(sql)
        album = self.get_album_object(album_id)
        self.increment_photo_count(album)
        self.db.commit()
        sql = f"SELECT * FROM photos WHERE path = \"{photo.get_path()}\""
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f"added photo {str(row)}")
        return row["id"]


def get_dbname(config):
    dbpath = config.get_datadir()
    dbname = config.get_dbname()
    return os.path.join(dbpath, dbname)

def open(dbname="plorn.db", cfgname="plorn.cfg"):
    global module_logger, current_db

    module_logger.debug("open db")
    module_logger.debug(f"config is \"{cfgname}\"")

    config = plorn_config.get_config(cfgname)
    if config.needs_db():
        module_logger.debug("need to create tables")
        current_db = PlornDb(get_dbname(config), config)
        config.db_done()

    if current_db == None:
        module_logger.debug(f"open existing db \"{get_dbname(config)}\"")
        current_db = PlornDb(get_dbname(config), config)

    return current_db

def close():
    global current_db

    if current_db != None:
        current_db.close()
        current_db = None

