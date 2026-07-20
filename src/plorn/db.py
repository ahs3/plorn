
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
from enum import IntEnum
import logging
import os
import sqlite3
import sys

from PySide6.QtSql import (
    QSql,
    QSqlDatabase,
    QSqlQuery,
)

from plorn import PlornAlbum, PlornPhoto, PlornName, PlornPlace, PlornTag
from plorn.config import PlornConfig

module_logger = logging.getLogger('plorn.db')
module_logger.setLevel(logging.INFO)

#-- handy field number constants
class AlbumFields(IntEnum):
    ID          = 0
    NAME        = 1
    DATED       = 2
    NOTES       = 3
    PHOTO_COUNT = 4

class AlbumNameFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    NAME_ID     = 2

class AlbumPlaceFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    PLACE_ID    = 2

class AlbumTagFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    TAG_ID      = 2

class AttrFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class ConfigFields(IntEnum):
    ID          = 0
    NAME        = 1
    VERSION     = 2
    USERNAME    = 3
    FULLNAME    = 4
    DATADIR     = 5

class NameFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class PhotoFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    NAME        = 2
    PATH        = 3
    DATED       = 4
    NOTES       = 5

class PhotoNameFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    NAME_ID     = 2

class PhotoPlaceFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    PLACE_ID    = 2

class PhotoTagFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    TAG_ID      = 2

class PlaceFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class TagFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class PlornDb(QSqlDatabase):
    def __init__(self, dbname):
        super().__init__()
        global module_logger

        self.dbname = dbname
        self.cfg = PlornConfig()

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(dbname)
        db.open()
        db.row_factory = dict_factory
        
        self.create_tables()

    def create_tables(self):
        global module_logger
        
        module_logger.debug('called create_tables')
        self.create_config_table()
        self.create_albums_table()
        self.create_photos_table()
        for ii in ['names', 'places', 'tags']:
            self.create_attr_table(ii)
        self.create_album_names_table()
        self.create_album_places_table()
        self.create_album_tags_table()
        self.create_photo_names_table()
        self.create_photo_places_table()
        self.create_photo_tags_table()

    def create_config_table(self):
        global module_logger

        db = QSqlDatabase.database()
        if 'config' in db.tables(QSql.TableType.Tables):
            return

        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                name text NOT NULL,
                version text,
                username text,
                fullname text,
                datadir text
            );
        ''')
        db.commit()
        module_logger.debug('checked for config table')

        #-- initial config table (should be constant, really)
        sql  = f'''
            INSERT INTO config (name, version, username, fullname, datadir) 
                VALUES ("plorn", "{self.cfg.get_version()}",
                "{self.cfg.get_username()}", "{self.cfg.get_fullname()}",
                "{self.cfg.get_datadir()}"
            );
        '''
        module_logger.debug(f'config sql: {sql}')
        addquery = QSqlQuery(sql, db)
        db.transaction()
        db.commit()
        module_logger.debug('added config entry')

    def create_albums_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY,
                name text NOT NULL,
                dated text,
                notes text,
                photo_count INT
            );
        ''')
        db.commit()
        module_logger.debug('checked for albums table')

    def create_photos_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
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
        ''')
        db.commit()
        module_logger.debug('checked for photos table')

    def create_attr_table(self, table_name):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                parent_id INT DEFAULT 0,
                value TEXT,
                FOREIGN KEY (parent_id)
                REFERENCES {table_name} (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for {table_name} table')

    def create_album_names_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS album_names (
                id INTEGER PRIMARY KEY,
                album_id INT NOT NULL,
                name_id INT NOT NULL,
                FOREIGN KEY (album_id)
                REFERENCES albums (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (name_id)
                REFERENCES names (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for album_names table')

    def create_album_places_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS album_places (
                id INTEGER PRIMARY KEY,
                album_id INT NOT NULL,
                place_id INT NOT NULL,
                FOREIGN KEY (album_id)
                REFERENCES albums (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (place_id)
                REFERENCES places (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for album_places table')

    def create_album_tags_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS album_tags (
                id INTEGER PRIMARY KEY,
                album_id INT NOT NULL,
                tag_id INT NOT NULL,
                FOREIGN KEY (album_id)
                REFERENCES albums (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (tag_id)
                REFERENCES tags (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for album_tags table')

    def create_photo_names_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS photo_names (
                id INTEGER PRIMARY KEY,
                photo_id INT NOT NULL,
                name_id INT NOT NULL,
                FOREIGN KEY (photo_id)
                REFERENCES photos (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (name_id)
                REFERENCES names (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for photo_names table')

    def create_photo_places_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS photo_places (
                id INTEGER PRIMARY KEY,
                photo_id INT NOT NULL,
                place_id INT NOT NULL,
                FOREIGN KEY (photo_id)
                REFERENCES photos (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (place_id)
                REFERENCES places (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for photo_places table')

    def create_photo_tags_table(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        db.transaction()
        query.exec('''
            CREATE TABLE IF NOT EXISTS photo_tags (
                id INTEGER PRIMARY KEY,
                photo_id INT NOT NULL,
                tag_id INT NOT NULL,
                FOREIGN KEY (photo_id)
                REFERENCES photos (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY (tag_id)
                REFERENCES tags (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        ''')
        db.commit()
        module_logger.debug(f'checked for photo_tags table')

    def get_config(self):
        global module_logger

        db = QSqlDatabase.database()
        query = QSqlQuery('SELECT * FROM config;', db)
        query.next()
        return query

    def get_all_albums_list(self):
        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        query.prepare(f'SELECT * FROM albums')
        query.setForwardOnly(True)
        query.exec()
        return query

    def get_all_photos_list(self, album_id=None):
        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        sql  = 'SELECT * FROM photos'
        if album_id != None:
            sql += f' WHERE album_id = \'{album_id}\''
        query.prepare(sql)
        query.setForwardOnly(True)
        query.exec()
        return query

    def album_exists(self, album):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM albums WHERE name = \'{album.get_name()}\';'
        query = QSqlQuery(sql, db)
        query.next()
        return query.value(AlbumFields.NAME) != None

    def photo_exists(self, photo):
        db = QSqlDatabase.database()
        query = QSqlQuery(db=db)
        sql = f'SELECT * FROM photos WHERE id = \'{photo.get_id()}\''
        query.prepare(sql)
        return query.exec().size() < 1

    def add_album_name_list(self, album):
        db = QSqlDatabase.database()
        res = None
        if len(album.get_name_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_names (name_id, album_id) VALUES '
            for ii in album.get_name_list():
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db)
            res = query
        return res

    def remove_album_name_list(self, album):
        db = QSqlDatabase.database()
        sql = f'DELETE FROM album_names WHERE album_id = \'{album.get_id()}\';'
        return QSqlQuery(sql, db)

    def add_album_place_list(self, album):
        db = QSqlDatabase.database()
        res = None
        if len(album.get_place_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_places (place_id, album_id) VALUES '
            for ii in album.get_place_list():
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db)
            res = query
        return res

    def remove_album_place_list(self, album):
        db = QSqlDatabase.database()
        sql = f'DELETE FROM album_places WHERE album_id = \'{album.get_id()}\';'
        return QSqlQuery(sql, db)

    def add_album_tag_list(self, album):
        db = QSqlDatabase.database()
        res = None
        if len(album.get_tag_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_tags (tag_id, album_id) VALUES '
            for ii in album.get_tag_list():
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db)
            res = query
        return res

    def remove_album_tag_list(self, album):
        db = QSqlDatabase.database()
        sql = f'DELETE FROM album_tags WHERE album_id = \'{album.get_id()}\''
        return QSqlQuery(sql, db)

    def add_photo_name_list(self, photo):
        res = None
        if len(photo.get_name_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_names (name_id, photo_id) VALUES '
            for ii in photo.get_name_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {photo_id}')
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
        return res

    def remove_photo_name_list(self, photo):
        sql = f'DELETE FROM photo_names WHERE photo_id = \'{photo.get_id()}\''
        return self.cursor.execute(sql)

    def add_photo_place_list(self, photo):
        res = None
        if len(photo.get_place_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_places (place_id, photo_id) VALUES '
            for ii in photo.get_place_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {photo_id}')
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
        return res

    def remove_photo_place_list(self, photo):
        sql = f'DELETE FROM photo_places WHERE photo_id = \'{photo.get_id()}\''
        return self.cursor.execute(sql)

    def add_photo_tag_list(self, photo):
        res = None
        if len(photo.get_tag_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_tags (tag_id, photo_id) VALUES '
            for ii in photo.get_tag_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {photo_id}')
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
        return res

    def remove_photo_tag_list(self, photo):
        sql = f'DELETE FROM photo_tags WHERE photo_id = \'{photo.get_id()}\''
        return self.cursor.execute(sql)

    def add_album(self, album):
        db = QSqlDatabase.database()

        db.transaction()
        sql = 'INSERT INTO albums (name,dated,notes,photo_count) VALUES '
        sql += f'("{album.get_name()}", '
        sql += f' "{album.get_dated()}", '
        sql += f' "{album.get_notes()}", '
        sql += f' {album.get_photo_count()}'
        sql += f');'
        query = QSqlQuery(sql, db)

        sql = f'SELECT * FROM albums WHERE name = "{album.get_name()}";'
        query = QSqlQuery(sql, db)
        query.next()
        module_logger.debug(f'added album {query.value(AlbumFields.NAME)}')
        result = PlornAlbum(query.value(AlbumFields.NAME),
                            id=query.value(AlbumFields.ID),
                            dated=query.value(AlbumFields.DATED),
                            notes=query.value(AlbumFields.NOTES),
                            photo_count=query.value(AlbumFields.PHOTO_COUNT),
        )

        album_id = result.get_id()
        result.set_name_list(album.get_name_list())
        result.set_place_list(album.get_place_list())
        result.set_tag_list(album.get_tag_list())

        res = self.add_album_name_list(result)
        res = self.add_album_place_list(result)
        res = self.add_album_tag_list(result)

        db.commit()
        return result

    def get_album(self, album_id):
        return self.get_album_by_id(album_id)

    def get_album_by_name(self, album_name):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM albums WHERE name = \'{album_name}\''
        query = QSqlQuery(sql, db)
        query.next()
        module_logger.debug(f'got by name: {str(query.value(AlbumFields.ID))}')
        return self.get_album_by_id(query.value(AlbumFields.ID))

    def get_album_by_id(self, album_id):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM albums WHERE id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        if not query.next():
            return None

        p = PlornAlbum(query.value(AlbumFields.NAME),
                       id=query.value(AlbumFields.ID),
                       dated=query.value(AlbumFields.DATED),
                       notes=query.value(AlbumFields.NOTES),
                       photo_count=query.value(AlbumFields.PHOTO_COUNT),
        )
        names = self.get_names_for_album_by_id(album_id)
        places = self.get_places_for_album_by_id(album_id)
        tags = self.get_tags_for_album_by_id(album_id)
        p.set_name_list(names)
        p.set_place_list(places)
        p.set_tag_list(tags)
        return p

    def remove_album_by_name(self, album_name):
        album = self.get_album_by_name(album_name)
        if album != None:
            self.remove_album_by_id(album.get_id())
        module_logger.debug(f'removed album by name: {album_name}')
        return 

    def remove_album_by_id(self, album_id):
        db = QSqlDatabase.database()
        db.transaction()
        sql = f'DELETE FROM albums WHERE id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        sql = f'DELETE FROM photos WHERE album_id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        sql = f'DELETE FROM album_names WHERE album_id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        sql = f'DELETE FROM album_places WHERE album_id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        sql = f'DELETE FROM album_tags WHERE album_id = \'{album_id}\';'
        query = QSqlQuery(sql, db)
        db.commit()
        module_logger.debug(f'removed album by id: {album_id}')
        return 

    def remove_album(self, album):
        self.remove_album_by_id(album.get_id())
        module_logger.debug(f'removed album by name: {album.get_name()}')
        return 

    def album_count(self):
        db = QSqlDatabase.database()
        query = QSqlQuery(f'SELECT id FROM albums', db=db)
        query.setForwardOnly(True)
        query.exec()
        count = 0
        while query.next():
            count += 1
        return count

    def photo_count(self):
        db = QSqlDatabase.database()
        query = QSqlQuery(f'SELECT id FROM photos', db=db)
        query.setForwardOnly(True)
        query.exec()
        count = 0
        while query.next():
            count += 1
        return count

    def add_name_to_album_by_id(self, name_id, album_id):
        global module_logger

        module_logger.debug(f'adding name to album: {name_id}, {album_id}')
        sql  = 'INSERT INTO album_names '
        sql += '(name_id, album_id) '
        sql += f'VALUES ({name_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_name_from_album_by_id(self, name_id, album_id):
        global module_logger

        module_logger.debug(f'removing name from album: {name_id}, {album_id}')
        sql  = 'DELETE FROM album_names'
        sql += f' WHERE name_id = {name_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def add_place_to_album_by_id(self, place_id, album_id):
        global module_logger

        module_logger.debug(f'adding place to album: {place_id}, {album_id}')
        sql  = 'INSERT INTO album_places '
        sql += '(place_id, album_id) '
        sql += f'VALUES ({place_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_place_from_album_by_id(self, place_id, album_id):
        global module_logger

        module_logger.debug(f'removing place from album: {place_id}, {album_id}')
        sql  = 'DELETE FROM album_places'
        sql += f' WHERE place_id = {place_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def add_tag_to_album_by_id(self, tag_id, album_id):
        global module_logger

        module_logger.debug(f'adding tag to album: {tag_id}, {album_id}')
        sql  = 'INSERT INTO album_tags '
        sql += '(tag_id, album_id) '
        sql += f'VALUES ({tag_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_tag_from_album_by_id(self, tag_id, album_id):
        global module_logger

        module_logger.debug(f'removing tag from album: {tag_id}, {album_id}')
        sql  = 'DELETE FROM album_tags'
        sql += f' WHERE tag_id = {tag_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def update_album(self, album, updated_album):
        global module_logger

        module_logger.debug(f'db update for {album.get_name()}')
        db = QSqlDatabase.database()
        db.transaction()
        self.remove_album_name_list(album)
        self.add_album_name_list(updated_album)
        self.remove_album_place_list(album)
        self.add_album_place_list(updated_album)
        self.remove_album_tag_list(album)
        self.add_album_tag_list(updated_album)

        sql  = f'UPDATE albums'
        sql += f' SET name = "{updated_album.get_name()}",'
        sql += f' dated = "{updated_album.get_dated()}",'
        sql += f' notes = "{updated_album.get_notes()}",'
        sql += f' photo_count = {updated_album.get_photo_count()}'
        sql += f' WHERE id = {album.get_id()}'
        sql += ';'
        query = QSqlQuery(sql, db)
        db.commit()

        sql  = 'SELECT * FROM albums'
        sql += f' WHERE name = "{updated_album.get_name()}";'
        query = QSqlQuery(sql, db)
        query.next()
        msg = f'updated album: from {album.get_name()}'
        msg += f' to {query.value(AlbumFields.ID)}'
        module_logger.debug(msg)
        return self.get_album_by_id(query.value(AlbumFields.ID))

    def get_photo_row_by_id(self, photo_id):
        sql = f'SELECT * FROM photos WHERE id = {photo_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return row

    def get_photo_by_id(self, photo_id):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM photos WHERE id = {photo_id};'
        query = QSqlQuery(sql, db)
        query.next()
        p = PlornPhoto(query.value(PhotoFields.NAME),
                       id=query.value(PhotoFields.ID),
                       album_id=query.value(PhotoFields.ALBUM_ID),
                       path=query.value(PhotoFields.PATH),
                       dated=query.value(PhotoFields.DATED),
                       notes=query.value(PhotoFields.NOTES),
        )
        names = self.get_names_for_photo_by_id(photo_id)
        places = self.get_places_for_photo_by_id(photo_id)
        tags = self.get_tags_for_photo_by_id(photo_id)
        p.set_name_list(names)
        p.set_place_list(places)
        p.set_tag_list(tags)
        return p

    def get_photo(self, photo_id):
        return self.get_photo_by_id(photo_id)

    def increment_photo_count(self, album):
        album_copy = album
        album_copy.set_photo_count(album.get_photo_count() + 1)
        self.update_album(album, album_copy)

    def decrement_photo_count(self, album):
        album_copy = album
        album_copy.set_photo_count(album.get_photo_count() - 1)
        self.update_album(album, album_copy)

    def add_photo(self, photo):
        db = QSqlDatabase.database()
        db.transaction()
        album = self.get_album(photo.get_album_id())
        sql  = 'INSERT INTO photos '
        sql += f'(album_id,name,path,dated,notes) VALUES '
        sql += f'(\'{photo.get_album_id()}\','
        sql += f' \'{photo.get_name()}\', \'{photo.get_path()}\','
        sql += f' \'{photo.get_dated()}\', \'{photo.get_notes()}\')'
        query = QSqlQuery(sql, db)
        self.increment_photo_count(album)
        db.commit()

        sql = f'SELECT * FROM photos WHERE path = \'{photo.get_path()}\';'
        query = QSqlQuery(sql, db)
        query.next()
        module_logger.debug(f'added photo {query.value(PhotoFields.ID)}')
        return PlornPhoto(query.value(PhotoFields.NAME),
                          id=query.value(PhotoFields.ID),
                          album_id=query.value(PhotoFields.ALBUM_ID),
                          path=query.value(PhotoFields.PATH),
                          dated=query.value(PhotoFields.DATED),
                          notes=query.value(PhotoFields.NOTES))

    def remove_photo_by_id(self, photo_id):
        sql = f'SELECT * FROM photos WHERE id = \'{photo_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        album = self.get_album(row['album_id'])

        sql = f'DELETE FROM photos WHERE id = \'{photo_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM photo_names WHERE photo_id = \'{photo_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM photo_places WHERE photo_id = \'{photo_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM photo_tags WHERE photo_id = \'{photo_id}\''
        res = self.cursor.execute(sql)
        self.decrement_photo_count(album)
        module_logger.debug(f'removed photo by id: {photo_id}')
        self.db.commit()
        return 

    def update_photo(self, photo, updated_photo):
        self.remove_photo_name_list(photo)
        self.add_photo_name_list(updated_photo)
        self.remove_photo_place_list(photo)
        self.add_photo_place_list(updated_photo)
        self.remove_photo_tag_list(photo)
        self.add_photo_tag_list(updated_photo)

        sql  = f'UPDATE photos'
        sql += f' SET name = \'{updated_photo.get_name()}\','
        sql += f' path = \'{updated_photo.get_path()}\','
        sql += f' dated = \'{updated_photo.get_dated()}\','
        sql += f' notes = \'{updated_photo.get_notes()}\''
        sql += f' WHERE id = \'{photo.get_id()}\''
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = 'SELECT * FROM photos'
        sql += f' WHERE id = \'{updated_photo.get_id()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f'updated photo: from {photo.get_name()}'
        msg += f' to {row['id']}'
        module_logger.debug(msg)
        return self.get_photo_by_id(photo.get_id())

    def name_exists(self, name, parent_id=0):
        sql = f'SELECT * FROM names WHERE name = \'{name}\''
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        pid = parent_id
        if parent_id == None:
            pid = 0
        for ii in rows:
            if ii['parent_id'] == pid:
                return True
        return False

    def get_names_cursor(self):
        sql = f'SELECT * FROM names'
        res = self.cursor.execute(sql)
        return self.cursor

    def get_places_cursor(self):
        sql = f'SELECT * FROM places'
        res = self.cursor.execute(sql)
        return self.cursor

    def get_tags_cursor(self):
        sql = f'SELECT * FROM tags'
        res = self.cursor.execute(sql)
        return self.cursor

    def get_name(self, name_id, parent_id=0):
        sql = f'SELECT * FROM names WHERE id = \'{name_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f'get_name: {str(row)}')
        return PlornName(row['name'], id=row['id'], parent_id=row['parent_id'])

    def get_name_by_name(self, name, parent_id=0):
        sql  = f'SELECT * FROM names WHERE name = \'{name}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornName(row['name'], id=row['id'], parent_id=row['parent_id'])

    def get_name_children(self, name_id):
        sql = f'SELECT * FROM names WHERE parent_id = {name_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            p = PlornName(ii['name'], id=ii['id'], parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_name_child(self, name_id, parent_id):
        sql  = f'SELECT * FROM names WHERE id = {name_id}'
        sql += ' AND parent_id = {parent_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornName(row['name'], id=row['id'], parent_id=row['parent_id'])

    def get_full_name(self, name_id):
        sql = f'SELECT * FROM names WHERE id = \'{name_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        fullname = []
        fullname.append(row['name'])
        while row != None and row['parent_id'] != None:
            pid = row['parent_id']
            sql = f'SELECT * FROM names WHERE id = \'{pid}\''
            res = self.cursor.execute(sql)
            row = res.fetchone()
            if row != None:
                fullname.append(row['name'])
        return fullname

    def remove_name(self, name_id, parent_id):
        sql  = f'DELETE FROM names WHERE id = \'{name_id}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        self.db.commit()
        module_logger.debug(f'removed name: {name_id} of {parent_id}')
        return 

    def get_names(self):
        sql = f'SELECT * FROM names'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['name'])
        result = []
        for ii in rows:
            p = PlornName(ii['name'], id=ii['id'], parent_id=ii['parent_id'])
            result.append(p)
        return result

    def update_name(self, name, updated_name):
        sql  = f'UPDATE names'
        sql += f' SET name = \'{updated_name.get_name()}\','
        sql += f' parent_id = \'{updated_name.get_parent_id()}\''
        sql += f' WHERE id = \'{name.get_id()}\''
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = 'SELECT * FROM names'
        sql += f' WHERE id = \'{updated_name.get_id()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f'updated name: from {name.get_name()}'
        msg += f' to {row['name']}'
        module_logger.debug(msg)
        return PlornName(row['name'], id=row['id'], parent_id=row['parent_id'])

    def place_exists(self, place, parent_id=0):
        sql = f'SELECT * FROM places WHERE place = \'{place}\''
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        for ii in rows:
            if ii['parent_id'] == parent_id:
                return True
        return False

    def get_place_children(self, place_id):
        sql  = f'SELECT * FROM places WHERE parent_id = {place_id}'
        module_logger.debug(f'get_place_children: sql {sql} for {place_id}')
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        module_logger.debug(f'get_place_children: found {len(rows)} for {place_id}')
        result = []
        for ii in rows:
            p = PlornPlace(ii['place'], id=ii['id'], parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_full_place(self, place_id, parent_id=0):
        sql = f'SELECT * FROM places WHERE id = {place_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        fullplace = []
        fullplace.append(row['place'])
        while row != None and row['parent_id'] != 0:
            pid = row['parent_id']
            sql = f'SELECT * FROM places WHERE id = {pid}'
            res = self.cursor.execute(sql)
            row = res.fetchone()
            if row:
                fullplace.append(row['place'])
        return fullplace

    def get_places(self):
        sql = f'SELECT * FROM places'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['place'])
        module_logger.debug(f'get_places: {rows}')
        result = []
        for ii in rows:
            p = PlornPlace(ii['place'], id=ii['id'], parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_place_by_place(self, place, parent_id=0):
        sql  = f'SELECT * FROM places WHERE place = \'{place}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return row

    def get_place_object_by_place(self, place, parent_id=0):
        sql  = f'SELECT * FROM places WHERE place = \'{place}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f'place obj by place \'{place}\': {str(row)}')
        return PlornPlace(row['place'], id=row['id'],
                          parent_id=row['parent_id'])

    def remove_place(self, place_id, parent_id):
        sql  = f'DELETE FROM places WHERE id = \'{place_id}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        self.db.commit()
        module_logger.debug(f'removed place: {place_id} of {parent_id}')
        return 

    def update_place(self, place, updated_place):
        sql  = f'UPDATE places'
        sql += f' SET place = \'{updated_place.get_place()}\','
        sql += f' parent_id = \'{updated_place.get_parent_id()}\''
        sql += f' WHERE id = \'{place.get_id()}\''
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = 'SELECT * FROM places'
        sql += f' WHERE id = \'{updated_place.get_id()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f'updated place: from {place.get_place()}'
        msg += f' to {row['place']}'
        module_logger.debug(msg)
        return row['id']

    def add_attr(self, attr):
        db = QSqlDatabase.database()
        table_name = attr.get_db_table_name()
        value = attr.get_value()
        pid = attr.get_parent_id()
        if pid == None:
            pid = 0
        sql  = f'INSERT INTO {table_name} (value, parent_id) VALUES '
        sql += f'("{value}", "{pid}");'
        query = QSqlQuery(sql, db)
        db.commit()

        sql = f'SELECT * FROM {table_name} WHERE value = \'{value}\';'
        query = QSqlQuery(sql, db)
        query.next()
        module_logger.debug(f'added to {table_name}: {str(query.value(0))}')
        return query

    def add_name(self, name):
        query = self.add_attr(name)
        return PlornName(query.value(NameFields.VALUE),
                         id=query.value(NameFields.ID),
                         parent_id=query.value(NameFields.PARENT_ID))

    def add_place(self, place):
        query = self.add_attr(place)
        return PlornPlace(query.value(PlaceFields.VALUE),
                          id=query.value(PlaceFields.ID),
                          parent_id=query.value(PlaceFields.PARENT_ID))

    def add_tag(self, tag):
        query = self.add_attr(tag)
        return PlornTag(query.value(TagFields.VALUE),
                        id=query.value(TagFields.ID),
                        parent_id=query.value(TagFields.PARENT_ID))

    def attr_exists(self, attr):
        db = QSqlDatabase.database()
        table_name = attr.get_db_table_name()
        value = attr.get_value()
        sql = f'SELECT * FROM {table_name} WHERE value = \'{value}\';'
        query =QSqlQuery(sql, db)
        query.next()
        return query.value(0) != None

    def name_exists(self, name):
        return self.attr_exists(name)

    def place_exists(self, place):
        return self.attr_exists(place)

    def tag_exists(self, tag):
        return self.attr_exists(tag)

    def get_attr(self, attr_id, table_name):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM {table_name}  WHERE id = \'{attr_id}\';'
        query = QSqlQuery(sql, db)
        query.next()
        return query

    def get_name(self, name_id):
        query = self.get_attr(name_id, 'names')
        return PlornName(query.value(NameFields.VALUE),
                         id=query.value(NameFields.ID),
                         parent_id=query.value(NameFields.PARENT_ID))

    def get_place(self, place_id):
        query = self.get_attr(place_id, 'places')
        return PlornPlace(query.value(PlaceFields.VALUE),
                          id=query.value(PlaceFields.ID),
                          parent_id=query.value(PlaceFields.PARENT_ID))

    def get_tag(self, tag_id):
        query = self.get_attr(tag_id, 'tags')
        return PlornTag(query.value(TagFields.VALUE),
                        id=query.value(TagFields.ID),
                        parent_id=query.value(TagFields.PARENT_ID))

    def get_attr_children(self, attr):
        db = QSqlDatabase.database()
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'SELECT * FROM {table_name} WHERE parent_id = {attr_id};'
        query = QSqlQuery(sql, db)
        return query

    def get_name_children(self, name):
        query = self.get_attr_children(name)
        result = []
        while query.next():
            p = PlornName(query.value(AttrFields.VALUE),
                          id=query.value(AttrFields.ID),
                          parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def get_place_children(self, place):
        query = self.get_attr_children(place)
        result = []
        while query.next():
            p = PlornPlace(query.value(AttrFields.VALUE),
                           id=query.value(AttrFields.ID),
                           parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def get_tag_children(self, tag):
        query = self.get_attr_children(tag)
        result = []
        while query.next():
            p = PlornTag(query.value(AttrFields.VALUE),
                         id=query.value(AttrFields.ID),
                         parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def get_full_attr(self, attr):
        db = QSqlDatabase.database()
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        attr_pid = attr.get_parent_id()
        sql = f'SELECT * FROM {table_name} WHERE id = \'{attr_id}\';'
        query = QSqlQuery(sql, db)
        query.next()
        fullattr = []
        fullattr.append(query.value(AttrFields.VALUE))
        while query.value(AttrFields.PARENT_ID) != 0:
            pid = query.value(AttrFields.PARENT_ID)
            sql = f'SELECT * FROM {table_name} WHERE id = \'{pid}\';'
            query.exec(sql)
            query.next()
            if query.value(AttrFields.ID) != None:
                fullattr.append(query.value(AttrFields.VALUE))
        return fullattr

    def get_full_name(self, name):
        fullattr = self.get_full_attr(name)
        return fullattr[::-1]

    def get_full_place(self, place):
        fullattr = self.get_full_attr(place)
        return fullattr[::-1]

    def get_full_tag(self, tag):
        fullattr = self.get_full_attr(tag)
        return fullattr[::-1]

    def get_all_attrs(self, table_name=''):
        db = QSqlDatabase.database()
        sql = f'SELECT * FROM {table_name};'
        query = QSqlQuery(sql, db)
        return query

    def get_all_names(self):
        query = self.get_all_attrs('names')
        result = []
        while query.next():
            p = PlornName(query.value(AttrFields.VALUE),
                          id=query.value(AttrFields.ID),
                          parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def get_all_places(self):
        query = self.get_all_attrs('places')
        result = []
        while query.next():
            p = PlornPlace(query.value(AttrFields.VALUE),
                           id=query.value(AttrFields.ID),
                           parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def get_all_tags(self):
        query = self.get_all_attrs('tags')
        result = []
        while query.next():
            p = PlornTag(query.value(AttrFields.VALUE),
                         id=query.value(AttrFields.ID),
                         parent_id=query.value(AttrFields.PARENT_ID))
            result.append(p)
        return result

    def remove_attr(self, attr):
        db = QSqlDatabase.database()
        query = self.get_all_attrs('names')
        db.transaction()
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'DELETE FROM {table_name} WHERE id = \'{attr_id}\';'
        query = QSqlQuery(sql, db)
        db.commit()
        module_logger.debug(f'removed attr: {attr_id} from {table_name}')
        return query

    def remove_name(self, name):
        return self.remove_attr(name)

    def remove_place(self, place):
        return self.remove_attr(place)

    def remove_tag(self, tag):
        return self.remove_attr(tag)

    def update_attr(self, attr, updated_attr):
        db = QSqlDatabase.database()
        db.transaction()
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'UPDATE {table_name}'
        sql += f' SET value = \'{updated_attr.get_value()}\','
        sql += f' parent_id = \'{updated_attr.get_parent_id()}\''
        sql += f' WHERE id = \'{attr.get_id()}\';'
        query = QSqlQuery(sql, db)
        db.commit()

        sql  = f'SELECT * FROM {table_name}'
        sql += f' WHERE id = \'{updated_attr.get_id()}\';'
        query = QSqlQuery(sql, db)
        query.next()
        msg = f'updated attr from {attr.get_value()}'
        msg += f' to {query.value(AttrFields.VALUE)}'
        module_logger.debug(msg)
        return query.value(AttrFields.ID)

    def update_name(self, name, updated_name):
        return self.update_attr(name, updated_name)

    def update_place(self, place, updated_place):
        return self.update_attr(place, updated_place)

    def update_tag(self, tag, updated_tag):
        return self.update_attr(tag, updated_tag)

    def get_name_ids_for_album(self, album):
        sql  = f'SELECT * FROM album_names'
        sql += f' WHERE album_id = {album.get_id()}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(ii['name_id'])
        return result

    def get_names_for_album_by_id(self, album_id):
        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM album_names'
        sql += f' WHERE album_id = {album_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_name(query.value(NameFields.VALUE)))
        return result

    def get_names_for_album(self, album):
        if not album:
            return []
        return self.get_names_for_album_by_id(album.get_id())

    def get_places_for_album_by_id(self, album_id):
        global module_logger

        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM album_places'
        sql += f' WHERE album_id = {album_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_place(query.value(PlaceFields.VALUE)))
        return result

    def get_places_for_album(self, album):
        if not album:
            return []
        return self.get_places_for_album_by_id(album.get_id())

    def get_tags_for_album_by_id(self, album_id):
        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM album_tags'
        sql += f' WHERE album_id = {album_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_tag(query.value(TagFields.VALUE)))
        return result

    def get_tags_for_album(self, album):
        if not album:
            return []
        return self.get_tags_for_album_by_id(album.get_id())

    def get_names_for_photo_by_id(self, photo_id):
        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM photo_names'
        sql += f' WHERE photo_id = {photo_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_name(query.value(NameFields.VALUE)))
        return result

    def get_names_for_photo(self, photo):
        if not photo:
            return []
        return self.get_names_for_photo_by_id(photo.get_id())

    def get_places_for_photo_by_id(self, photo_id):
        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM photo_places'
        sql += f' WHERE photo_id = {photo_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_name(query.value(PlaceFields.VALUE)))
        return result

    def get_places_for_photo(self, photo):
        if not photo:
            return []
        return self.get_places_for_photo_by_id(photo.get_id())

    def get_tags_for_photo_by_id(self, photo_id):
        db = QSqlDatabase.database()
        sql  = f'SELECT * FROM photo_tags'
        sql += f' WHERE photo_id = {photo_id};'
        query = QSqlQuery(sql, db)
        result = []
        while query.next():
            result.append(self.get_name(query.value(TagFields.VALUE)))
        return result

    def get_tags_for_photo(self, photo):
        if not photo:
            return []
        return self.get_tags_for_photo_by_id(photo.get_id())

    def get_raw_names_table(self):
        sql  = f'SELECT * FROM names'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        return rows

    def get_raw_places_table(self):
        sql  = f'SELECT * FROM places'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        return rows

    def get_raw_tags_table(self):
        sql  = f'SELECT * FROM tags'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        return rows

