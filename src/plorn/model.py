#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

from enum import IntEnum
import logging
import os.path
import sys
import traceback

from PyQt6.QtCore import (
    QModelIndex,
    Qt,
)

from PyQt6.QtGui import (
    QFont,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlRelation,
    QSqlTableModel,
    QSqlRelationalTableModel,
    QSqlQuery,
)

from PyQt6.QtWidgets import (
    QTreeWidgetItem,
)

from plorn.config import PlornConfig
from plorn import (
    PlornAlbum,
    AlbumFields,
    AttrFields,
    PhotoFields,
    PlornDbException,
)

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.DEBUG)


##########################################################################
#
#   data model for Albums -- use simple relational model (DEPRECATED)
#
class PlornAlbumModel(QSqlRelationalTableModel):
    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'album model init: {db.connectionName()}')
        self.setTable('albums')
        module_logger.debug(f'album model: valid? {db.isValid()}')
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        res = self.select()
        module_logger.debug(f'album model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger

        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        section_text = ['ID', 'Album', 'Dated', 'Notes', 'Photo Count']
        if role == Qt.ItemDataRole.DisplayRole:
            module_logger.debug(f'headerData: display {section}')
            return str(section_text[section])

        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        elif section==AttrFields.ID and role==Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignHCenter

        elif section > AttrFields.ID:
            return Qt.AlignmentFlag.AlignLeft
        
##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
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

        if db.isOpen() and db.isValid():
            db = db
            _current_db =db
            PlornDbOperations.create_tables()
        else:
            raise PlornDbException(f'{db.connectionName()} is not valid')

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
        module_logger.debug(f'created tables: {_current_db.tables()}')

    @staticmethod
    def create_config_table():
        global _current_db

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS config (
                name text NOT NULL,
                version text,
                username text,
                fullname text,
            );
        '''
        query = QSqlQuery(sql_stmt, db=_current_db)
        if query.isActive():
            cfgq = QSqlQuery('SELECT * FROM config;', db=_current_db)
            if cfgq.isActive() and not cfgq.next():
                config = PlornConfig()
                sql = 'INSERT INTO config VALUES ("plorn", '
                sql += f'"{config.get_version()}", '
                sql += f'"{config.get_username()}", '
                sql += f'"{config.get_fullname()}");'
                cfgadd = QSqlQuery(sql, db=_current_db)
        #else:
        #    raise PlornDbException('cannot create config table')

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
        #if not query.isActive():
        #    raise PlornDbException('cannot create albums table')

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
        #if not query.isActive():
        #    raise PlornDbException('cannot create photos table')

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
        #if not query.isActive():
        #    raise PlornDbException(f'cannot create {table_name} table')

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
            CREATE TABLE IF NOT EXISTS {obj_name}_{attr_name} (
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
        sql = f'SELECT * FROM config'
        res = self.cursor.execute(sql)
        return res.fetchone()

    def album_exists(self, album):
        sql = f'SELECT * FROM albums WHERE name = \'{album.get_name()}\''
        res = self.cursor.execute(sql)
        rows = res.fetchone()
        return rows != None

    def photo_exists(self, photo):
        sql = f'SELECT * FROM photos WHERE id = \'{photo.get_id()}\''
        res = self.cursor.execute(sql)
        rows = res.fetchone()
        return rows != None

    def add_album_name_list(album):
        global _current_album

        res = False
        if len(album.get_name_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_names (name_id, album_id) VALUES '
            for ii in album.get_name_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            sql += ';'
            query = QSqlQuery(sql, db=_current_db)
            res = query.isValid()
        return res

    def remove_album_name_list(self, album):
        sql = f'DELETE FROM album_names WHERE album_id = \'{album.get_id()}\''
        return self.cursor.execute(sql)

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

    def remove_album_place_list(self, album):
        sql = f'DELETE FROM album_places WHERE album_id = \'{album.get_id()}\''
        return self.cursor.execute(sql)

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

    def remove_album_tag_list(self, album):
        sql = f'DELETE FROM album_tags WHERE album_id = \'{album.get_id()}\''
        return self.cursor.execute(sql)

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

    def add_album(db, album):
        global _current_db

        sql = 'INSERT INTO albums (name,dated,notes,photo_count) VALUES '
        sql += f'("{album.get_name()}", '
        sql += f' "{album.get_dated()}", '
        sql += f' "{album.get_notes()}", '
        sql += f' {album.get_photo_count()}'
        sql += f');'
        query = QSqlQuery(sql, db=_current_db)

        sql = f'SELECT * FROM albums WHERE name = "{album.get_name()}"'
        query = QSqlQuery(sql, db=_current_db)
        result = None
        if query.isActive():
            query.next()
            id = query.value(AlbumFields.ID)
            name = query.value(AlbumFields.NAME)
            dated = query.value(AlbumFields.DATED)
            notes = query.value(AlbumFields.NOTES)
            count = query.value(AlbumFields.PHOTO_COUNT)
            result = PlornAlbum(name, id=id, dated=dated, notes=notes,
                                photo_count=count)
            album_id = result.get_id()

            result.set_name_list(album.get_name_list())
            result.set_place_list(album.get_place_list())
            result.set_tag_list(album.get_tag_list())

            PlornDbOperations.add_album_name_list(result)
            PlornDbOperations.add_album_place_list(result)
            PlornDbOperations.add_album_tag_list(result)

        else:
            raise PlornDBException(f'cannot add album {album.get_name()}')

        return result

    def get_album(self, album_id):
        return self.get_album_by_id(album_id)

    def get_album_by_name(self, album_name):
        sql = f'SELECT * FROM albums WHERE name = \'{album_name}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return self.get_album_by_id(row['id'])

    def get_album_row_by_id(self, album_id):
        sql = f'SELECT * FROM albums WHERE id = \'{album_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        if row == None:
            return None
        row['names'] = self.get_names_for_album_by_id(album_id)
        row['places'] = self.get_places_for_album_by_id(album_id)
        row['tags'] = self.get_tags_for_album_by_id(album_id)
        return row

    def get_album_by_id(self, album_id):
        row = self.get_album_row_by_id(album_id)
        if row == None:
            return None
        p = PlornAlbum(row['name'], id=row['id'],
                                   dated=row['dated'], notes=row['notes'],
                                   photo_count=row['photo_count'],
                                  )

        p.set_name_list(row['names'])
        p.set_place_list(row['places'])
        p.set_tag_list(row['tags'])
        return p

    def remove_album_by_name(self, album_name):
        album = self.get_album_by_name(album_name)
        if album != None:
            self.remove_album_by_id(album.get_id())
        return 

    def remove_album_by_id(self, album_id):
        sql = f'DELETE FROM albums WHERE id = \'{album_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM photos WHERE album_id = \'{album_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM album_names WHERE album_id = \'{album_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM album_places WHERE album_id = \'{album_id}\''
        res = self.cursor.execute(sql)
        sql = f'DELETE FROM album_tags WHERE album_id = \'{album_id}\''
        res = self.cursor.execute(sql)
        self.db.commit()
        return 

    def remove_album(self, album):
        self.remove_album_by_id(album.get_id())
        return 

    def get_album_cursor(self):
        cursor = self.db.cursor()
        sql = f'SELECT * FROM albums'
        res = cursor.execute(sql)
        return cursor

    def get_photo_cursor(self, album_id=None):
        cursor = self.db.cursor()
        sql  = 'SELECT * FROM photos'
        if album_id != None:
            sql += f' WHERE album_id = \'{album_id}\''
        res = cursor.execute(sql)
        return cursor

    def album_count(self):
        sql = f'SELECT id FROM albums'
        res = self.cursor.execute(sql)
        return len(res.fetchall())

    def photo_count(self):
        sql = f'SELECT id FROM photos'
        res = self.cursor.execute(sql)
        return len(res.fetchall())

    def add_name_to_album_by_id(self, name_id, album_id):
        sql  = 'INSERT INTO album_names '
        sql += '(name_id, album_id) '
        sql += f'VALUES ({name_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_name_from_album_by_id(self, name_id, album_id):
        sql  = 'DELETE FROM album_names'
        sql += f' WHERE name_id = {name_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def add_place_to_album_by_id(self, place_id, album_id):
        sql  = 'INSERT INTO album_places '
        sql += '(place_id, album_id) '
        sql += f'VALUES ({place_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_place_from_album_by_id(self, place_id, album_id):
        sql  = 'DELETE FROM album_places'
        sql += f' WHERE place_id = {place_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def add_tag_to_album_by_id(self, tag_id, album_id):
        sql  = 'INSERT INTO album_tags '
        sql += '(tag_id, album_id) '
        sql += f'VALUES ({tag_id}, {album_id})'
        res = self.cursor.execute(sql)

    def remove_tag_from_album_by_id(self, tag_id, album_id):
        sql  = 'DELETE FROM album_tags'
        sql += f' WHERE tag_id = {tag_id} AND album_id = {album_id}'
        res = self.cursor.execute(sql)

    def update_album(self, album, updated_album):
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
        res = self.cursor.execute(sql)
        self.db.commit()

        sql  = 'SELECT * FROM albums'
        sql += f' WHERE name = "{updated_album.get_name()}"'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        msg = f'updated album: from {album.get_name()}'
        msg += f' to {row['id']}'
        return self.get_album_by_id(row['id'])

    def get_photo_row_by_id(self, photo_id):
        sql = f'SELECT * FROM photos WHERE id = {photo_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        row['names'] = self.get_names_for_photo_by_id(photo_id)
        row['places'] = self.get_places_for_photo_by_id(photo_id)
        row['tags'] = self.get_tags_for_photo_by_id(photo_id)
        return row

    def get_photo_by_id(self, photo_id):
        row = self.get_photo_row_by_id(photo_id)
        p = PlornPhoto(row['name'], id=row['id'],
                                   album_id=row['album_id'],
                                   path=row['path'], dated=row['dated'],
                                   notes=row['notes'])
        p.set_name_list(row['names'])
        p.set_place_list(row['places'])
        p.set_tag_list(row['tags'])
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
        album = self.get_album(photo.get_album_id())
        sql  = 'INSERT INTO photos '
        sql += f'(album_id,name,path,dated,notes) VALUES '
        sql += f'(\'{photo.get_album_id()}\','
        sql += f' \'{photo.get_name()}\', \'{photo.get_path()}\','
        sql += f' \'{photo.get_dated()}\', \'{photo.get_notes()}\')'
        res = self.cursor.execute(sql)
        self.increment_photo_count(album)
        self.db.commit()
        sql = f'SELECT * FROM photos WHERE path = \'{photo.get_path()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return PlornPhoto(row['name'],
                                      id=row['id'], album_id=row['album_id'],
                                      path=row['path'],
                                      dated=row['dated'], notes=row['notes'])

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

    def add_attr(self, attr):
        table_name = attr.get_db_table_name()
        sql = f'INSERT INTO {table_name} (value, parent_id) VALUES '
        value = attr.get_value()
        pid = attr.get_parent_id()
        if pid == None:
            pid = 0
        sql += f'(\'{value}\', \'{pid}\')'
        res = self.cursor.execute(sql)
        self.db.commit()
        sql = f'SELECT * FROM {table_name} WHERE value = \'{value}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return row

    def add_name(self, name):
        row = self.add_attr(name)
        return PlornName(row['value'], id=row['id'],
                                    parent_id=row['parent_id'])

    def add_place(self, place):
        row = self.add_attr(place)
        return PlornPlace(row['value'], id=row['id'],
                                     parent_id=row['parent_id'])

    def add_tag(self, tag):
        row = self.add_attr(tag)
        return PlornTag(row['value'], id=row['id'],
                                   parent_id=row['parent_id'])

    def attr_exists(self, attr):
        table_name = attr.get_db_table_name()
        value = attr.get_value()
        sql = f'SELECT * FROM {table_name} WHERE value = \'{value}\''
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        return len(rows) > 0

    def name_exists(self, name):
        return self.attr_exists(name)

    def place_exists(self, place):
        return self.attr_exists(place)

    def tag_exists(self, tag):
        return self.attr_exists(tag)

    def get_attr(self, attr_id, table_name):
        sql = f'SELECT * FROM {table_name}  WHERE id = \'{attr_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return row

    def get_name(self, name_id):
        row = self.get_attr(name_id, 'names')
        return PlornName(row['value'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_place(self, place_id):
        row = self.get_attr(place_id, 'places')
        return PlornPlace(row['value'], id=row['id'],
                                     parent_id=row['parent_id'])

    def get_tag(self, tag_id):
        row = self.get_attr(tag_id, 'tags')
        return PlornTag(row['value'], id=row['id'],
                                   parent_id=row['parent_id'])

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

    def get_full_attr(self, attr):
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql = f'SELECT * FROM {table_name} WHERE id = \'{attr_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        fullattr = []
        fullattr.append(row['value'])
        while row and row['parent_id'] != 0:
            pid = row['parent_id']
            sql = f'SELECT * FROM {table_name} WHERE id = \'{pid}\''
            res = self.cursor.execute(sql)
            row = res.fetchone()
            if row:
                fullattr.append(row['value'])
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
        sql = f'SELECT * FROM {table_name}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['value'])
        return rows

    def get_all_names(self):
        rows = self.get_all_attrs('names')
        result = []
        for ii in rows:
            p = PlornName(ii['value'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_all_places(self):
        rows = self.get_all_attrs('places')
        result = []
        for ii in rows:
            p = PlornPlace(ii['value'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

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

    def get_names_for_album_by_id(self, album_id):
        sql  = f'SELECT * FROM album_names'
        sql += f' WHERE album_id = {album_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_name(ii['name_id']))
        return result

    def get_names_for_album(self, album):
        if not album:
            return []
        return self.get_names_for_album_by_id(album.get_id())

    def get_places_for_album_by_id(self, album_id):
        sql  = f'SELECT * FROM album_places'
        sql += f' WHERE album_id = {album_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_place(ii['place_id']))
        return result

    def get_places_for_album(self, album):
        if not album:
            return []
        return self.get_places_for_album_by_id(album.get_id())

    def get_tags_for_album_by_id(self, album_id):
        sql  = f'SELECT * FROM album_tags'
        sql += f' WHERE album_id = {album_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_tag(ii['tag_id']))
        return result

    def get_tags_for_album(self, album):
        if not album:
            return []
        return self.get_tags_for_album_by_id(album.get_id())

    def get_names_for_photo_by_id(self, photo_id):
        sql  = f'SELECT * FROM photo_names'
        sql += f' WHERE photo_id = {photo_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_name(ii['name_id']))
        return result

    def get_names_for_photo(self, photo):
        if not photo:
            return []
        return self.get_names_for_photo_by_id(photo.get_id())

    def get_places_for_photo_by_id(self, photo_id):
        sql  = f'SELECT * FROM photo_places'
        sql += f' WHERE photo_id = {photo_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_place(ii['place_id']))
        return result

    def get_places_for_photo(self, photo):
        if not photo:
            return []
        return self.get_places_for_photo_by_id(photo.get_id())

    def get_tags_for_photo_by_id(self, photo_id):
        sql  = f'SELECT * FROM photo_tags'
        sql += f' WHERE photo_id = {photo_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            result.append(self.get_tag(ii['tag_id']))
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


##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

_ALBUM_DATA = {}
_PHOTO_DATA = {}

class AlbumViewColumn(IntEnum):
    '''
    column numbers used in the album tree view
    '''
    ROW   = 0
    ID    = 1
    NAME  = 2
    COUNT = 3
    PATH  = 4

def populate_albums(root, db=QSqlDatabase()):
    global module_logger, _ALBUM_DATA

    msg  = f'populate_albums: init: db {db.connectionName()} is '
    msg += f'{db.databaseName()}'
    module_logger.debug(msg)

    if not db.isOpen():
        raise PlornDbException('cannot get albums from closed db')
    if not db.isValid():
        raise PlornDbException('cannot get albums from invalid db')

    dbdata = _collect_album_dbdata(db)
    _ALBUM_DATA = dbdata
    dbtree = _build_album_tree(root, db, dbdata)
    _dump_album_tree(root, dbtree)
    module_logger.debug(f'populate_albums: init done')

def album_stats():
    global module_logger, _ALBUM_DATA

    album_count = len(_ALBUM_DATA)
    photo_count = 0
    for ii, data in _ALBUM_DATA.items():
        nphotos = data[AlbumFields.PHOTO_COUNT]
        photo_count += nphotos
        album_name = data[AlbumFields.NAME]
        module_logger.debug(f'album_stats: {ii} "{album_name}", {nphotos}')
    module_logger.debug(f'album_stats: {album_count}, {photo_count}')
    return album_count, photo_count

def _build_id_item(id):
    item = QStandardItem(f'{id:04}')
    item.setEditable(False)
    item.setCheckable(False)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
    return item

def _build_album_id_item(dbrow):
    id = dbrow[AlbumFields.ID]
    item = _build_id_item(id)
    font = QFont()
    font.setBold(True)
    font.setItalic(True)
    item.setFont(font)
    return item

def _build_photo_id_item(dbrow):
    id = dbrow[PhotoFields.ID]
    return _build_id_item(id)

def _build_album_name_item(dbrow):
    name = dbrow[AlbumFields.NAME]
    item = QStandardItem(str(name))
    item.setEditable(True)
    item.setCheckable(False)
    font = QFont()
    font.setBold(True)
    font.setItalic(True)
    item.setFont(font)
    return item

def _build_dated_item(dated):
    item = QStandardItem(str(dated))
    item.setEditable(True)
    item.setCheckable(False)
    return item

def _build_album_dated_item(dbrow):
    dated = dbrow[AlbumFields.DATED]
    item = _build_dated_item(dated)
    font = QFont()
    font.setBold(True)
    font.setItalic(True)
    item.setFont(font)
    return item

def _build_photo_dated_item(dbrow):
    dated = dbrow[PhotoFields.DATED]
    return _build_dated_item(dated)

def _build_album_count_item(dbrow):
    count = dbrow[AlbumFields.PHOTO_COUNT]
    item = QStandardItem(str(count))
    item.setEditable(False)
    item.setCheckable(False)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    font = QFont()
    font.setBold(True)
    font.setItalic(True)
    item.setFont(font)
    return item

def _build_photo_name_item(dbrow):
    name = dbrow[PhotoFields.NAME]
    item = QStandardItem(str(name))
    item.setEditable(True)
    item.setCheckable(False)
    return item

def _build_photo_path_item(dbrow):
    name = dbrow[PhotoFields.PATH]
    item = QStandardItem(str(name))
    item.setEditable(False)
    item.setCheckable(False)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
    return item

def _collect_album_dbdata(db):
    global module_logger

    module_logger.debug('_collect_album_dbdata: entered')
    dbdata = {}
    query = QSqlQuery(f'SELECT * FROM albums;', db=db)
    while query.next():
        row_data = [query.value(AlbumFields.ID),
                    query.value(AlbumFields.NAME),
                    query.value(AlbumFields.DATED),
                    query.value(AlbumFields.NOTES),
                    query.value(AlbumFields.PHOTO_COUNT)]
        dbdata[query.value(AlbumFields.ID)] = row_data
    module_logger.debug(f'_collect_album_dbdata: keys {str(dbdata.keys())}')
    module_logger.debug(f'_collect_album_dbdata: done, {len(dbdata)} records')
    return dbdata

def _collect_photo_dbdata(db, album_id):
    global module_logger, _PHOTO_DATA

    module_logger.debug('_collect_photo_dbdata: entered')
    dbdata = {}
    actual_id = int(album_id)                       # paranoid conversion
    sql = f'SELECT * FROM photos WHERE album_id = {actual_id};'
    query = QSqlQuery(sql, db=db)
    while query.next():
        row_data = [query.value(PhotoFields.ID),
                    query.value(PhotoFields.ALBUM_ID),
                    query.value(PhotoFields.NAME),
                    query.value(PhotoFields.PATH),
                    query.value(PhotoFields.DATED),
                    query.value(PhotoFields.NOTES)]
        id = query.value(PhotoFields.ID)
        dbdata[id] = row_data
        if id not in _PHOTO_DATA:
            _PHOTO_DATA[id] = row_data

    module_logger.debug(f'_collect_photo_dbdata: keys {str(dbdata.keys())}')
    module_logger.debug(f'_collect_photo_dbdata: done, {len(dbdata)} records')
    return dbdata

def _build_album_tree(root, db, dbdata):
    global module_logger, _ALBUM_DATA, _PHOTO_DATA
    '''
        NB: whilst the database itself if a 1-based array,
        with ID pointing to parents, Qt expects an actual tree
        structure when working with QTreeView.  So, build the
        structure up from our dbdata.
    '''
    module_logger.debug('_build_album_tree: entered')
    dbtree = {}
    row = 0
    for ii, dbrow in dbdata.items():
        id_item = _build_album_id_item(dbrow)
        id = int(id_item.text())
        row_item = QStandardItem(str(row))
        name_item = _build_album_name_item(dbrow)
        dated_item = _build_album_dated_item(dbrow)
        count_item = _build_album_count_item(dbrow)
        root.appendRow([id_item, row_item, name_item, dated_item, count_item])
        current = root.child(row)

        #-- the model is zero-based, but the db fields are one-based,
        #   and we only want certain columns anyway
        album_id = dbrow[AlbumFields.ID]
        dbtree[album_id] = [id_item, name_item, dated_item, count_item]
        row += 1
        
        nphotos = 0
        photos = _collect_photo_dbdata(db, album_id)
        for jj, photo_row in photos.items():
            msg  = f'_build_album_tree: photo row {nphotos}, '
            msg += f'{photo_row}'
            module_logger.debug(msg)
            prow_item = QStandardItem(str(nphotos))
            pid_item = _build_photo_id_item(photo_row)
            pid = int(pid_item.text())
            pname_item = _build_photo_name_item(photo_row)
            pdated_item = _build_photo_dated_item(photo_row)
            ppath_item = _build_photo_path_item(photo_row)
            current.appendRow([pid_item, prow_item, pname_item,
                               pdated_item, QStandardItem(), ppath_item])
            nphotos += 1

    module_logger.debug('_build_album_tree: done')
    return dbtree

def _dump_album_tree(root, dbtree):
    global module_logger, _ALBUM_DATA

    if module_logger.isEnabledFor(logging.DEBUG):
        module_logger.debug('=> _dump_album_tree start')
        if root.hasChildren():
            for row in range(len(_ALBUM_DATA)):
                vrow = root.child(row, 0)
                album = root.child(row, 1)
                name = root.child(row, 2)
                count = root.child(row, 3)
                msg  = f'{album.text()}  {name.text()}  {count.text()}'
                module_logger.debug(msg)

                if vrow.hasChildren():
                    for nphoto in range(vrow.rowCount()):
                        photo = vrow.child(nphoto, 1)
                        pname = vrow.child(nphoto, 2)
                        ppath = vrow.child(nphoto, 3)
                        msg  = f'    {photo.text()}  {pname.text()}  '
                        msg += f'{ppath.text()}'
                        module_logger.debug(msg)
        module_logger.debug('<= _dump_album_tree end')

def model_add_album(root, album, db=QSqlDatabase()):
    global module_logger, _ALBUM_DATA

    msg  = f'model_add_album: {str(album)}'
    module_logger.debug(msg)

    if not db.isOpen():
        msg  = 'model_add_album: cannot open database'
        module_logger.debug(msg)
        return 'cannot open db'

    if not db.isValid():
        msg  = 'model_add_album: database is not valid'
        module_logger.debug(msg)
        return 'db is invalid'

    # add to db to get an id and actual dbrow
    # ...we do not care about duplicate names, so try adding it
    added_album = PlornDbOperations.add_album(db, album)
    assert added_album != None and added_album.get_id() != 0

    row_data = [added_album.get_id(),
                added_album.get_name(),
                added_album.get_dated(),
                added_album.get_notes(),
                added_album.get_photo_count()]
    _ALBUM_DATA[id] = row_data
    module_logger.debug(f'model_add_album: added {row_data}')
    row_item = QStandardItem(str(root.rowCount()+1))
    id_item = _build_album_id_item(row_data)
    name_item = _build_album_name_item(row_data)
    dated_item = _build_album_dated_item(row_data)
    count_item = _build_album_count_item(row_data)
    root.appendRow([id_item, row_item, name_item, dated_item, count_item])
    module_logger.debug(f'model_add_album: okay and done')
    return 'okay'
    

##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

_NAMES_DATA = {}
_PLACES_DATA = {}
_TAGS_DATA = {}

def _set_table_data(table, dbdata):
    global module_logger, _NAMES_DATA, _PLACES_DATA, _TAGS_DATA

    if table == 'name':
        _NAMES_DATA = dbdata
    elif table == 'places':
        _PLACES_DATA = dbdata
    elif table == 'tags':
        _TAGS_DATA = dbdata
    else:
        return None

def _add_table_data(table, id, data):
    global module_logger, _NAMES_DATA, _PLACES_DATA, _TAGS_DATA

    if table == 'name':
        _NAMES_DATA[id] = data
    elif table == 'places':
        _PLACES_DATA[id] = data
    elif table == 'tags':
        _TAGS_DATA[id] = data
    else:
        return None

def _del_table_data(table, id):
    global module_logger, _NAMES_DATA, _PLACES_DATA, _TAGS_DATA

    if table == 'name':
        del _NAMES_DATA[id]
    elif table == 'places':
        del _PLACES_DATA[id]
    elif table == 'tags':
        del _TAGS_DATA[id]
    else:
        return None

def _in_table_keys(table, id):
    global module_logger, _NAMES_DATA, _PLACES_DATA, _TAGS_DATA

    if table == 'name':
        return id in _NAMES_DATA.keys()
    elif table == 'places':
        return id in _PLACES_DATA.keys()
    elif table == 'tags':
        return id in _TAGS_DATA.keys()
    else:
        return False

def populate_attrs(root, table='names', db=QSqlDatabase()):
    global module_logger

    module_logger.debug(f'populate_attrs: {table} init')
    dbdata = _collect_attr_dbdata(table, db)
    _set_table_data(table, dbdata)
    dbtree = _build_attr_tree(root, dbdata)
    _dump_attr_tree(root, dbtree)
    module_logger.debug(f'populate_attrs: {table} init done')

def add_attrs(root, parent, value, table='names', db=QSqlDatabase()):
    global module_logger

    msg  = f'add_attrs: add {value} to {table} in db {db.connectionName()}'
    module_logger.debug(msg)

    if len(value) < 1:          # should be a string and actual QStandardItem
        return 'internal error: bad value'
    if parent == None:
        parent = root
    msg  = f'add_attrs: appending row "{value}" to "{parent.text()}"'
    module_logger.debug(msg)
    pid = 0
    if parent.data() and len(parent.data()) > 0:
        module_logger.debug(f'add_attrs: parent data "{parent.data()}"')
        pid = parent.data()[AttrFields.ID]

    # add to db to get an id and actual dbrow
    # ...but first, do we already have it?
    sql  = f'SELECT * FROM {table} WHERE '
    sql += f'value = "{value}" AND parent_id = {pid};'
    query = QSqlQuery(sql, db=db)
    if query and query.next():
        module_logger.debug(f'add_attrs: found existing {query}')
        return 'duplicate attribute'

    # ...we don't, so try adding it
    module_logger.debug(f'add_attrs: adding item to db')
    sql  = f'INSERT INTO {table} '
    sql += f'(parent_id, value) VALUES '
    sql += f'({pid}, "{value}");'
    query = QSqlQuery(sql, db=db)
    if not query:
        module_logger.debug(f'add_attrs: query to insert failed')
        return 'cannot insert'

    # ...we added it, so now tell the view
    sql  = f'SELECT * FROM {table} WHERE '
    sql += f'value = "{value}" AND parent_id = {pid};'
    query = QSqlQuery(sql, db=db)
    if not query.next():
        module_logger.debug(f'add_attrs: retrieval of row failed')
        return 'retrieve failed'
    id = query.value(AttrFields.ID)
    row = [id, pid, value]
    module_logger.debug(f'add_attrs: added {row} to {table}')
    item = _build_attr_item(row)
    parent.appendRow(item)                          # add to treeview
    _add_table_data(table, id, item)                # save if for the "model"
    module_logger.debug(f'add_attrs: okay and done')
    return 'okay'

def remove_attrs(root, item, table='names', db=QSqlDatabase()):
    global module_logger

    if not item:
        module_logger.debug('remove_attrs: nothing to remove')
        return 'okay'

    msg  = f'remove_attrs: remove {item.text()} from {table} '
    msg += f'in db {db.connectionName()}'
    module_logger.debug(msg)

    row = item.data()
    if not row or len(row) < 1:                     # cannot remove root
        return 'cannot delete root'

    id = row[AttrFields.ID]                         # no such db record
    if id < 1:
        return 'cannot delete db index 0'

    parent = item.parent()
    msg = 'remove_attrs: '
    if not parent:
        parent = root
        msg += f'deleting {item.row()} from root'
    else:
        msg += f'deleting {item.row()} from parent {parent.text()}'
    module_logger.debug(msg)

    while item.hasChildren():
        res = remove_attrs(root, item.child(0), table=table, db=db)

    sql  = f'DELETE FROM {table} WHERE id = {id};'
    query = QSqlQuery(sql, db=db)
    if not query:
        module_logger.debug(f'remove_attrs: retrieval of row failed')
        return 'retrieve failed'
    module_logger.debug(f'remove_attrs: deleted {row} from {table}')

    module_logger.debug(msg)
    value = item.text()
    parent.removeRow(item.row())                    # remove from treeview
    if _in_table_keys(table, id):
        msg = f'remove_attrs: deleting "{value}" from _ATTR_DATA'
        module_logger.debug(msg)
        _del_table_data(table, id)
    module_logger.debug(f'remove_attrs: okay and done')
    return 'okay'

def _build_attr_item(dbrow):
    id = dbrow[AttrFields.ID]
    parent_id = dbrow[AttrFields.PARENT_ID]
    value = dbrow[AttrFields.VALUE]
    item = QStandardItem(str(value))
    item.setEditable(True)
    item.setCheckable(False)
    item.setData([id, parent_id, value])
    return item

def _collect_attr_dbdata(table, db):
    global module_logger

    module_logger.debug('_collect_dbdata: entered')
    dbdata = {}
    query = QSqlQuery(f'SELECT * FROM {table};', db=db)
    while query.next():
        row_data = [query.value(AttrFields.ID),
                    query.value(AttrFields.PARENT_ID),
                    query.value(AttrFields.VALUE)]
        dbdata[query.value(AttrFields.ID)] = _build_attr_item(row_data)
    module_logger.debug(f'_collect_dbdata: keys {str(dbdata.keys())}')
    module_logger.debug(f'_collect_dbdata: done, {len(dbdata)} records')
    return dbdata

def _build_attr_tree(root, dbdata):
    global module_logger
    '''
        NB: whilst the database itself if a 1-based array,
        with ID pointing to parents, Qt expects an actual tree
        structure when working with QTreeView.  So, build the
        structure up from our dbdata.
    '''
    module_logger.debug('_build_attr_tree: entered')
    dbtree = {}
    count = len(dbdata)
    while count > 0:
        for ii, item in dbdata.items():
            dbrow = item.data()
            id = dbrow[AttrFields.ID]
            parent_id = dbrow[AttrFields.PARENT_ID]
            value = dbrow[AttrFields.VALUE]
            msg = f'count, dbdata: {count} [{id}, {parent_id}, {value}]'
            module_logger.debug(msg)
            if id not in dbtree.keys():
                if parent_id in dbtree.keys():
                    module_logger.debug(f'! append to {parent_id}')
                    dbtree[parent_id].appendRow(item)
                    dbtree[id] = item
                    count -= 1
                elif parent_id == 0:
                    module_logger.debug(f'! append to root')
                    root.appendRow(item)
                    dbtree[id] = item
                    count -= 1
                else:
                    module_logger.debug(f'! skipping???')
    root.sortChildren(0, Qt.SortOrder.AscendingOrder)
    module_logger.debug('_build_attr_tree: done')
    return dbtree

def _dump_attr_tree(root, dbtree, item=None, level=0):
    global module_logger

    if module_logger.isEnabledFor(logging.DEBUG):
        if item == None:
            item = root
        if level == 0:
            module_logger.debug('_dump_attr_tree start =>')
        spaces = '   ' * level
        if item.data() == None:
            module_logger.debug(f'{spaces}root:')
        else:
            msg  = f'{spaces}{item.text()} {str(item.data())}'
            module_logger.debug(msg)
        kids = []
        if item.hasChildren():
            for ii in range(item.rowCount()):
                kids.append(item.child(ii))
        for ii in kids:
             _dump_attr_tree(root, dbtree, ii, level+1)
        if level == 0:
            module_logger.debug('<= _dump_attr_tree end')

