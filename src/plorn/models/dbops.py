#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os.path

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
)

from plorn.config import PlornConfig

from plorn import (
    AlbumFields,
    AttrFields,
    ObjAttrFields,
    PhotoFields,
    PlornAlbum,
    PlornDbException,
    PlornName,
    PlornPhoto,
    PlornPlace,
    PlornTag,
)

module_logger = logging.getLogger('plorn.model.dbops')
module_logger.setLevel(logging.DEBUG)


##########################################################################
#
#   static class for direct database access -- these are helper functions
#   to populate the various models
#

_current_db = None

class PlornDbOperations:
    '''
    wrapper for all the necessary operations on the QSqlDatabase
    '''
    def __init__(self):
        pass                # there are no non-static methods

    @staticmethod
    def initialize(db):                 # open QSqlDatabase connection
        global _current_db

        if _current_db:
            if db and db.connectionName() == _current_db.connectionName():
                return _current_db

        if db and db.isOpen() and db.isValid():
            db = db
            _current_db = db
            PlornDbOperations.create_tables()
            return _current_db

        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        if catalog not in QSqlDatabase.connectionNames():
            db = QSqlDatabase.addDatabase('QSQLITE', connectionName=catalog)
            dbpath = os.path.expanduser(os.path.join(datadir, dbname))
            db.setDatabaseName(dbpath)
            db.open()
            _current_db = db
            PlornDbOperations.create_tables()

        elif catalog in QSqlDatabase.connectionNames():
            db = QSqlDatabase.database(connectionName=catalog)
            db.open()
            _current_db = db

        else:
            raise PlornDbException(f'{db.connectionName()} is not valid')

        return _current_db

    @staticmethod
    def close(db):
        global _current_db

        if db and db.connectionName() == _current_db.connectionName():
            _current_db.close()
            _current_db = QSqlDatabase.database()

    @staticmethod
    def create_tables():
        global module_logger

        PlornDbOperations.create_config_table()
        PlornDbOperations.create_albums_table()
        PlornDbOperations.create_photos_table()
        for ii in ['names', 'places', 'tags']:
            PlornDbOperations.create_attr_table(ii)
            for jj in ['albums', 'photos']:
                PlornDbOperations.create_obj_attr_table(jj, ii)
        #module_logger.debug(f'created tables: {_current_db.tables()}')

    @staticmethod
    def create_config_table():
        global _current_db

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS config (
                name text NOT NULL,
                version text,
                username text,
                fullname text
            );
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)
        
        cfgq = QSqlQuery('SELECT * FROM config;', db=_current_db)
        count = 0
        while cfgq.next():
            count += 1
        if count < 1:
            config = PlornConfig()
            sql = 'INSERT INTO config VALUES ("plorn", '
            sql += f'"{config.get_version()}", '
            sql += f'"{config.get_username()}", '
            sql += f'"{config.get_fullname()}");'
            cfgadd = QSqlQuery(sql, db=_current_db)

    @staticmethod
    def create_albums_table():
        global _current_db

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY,
                name text NOT NULL,
                dated text,
                notes text,
                photo_count INT
            );
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)

    @staticmethod
    def create_photos_table():
        global _current_db

        sql_stmt = '''
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
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)

    @staticmethod
    def create_attr_table(table_name):
        global _current_db

        sql_stmt = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                parent_id INT DEFAULT 0,
                value TEXT,
                FOREIGN KEY (parent_id)
                REFERENCES {table_name} (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)

    @staticmethod
    def create_obj_attr_table(obj_name, attr_name):
        global _current_db

        obj = obj_name
        if obj_name[-1] == 's':
            obj = obj_name[0:-1]
        attr = attr_name
        if attr_name[-1] == 's':
            attr = attr_name[0:-1]
        sql_stmt = f'''
            CREATE TABLE IF NOT EXISTS {obj}_{attr_name} (
                id INTEGER PRIMARY KEY,
                {obj}_id INT NOT NULL,
                {attr}_id INT NOT NULL,
                FOREIGN KEY ({obj}_id)
                REFERENCES {obj_name} (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                FOREIGN KEY ({attr}_id)
                REFERENCES {attr_name} (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)
        #if not query.isActive():
        #    raise PlornDbException(f'cannot create {table_name} table')

    @staticmethod
    def truncate_tables():
        global _current_db

        query = QSqlQuery(f'DELETE FROM albums;', db=_current_db)
        query = QSqlQuery(f'DELETE FROM photos;', db=_current_db)
        for ii in ['names', 'places', 'tags']:
            query = QSqlQuery(f'DELETE FROM {ii};', db=_current_db)
            for jj in ['album', 'photo']:
                query = QSqlQuery(f'DELETE FROM {jj}_{ii};', db=_current_db)

    @staticmethod
    def get_config(self):
        global _current_db

        query = QSqlQuery(f'SELECT * FROM config;', db=_current_db)
        return query.next()

#    def album_exists(self, album):
#        sql = f'SELECT * FROM albums WHERE name = \'{album.get_name()}\''
#        res = self.cursor.execute(sql)
#        rows = res.fetchone()
#        return rows != None

#    def photo_exists(self, photo):
#        sql = f'SELECT * FROM photos WHERE id = \'{photo.get_id()}\''
#        res = self.cursor.execute(sql)
#        rows = res.fetchone()
#        return rows != None

    @staticmethod
    def add_album_name_list(album):
        global module_logger, _current_album

        res = False
        if len(album.get_name_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_names (name_id, album_id) VALUES '
            for ii in album.get_name_list():
                module_logger.debug(f'static add_album_name list {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_album_name_list(album):
        global module_logger, _current_album
        sql = f'DELETE FROM album_names WHERE album_id = {album.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_photo_name_list(photo):
        global module_logger, _current_album

        res = False
        if len(photo.get_name_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_names (name_id, photo_id) VALUES '
            for ii in photo.get_name_list():
                msg  = f'static add_photo_name list '
                msg += f'{ii.get_value()}: {ii.get_id()}, {photo_id}'
                module_logger.debug(msg)
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            msg  = f'static add_photo_name list sql "{sql}"'
            module_logger.debug(msg)
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_photo_name_list(photo):
        global module_logger, _current_album
        sql = f'DELETE FROM photo_names WHERE photo_id = {photo.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_album_place_list(album):
        global _current_db

        res = False
        if len(album.get_place_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_places (place_id, album_id) VALUES '
            for ii in album.get_place_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_album_place_list(album):
        global module_logger, _current_album
        sql = f'DELETE FROM album_places WHERE album_id = {album.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_photo_place_list(photo):
        global module_logger, _current_album

        res = False
        if len(photo.get_place_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_places (place_id, photo_id) VALUES '
            for ii in photo.get_place_list():
                module_logger.debug(f'static add_photo_place list {ii.get_value()}: {ii.get_id()}, {photo_id}')
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_photo_place_list(photo):
        global module_logger, _current_album
        sql = f'DELETE FROM photo_places WHERE photo_id = {photo.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_album_tag_list(album):
        global _current_db

        res = False
        if len(album.get_tag_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_tags (tag_id, album_id) VALUES '
            for ii in album.get_tag_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_album_tag_list(album):
        global module_logger, _current_album
        sql = f'DELETE FROM album_tags WHERE album_id = {album.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_photo_tag_list(photo):
        global module_logger, _current_album

        res = False
        if len(photo.get_tag_list()) > 0:
            photo_id = photo.get_id()
            sql  = 'INSERT INTO photo_tags (tag_id, photo_id) VALUES '
            for ii in photo.get_tag_list():
                module_logger.debug(f'static add_photo_tag list {ii.get_value()}: {ii.get_id()}, {photo_id}')
                sql += f'({ii.get_id()}, {photo_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    @staticmethod
    def remove_photo_tag_list(photo):
        global module_logger, _current_album
        sql = f'DELETE FROM photo_tags WHERE photo_id = {photo.get_id()};'
        return QSqlQuery(sql, db=_current_db)

    @staticmethod
    def add_album(album):
        global module_logger, _current_db

        module_logger.debug('static add_album: entered')
        sql = 'INSERT INTO albums (name,dated,notes,photo_count) VALUES '
        sql += f'("{album.get_name()}", '
        sql += f' "{album.get_dated()}", '
        sql += f' "{album.get_notes()}", '
        sql += f' {album.get_photo_count()}'
        sql += f');'
        query = QSqlQuery(sql, db=_current_db)
        module_logger.debug(f'static add_album: album is {str(album)}')

        sql = f'SELECT * FROM albums WHERE name = "{album.get_name()}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            id = query.value(AlbumFields.ID)
            album.set_id(id)
            module_logger.debug('static add_album: adding attr lists')
            PlornDbOperations.add_album_name_list(album)
            PlornDbOperations.add_album_place_list(album)
            PlornDbOperations.add_album_tag_list(album)
            module_logger.debug(f'static add_album: attr lists done, album {str(album)}')

        else:
            msg  = f'cannot add album {album.get_name()}'
            msg += f'\n{query.lastError().text()}'
            raise PlornDbException(msg)

        module_logger.debug('static add_album: done')
        return album

#    def get_album(self, album_id):
#        return self.get_album_by_id(album_id)

    @staticmethod
    def get_album_by_name(album_name):
        global module_logger, _current_db

        module_logger.debug(f'static get_album_by_name: getting {album_name}')
        album = None
        sql = f'SELECT * FROM albums WHERE name = "{album_name}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            album_id = query.value(AlbumFields.ID)
            names = PlornDbOperations.get_names_for_album_by_id(album_id)
            places = PlornDbOperations.get_places_for_album_by_id(album_id)
            tags = PlornDbOperations.get_tags_for_album_by_id(album_id)
            album = PlornAlbum(query.value(AlbumFields.NAME),
                               id=query.value(AlbumFields.ID),
                               dated=query.value(AlbumFields.DATED),
                               notes=query.value(AlbumFields.NOTES),
                               names=names, places=places, tags=tags)
        module_logger.debug(f'static get_album_by_name: done, album is {str(album)}')
        return album

    @staticmethod
    def get_album_by_id(album_id):
        global module_logger, _current_db

        album = None
        sql = f'SELECT * FROM albums WHERE id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            album_id = query.value(AlbumFields.ID)
            names = PlornDbOperations.get_names_for_album_by_id(album_id)
            places = PlornDbOperations.get_places_for_album_by_id(album_id)
            tags = PlornDbOperations.get_tags_for_album_by_id(album_id)
            album = PlornAlbum(query.value(AlbumFields.NAME),
                               id=query.value(AlbumFields.ID),
                               dated=query.value(AlbumFields.DATED),
                               notes=query.value(AlbumFields.NOTES),
                               photo_count=query.value(AlbumFields.PHOTO_COUNT),
                               names=names, places=places, tags=tags)
        return album

    @staticmethod
    def remove_album_by_id(album_id):
        global module_logger, _current_db

        module_logger.debug(f'remove_album_by_id: entered, id {album_id}')
        module_logger.debug(f'remove_album_by_id: tables {_current_db.tables()}')

        res = False
        _current_db.transaction()
        sql = f'DELETE FROM albums WHERE id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        sql = f'DELETE FROM photos WHERE album_id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        sql = f'DELETE FROM album_names WHERE album_id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        sql = f'DELETE FROM album_places WHERE album_id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        sql = f'DELETE FROM album_tags WHERE album_id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        module_logger.debug(f'remove_album_by_id: done, id {album_id}')
        res = _current_db.commit()
        return res 

    @staticmethod
    def remove_album(album):
        return PlornDbOperations.remove_album_by_id(album.get_id())

#    def add_name_to_album_by_id(self, name_id, album_id):
#        sql  = 'INSERT INTO album_names '
#        sql += '(name_id, album_id) '
#        sql += f'VALUES ({name_id}, {album_id})'
#        res = self.cursor.execute(sql)

#    def remove_name_from_album_by_id(self, name_id, album_id):
#        sql  = 'DELETE FROM album_names'
#        sql += f' WHERE name_id = {name_id} AND album_id = {album_id}'
#        res = self.cursor.execute(sql)

#    def add_place_to_album_by_id(self, place_id, album_id):
#        sql  = 'INSERT INTO album_places '
#        sql += '(place_id, album_id) '
#        sql += f'VALUES ({place_id}, {album_id})'
#        res = self.cursor.execute(sql)

#    def remove_place_from_album_by_id(self, place_id, album_id):
#        sql  = 'DELETE FROM album_places'
#        sql += f' WHERE place_id = {place_id} AND album_id = {album_id}'
#        res = self.cursor.execute(sql)

#    def add_tag_to_album_by_id(self, tag_id, album_id):
#        sql  = 'INSERT INTO album_tags '
#        sql += '(tag_id, album_id) '
#        sql += f'VALUES ({tag_id}, {album_id})'
#        res = self.cursor.execute(sql)

#    def remove_tag_from_album_by_id(self, tag_id, album_id):
#        sql  = 'DELETE FROM album_tags'
#        sql += f' WHERE tag_id = {tag_id} AND album_id = {album_id}'
#        res = self.cursor.execute(sql)

    @staticmethod
    def update_album(album, updated_album):
        global module_logger, _current_db

        module_logger.debug(f'update_album: entered, id {album.get_id()}')
        PlornDbOperations.remove_album_name_list(album)
        PlornDbOperations.add_album_name_list(updated_album)
        PlornDbOperations.remove_album_place_list(album)
        PlornDbOperations.add_album_place_list(updated_album)
        PlornDbOperations.remove_album_tag_list(album)
        PlornDbOperations.add_album_tag_list(updated_album)

        sql  = f'UPDATE albums'
        sql += f' SET name = "{updated_album.get_name()}",'
        sql += f' dated = "{updated_album.get_dated()}",'
        sql += f' notes = "{updated_album.get_notes()}",'
        sql += f' photo_count = {updated_album.get_photo_count()}'
        sql += f' WHERE id = {album.get_id()};'
        query = QSqlQuery(sql, db=_current_db)

        return PlornDbOperations.get_album_by_id(updated_album.get_id())

    @staticmethod
    def get_photo_row_by_id(photo_id):
        global module_logger, _current_db

        row = {}
        sql = f'SELECT * FROM photos WHERE id = {photo_id};'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            row['id'] = query.value(PhotoFields.ID)
            row['album_id'] = query.value(PhotoFields.ALBUM_ID)
            row['photo'] = query.value(PhotoFields.NAME)
            row['path'] = query.value(PhotoFields.PATH)
            row['dated'] = query.value(PhotoFields.DATED)
            row['notes'] = query.value(PhotoFields.NOTES)
            row['names'] = PlornDbOperations.get_names_for_photo_by_id(photo_id)
            row['places'] = \
                          PlornDbOperations.get_places_for_photo_by_id(photo_id)
            row['tags'] = PlornDbOperations.get_tags_for_photo_by_id(photo_id)
        return row

    @staticmethod
    def get_photo_by_id(photo_id):
        global module_logger, _current_db

        row = PlornDbOperations.get_photo_row_by_id(photo_id)
        p = PlornPhoto(row['photo'], id=row['id'],
                                   album_id=row['album_id'],
                                   path=row['path'], dated=row['dated'],
                                   notes=row['notes'])
        p.set_name_list(row['names'])
        p.set_place_list(row['places'])
        p.set_tag_list(row['tags'])
        return p

#    def get_photo(self, photo_id):
#        return self.get_photo_by_id(photo_id)

    @staticmethod
    def get_photo_by_album_and_path(album_id, path):
        global module_logger, _current_db

        sql  = 'SELECT * FROM photos WHERE '
        sql += f'path = "{path}" AND album_id = "{album_id}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            photo_id = query.value(PhotoFields.ID)
            photo = PlornPhoto(query.value(PhotoFields.NAME),
                               id=photo_id,
                               album_id=query.value(PhotoFields.ALBUM_ID),
                               path=query.value(PhotoFields.PATH),
                               dated=query.value(PhotoFields.DATED),
                               notes=query.value(PhotoFields.NOTES))
            names = PlornDbOperations.get_names_for_photo_by_id(photo_id)
            photo.set_name_list(names)
            places = PlornDbOperations.get_places_for_photo_by_id(photo_id)
            photo.set_place_list(places)
            tags = PlornDbOperations.get_tags_for_photo_by_id(photo_id)
            photo.set_tag_list(tags)
            return photo

        return None
            

    @staticmethod
    def increment_photo_count(album):
        album_copy = album
        album_copy.set_photo_count(album.get_photo_count() + 1)
        PlornDbOperations.update_album(album, album_copy)

    @staticmethod
    def decrement_photo_count(album):
        album_copy = album
        album_copy.set_photo_count(album.get_photo_count() - 1)
        PlornDbOperations.update_album(album, album_copy)

    @staticmethod
    def add_photo(photo):
        global module_logger, _current_db

        album = PlornDbOperations.get_album_by_id(photo.get_album_id())
        sql  = 'INSERT INTO photos '
        sql += f'(album_id,name,path,dated,notes) VALUES '
        sql += f'("{photo.get_album_id()}",'
        sql += f' "{photo.get_name()}", "{photo.get_path()}",'
        sql += f' "{photo.get_dated()}", "{photo.get_notes()}");'
        query = QSqlQuery(sql, db=_current_db)
        PlornDbOperations.increment_photo_count(album)

        sql  = f'SELECT * FROM photos WHERE path = "{photo.get_path()}" '
        sql += f'AND album_id = "{photo.get_album_id()}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            id = query.value(PhotoFields.ID)
            photo.set_id(id)
            module_logger.debug('static add_photo: adding attr lists')
            PlornDbOperations.add_photo_name_list(photo)
            PlornDbOperations.add_photo_place_list(photo)
            PlornDbOperations.add_photo_tag_list(photo)
            module_logger.debug(f'static add_photo: attr lists done, photo {str(photo)}')

        else:
            msg  = f'cannot add photo {photo.get_name()}'
            msg += f'\n{query.lastError().text()}'
            raise PlornDbException(msg)

        module_logger.debug('static add_photo: done')
        return photo

    @staticmethod
    def remove_photo(photo_id, path=''):
        return PlornDbOperations.remove_photo_by_id(photo_id, path)

    @staticmethod
    def remove_photo_by_id(photo_id):
        global module_logger, _current_db

        photo = PlornDbOperations.get_photo_by_id(photo_id)
        album = PlornDbOperations.get_album_by_id(photo.get_album_id())
        sql = f'SELECT * FROM photos WHERE id = "{photo_id}";'
        res = False
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            album_id = query.value(PhotoFields.ALBUM_ID)
            sql = f'DELETE FROM photos WHERE id = "{photo_id}";'
            query = QSqlQuery(sql, db=_current_db)
            sql = f'DELETE FROM photo_names WHERE photo_id = "{photo_id}";'
            query = QSqlQuery(sql, db=_current_db)
            sql = f'DELETE FROM photo_places WHERE photo_id = "{photo_id}";'
            query = QSqlQuery(sql, db=_current_db)
            sql = f'DELETE FROM photo_tags WHERE photo_id = "{photo_id}";'
            query = QSqlQuery(sql, db=_current_db)
            album = PlornDbOperations.get_album_by_id(album_id)
            PlornDbOperations.decrement_photo_count(album)
            res = _current_db.commit()
        return res

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

    def get_name(self, name_id, parent_id=0):
        sql = f'SELECT * FROM names WHERE id = \'{name_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_name_by_name(self, name, parent_id=0):
        sql  = f'SELECT * FROM names WHERE name = \'{name}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_name_children(self, name_id):
        sql = f'SELECT * FROM names WHERE parent_id = {name_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            p = PlornName(ii['name'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_name_child(self, name_id, parent_id):
        sql  = f'SELECT * FROM names WHERE id = {name_id}'
        sql += ' AND parent_id = {parent_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

    @staticmethod
    def get_full_attr(table='names', id=0):
        global _current_db

        sql = f'SELECT * from {table} WHERE id = {id};'
        fullattr = []
        query = QSqlQuery(sql, db=_current_db)
        while query.next() and query.value(AttrFields.PARENT_ID) != None:
            fullattr.append(query.value(AttrFields.VALUE))
            pid = query.value(AttrFields.PARENT_ID)
            sql = f'SELECT * from {table} WHERE id = {pid};'
            query = QSqlQuery(sql, db=_current_db)
        return fullattr[::-1]

    def remove_name(self, name_id, parent_id):
        sql  = f'DELETE FROM names WHERE id = \'{name_id}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        self.db.commit()
        return 

    def get_names(self):
        sql = f'SELECT * FROM names'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['name'])
        result = []
        for ii in rows:
            p = PlornName(ii['name'], id=ii['id'],
                                     parent_id=ii['parent_id'])
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
        return PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

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
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            p = PlornPlace(ii['place'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_places(self):
        sql = f'SELECT * FROM places'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['place'])
        result = []
        for ii in rows:
            p = PlornPlace(ii['place'], id=ii['id'],
                                       parent_id=ii['parent_id'])
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
        return PlornPlace(row['place'], id=row['id'],
                                     parent_id=row['parent_id'])

    def remove_place(self, place_id, parent_id):
        sql  = f'DELETE FROM places WHERE id = \'{place_id}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        self.db.commit()
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
        return row['id']

    @staticmethod
    def add_attr(attr):
        global module_logger, _current_db

        table_name = attr.get_db_table_name()
        sql = f'INSERT INTO {table_name} (value, parent_id) VALUES '
        value = attr.get_value()
        pid = attr.get_parent_id()
        if pid == None:
            pid = 0
        sql += f'(\'{value}\', \'{pid}\');'
        query = QSqlQuery(sql, db=_current_db)
        row = {}
        sql = f'SELECT * FROM {table_name} WHERE value = "{value}";'
        query = QSqlQuery(sql, db=_current_db)
        if query.next():
            row['id'] = query.value(AttrFields.ID)
            row['parent_id'] = query.value(AttrFields.PARENT_ID)
            row['value'] = query.value(AttrFields.VALUE)
        return row

    @staticmethod
    def add_name(name):
        row = PlornDbOperations.add_attr(name)
        if len(row) > 0:
            return PlornName(row['value'], id=row['id'],
                             parent_id=row['parent_id'])
        return None

    @staticmethod
    def add_place(place):
        row = PlornDbOperations.add_attr(place)
        if len(row) > 0:
            return PlornPlace(row['value'], id=row['id'],
                              parent_id=row['parent_id'])
        return None

    @staticmethod
    def add_tag(tag):
        row = PlornDbOperations.add_attr(tag)
        if len(row) > 0:
            return PlornTag(row['value'], id=row['id'],
                            parent_id=row['parent_id'])
        return None

    @staticmethod
    def attr_exists(attr):
        global module_logger, _current_db

        table_name = attr.get_db_table_name()
        value = attr.get_value()
        sql = f'SELECT * FROM {table_name} WHERE value = "{value}";'
        query = QSqlQuery(sql, db=_current_db)
        return query.next()

    @staticmethod
    def name_exists(name):
        return PlornDbOperations.attr_exists(name)

    @staticmethod
    def place_exists(place):
        return PlornDbOperations.attr_exists(place)

    @staticmethod
    def tag_exists(tag):
        return PlornDbOperations.attr_exists(tag)

    @staticmethod
    def get_attr(attr_id, table_name):
        global module_logger, _current_db

        sql = f'SELECT * FROM {table_name}  WHERE id = "{attr_id}";'
        query = QSqlQuery(sql, db=_current_db)
        row = {}
        if query.next():
            row['id'] = query.value(AttrFields.ID)
            row['parent_id'] = query.value(AttrFields.PARENT_ID)
            row['value'] = query.value(AttrFields.VALUE)
        return row

    @staticmethod
    def get_name(name_id):
        row = PlornDbOperations.get_attr(name_id, 'names')
        if len(row) > 0:
            return PlornName(row['value'], id=row['id'],
                             parent_id=row['parent_id'])
        return None

    @staticmethod
    def get_place(place_id):
        row = PlornDbOperations.get_attr(place_id, 'places')
        if len(row) > 0:
            return PlornPlace(row['value'], id=row['id'],
                              parent_id=row['parent_id'])
        return None

    @staticmethod
    def get_tag(tag_id):
        row = PlornDbOperations.get_attr(tag_id, 'tags')
        if len(row) > 0:
            return PlornTag(row['value'], id=row['id'],
                            parent_id=row['parent_id'])
        return None

    def get_attr_children(self, attr):
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'SELECT * FROM {table_name} WHERE parent_id = {attr_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        return rows

    def get_name_children(self, name):
        rows = self.get_attr_children(name)
        result = []
        for ii in rows:
            p = PlornName(ii['value'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_place_children(self, place):
        rows = self.get_attr_children(place)
        result = []
        for ii in rows:
            p = PlornPlace(ii['value'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_tag_children(self, tag):
        rows = self.get_attr_children(tag)
        result = []
        for ii in rows:
            p = PlornTag(ii['value'], id=ii['id'],
                                    parent_id=ii['parent_id'])
            result.append(p)
        return result

    @staticmethod
    def get_all_attrs(table_name=''):
        global module_logger, _current_db

        sql = f'SELECT * FROM {table_name};'
        query = QSqlQuery(sql, db=_current_db)
        rows = []
        while query.next():
            row = {}
            row['id'] = query.value(AttrFields.ID)
            row['parent_id'] = query.value(AttrFields.PARENT_ID)
            row['value'] = query.value(AttrFields.VALUE)
            rows.append(row)
        rows.sort(key=lambda x: x['value'])
        return rows

    @staticmethod
    def get_all_names(self):
        rows = self.get_all_attrs('names')
        result = []
        for ii in rows:
            p = PlornName(ii['value'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    @staticmethod
    def get_all_places(self):
        rows = self.get_all_attrs('places')
        result = []
        for ii in rows:
            p = PlornPlace(ii['value'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

    @staticmethod
    def get_all_tags(self):
        rows = self.get_all_attrs('tags')
        result = []
        for ii in rows:
            p = PlornTag(ii['value'], id=ii['id'],
                                    parent_id=ii['parent_id'])
            result.append(p)
        return result

    def remove_attr(self, attr):
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'DELETE FROM {table_name} WHERE id = \'{attr_id}\''
        res = self.cursor.execute(sql)
        self.db.commit()
        return 

    def remove_name(self, name):
        return self.remove_attr(name)

    def remove_place(self, place):
        return self.remove_attr(place)

    def remove_tag(self, tag):
        return self.remove_attr(tag)

    def update_attr(self, attr, updated_attr):
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'UPDATE {table_name}'
        sql += f' SET value = \'{updated_attr.get_value()}\','
        sql += f' parent_id = \'{updated_attr.get_parent_id()}\''
        sql += f' WHERE id = \'{attr.get_id()}\''
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = f'SELECT * FROM {table_name}'
        sql += f' WHERE id = \'{updated_attr.get_id()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f'updated attr from {attr.get_value()}'
        msg += f' to {row['value']}'
        return row['id']

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

    @staticmethod
    def _get_obj_attr_by_id(obj_name, attr_name, id):
        global module_logger, _current_db

        msg  = '_get_obj_attr_by_id: entering with '
        msg += f'{obj_name}, {attr_name}, {id}'
        module_logger.debug(msg)
        sql  = f'SELECT * FROM {obj_name}_{attr_name} '
        sql += f'WHERE {obj_name}_id = {id};'
        query = QSqlQuery(sql, db=_current_db)
        result = []
        while query.next():
            result.append([query.value(ObjAttrFields.ID),
                           query.value(ObjAttrFields.OBJECT_ID),
                           query.value(ObjAttrFields.ATTR_ID)])
        module_logger.debug('_get_obj_attr_by_id: done')
        return result

    @staticmethod
    def get_names_for_album_by_id(album_id):
        rows = PlornDbOperations._get_obj_attr_by_id('album','names',album_id)
        names = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_name(attr_id)
            name = PlornName(obj.get_value(), id=obj.get_id(),
                             parent_id=obj.get_parent_id())
            names.append(name)
        return names

    @staticmethod
    def get_names_for_album(album):
        if not album:
            return []
        return PlornDbOperations.get_names_for_album_by_id(album.get_id())

    @staticmethod
    def get_places_for_album_by_id(album_id):
        rows = PlornDbOperations._get_obj_attr_by_id('album','places',album_id)
        places = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_place(attr_id)
            place = PlornPlace(obj.get_value(), id=obj.get_id(),
                               parent_id=obj.get_parent_id())
            places.append(place)
        return places

    @staticmethod
    def get_places_for_album(album):
        if not album:
            return []
        return PlornDbOperations.get_places_for_album_by_id(album.get_id())

    @staticmethod
    def get_tags_for_album_by_id(album_id):
        rows = PlornDbOperations._get_obj_attr_by_id('album','tags',album_id)
        tags = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_tag(attr_id)
            tag = PlornPlace(obj.get_value(), id=obj.get_id(),
                             parent_id=obj.get_parent_id())
            tags.append(tag)
        return tags

    @staticmethod
    def get_tags_for_album(album):
        if not album:
            return []
        return PlornDbOperations.get_tags_for_album_by_id(album.get_id())

    @staticmethod
    def get_names_for_photo_by_id(photo_id):
        rows = PlornDbOperations._get_obj_attr_by_id('photo','names',photo_id)
        names = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_name(attr_id)
            name = PlornName(obj.get_value(), id=obj.get_id(),
                             parent_id=obj.get_parent_id())
            names.append(name)
        return names

    @staticmethod
    def get_names_for_photo(photo):
        if not photo:
            return []
        return PlornDbOperations.get_names_for_photo_by_id(photo.get_id())

    @staticmethod
    def get_places_for_photo_by_id(photo_id):
        rows = PlornDbOperations._get_obj_attr_by_id('photo','places',photo_id)
        places = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_place(attr_id)
            place = PlornPlace(obj.get_value(), id=obj.get_id(),
                               parent_id=obj.get_parent_id())
            places.append(place)
        return places

    @staticmethod
    def get_places_for_photo(photo):
        if not photo:
            return []
        return PlornDbOperations.get_places_for_photo_by_id(photo.get_id())

    @staticmethod
    def get_tags_for_photo_by_id(photo_id):
        rows = PlornDbOperations._get_obj_attr_by_id('photo','tags',photo_id)
        tags = []
        for id, obj_id, attr_id in rows:
            obj = PlornDbOperations.get_tag(attr_id)
            tag = PlornPlace(obj.get_value(), id=obj.get_id(),
                             parent_id=obj.get_parent_id())
            tags.append(tag)
        return tags

    @staticmethod
    def get_tags_for_photo(photo):
        if not photo:
            return []
        return PlornDbOperations.get_tags_for_photo_by_id(photo.get_id())

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

