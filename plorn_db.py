import copy
import logging
import os
import sqlite3
import sys

from PIL import Image as pilImage
from PIL import ImageTk

import plorn_album
import plorn_attr
import plorn_config
import plorn_photo

module_logger = logging.getLogger('plorn.db')
module_logger.setLevel(logging.INFO)

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
        self.create_tables()

    def close(self):
        self.db.close()
        self.config = None

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

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS config (
                name text NOT NULL,
                version text,
                username text,
                fullname text,
                datadir text
            );
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 1
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))

        cfg = self.config
        sql = 'INSERT INTO config VALUES (\'plorn\', '
        sql += f'\'{cfg.get_version()}\', \'{cfg.get_username()}\', '
        sql += f'\'{cfg.get_fullname()}\', \'{cfg.get_datadir()}\')'
        self.cursor.execute(sql)
        self.db.commit()

    def create_albums_table(self):
        global module_logger

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY,
                name text NOT NULL,
                dated text,
                notes text,
                photo_count INT
            );
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 1
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_photos_table(self):
        global module_logger

        sql_stmt = '''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY,
                album_id INT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                dated TEXT,
                notes TEXT,
                thumbnail TEXT,
                FOREIGN KEY (album_id)
                REFERENCES albums (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_attr_table(self, table_name):
        global module_logger

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
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_album_names_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_album_places_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_album_tags_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_photo_names_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_photo_places_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

    def create_photo_tags_table(self):
        global module_logger

        sql_stmt = '''
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
        '''
        self.cursor.execute(sql_stmt)
        self.db.commit()
        rowid = self.cursor.lastrowid + 2
        sql = f'SELECT name FROM sqlite_master WHERE rowid = {rowid}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug('added table: ' + str(row))
        self.db.commit()

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

    def add_album_name_list(self, album):
        res = None
        if len(album.get_name_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_names (name_id, album_id) VALUES '
            for ii in album.get_name_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
        return res

    def remove_album_name_list(self, album):
        sql = f'DELETE FROM album_names WHERE album_id = \'{album.get_id()}\''
        return self.cursor.execute(sql)

    def add_album_place_list(self, album):
        res = None
        if len(album.get_place_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_places (place_id, album_id) VALUES '
            for ii in album.get_place_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
        return res

    def remove_album_place_list(self, album):
        sql = f'DELETE FROM album_places WHERE album_id = \'{album.get_id()}\''
        return self.cursor.execute(sql)

    def add_album_tag_list(self, album):
        res = None
        if len(album.get_tag_list()) > 0:
            album_id = album.get_id()
            sql  = 'INSERT INTO album_tags (tag_id, album_id) VALUES '
            for ii in album.get_tag_list():
                #print(f'   {ii.get_value()}: {ii.get_id()}, {album_id}')
                sql += f'({ii.get_id()}, {album_id}), '
            idx = sql.rfind(',')
            sql = sql[0:idx]
            res = self.cursor.execute(sql)
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

    def add_album(self, album):
        sql = 'INSERT INTO albums (name,dated,notes,photo_count) VALUES '
        sql += f'("{album.get_name()}", '
        sql += f' "{album.get_dated()}", '
        sql += f' "{album.get_notes()}", '
        sql += f' {album.get_photo_count()}'
        sql += f')'
        res = self.cursor.execute(sql)
        self.db.commit()
        sql = f'SELECT * FROM albums WHERE name = "{album.get_name()}"'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f'added album {str(row)}')
        result = plorn_album.PlornAlbum(row['name'], id=row['id'],
                                        dated=row['dated'], notes=row['notes'],
                                        photo_count=row['photo_count'])

        album_id = result.get_id()
        result.set_name_list(album.get_name_list())
        result.set_place_list(album.get_place_list())
        result.set_tag_list(album.get_tag_list())

        res = self.add_album_name_list(result)
        res = self.add_album_place_list(result)
        res = self.add_album_tag_list(result)

        self.db.commit()
        return result

    def get_album(self, album_id):
        return self.get_album_by_id(album_id)

    def get_album_by_name(self, album_name):
        sql = f'SELECT * FROM albums WHERE name = \'{album_name}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f'got by name: {str(row)}')
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
        p = plorn_album.PlornAlbum(row['name'], id=row['id'],
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
        module_logger.debug(f'removed album by name: {album_name}')
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
        module_logger.debug(f'removed album by id: {album_id}')
        return 

    def remove_album(self, album):
        self.remove_album_by_id(album.get_id())
        module_logger.debug(f'removed album by name: {album.get_name()}')
        return 

    def get_album_cursor(self):
        cursor = self.db.cursor()
        sql = f'SELECT * FROM albums'
        res = cursor.execute(sql)
        return cursor

    def get_photo_cursor(self):
        cursor = self.db.cursor()
        sql  = 'SELECT * FROM photos'
        res = cursor.execute(sql)
        return cursor

    def get_photos(self, album_id):
        sql  = f'SELECT * FROM photos WHERE album_id = \'{album_id}\''
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: int(x['id']))
        result = []
        for ii in rows:
            p = plorn_photo.PlornPhoto(ii['name'], id=ii['id'],
                                       album_id=album_id,
                                       path=ii['path'],
                                       dated=ii['dated'], notes=ii['notes'],
                                       thumbnail=ii['thumbnail'])
            result.append(p)
        return result

    def album_count(self):
        sql = f'SELECT id FROM albums'
        res = self.cursor.execute(sql)
        return len(res.fetchall())

    def photo_count(self):
        sql = f'SELECT id FROM photos'
        res = self.cursor.execute(sql)
        return len(res.fetchall())

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
        module_logger.debug(msg)
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
        p = plorn_photo.PlornPhoto(row['name'], id=row['id'],
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

    def get_thumbnails_dir(self, album_id):
        dirname = os.path.join(self.config.get_datadir(),
                               'thumbnails',
                               f'album{album_id:04}')
        if not (os.path.exists(dirname) and os.path.isdir(dirname)):
            module_logger.debug(f'make thumbnail dir {dirname}')
            os.makedirs(dirname, exist_ok=True)
        return dirname

    def make_thumbnail(self, photo, album):
        fullpath = os.path.expandvars(os.path.expanduser(photo.get_path()))
        base = os.path.basename(fullpath)
        thumbpath = os.path.join(self.get_thumbnails_dir(album.get_id()), base)
        #raw_img = pilImage.open(fullpath)
        #small_img = raw_img.resize((100,100))
        small_img = pilImage.open(fullpath)
        small_img.thumbnail((100,100), pilImage.Resampling.LANCZOS)
        small_img.save(thumbpath)
        small_img.close()
        return thumbpath

    def add_photo(self, photo):
        album = self.get_album(photo.get_album_id())
        thumb = self.make_thumbnail(photo, album)
        photo.set_thumbnail(thumb)
        sql  = 'INSERT INTO photos '
        sql += f'(album_id,name,path,dated,notes,thumbnail) VALUES '
        sql += f'(\'{photo.get_album_id()}\','
        sql += f' \'{photo.get_name()}\', \'{photo.get_path()}\','
        sql += f' \'{photo.get_dated()}\', \'{photo.get_notes()}\','
        sql += f' \'{photo.get_thumbnail()}\')'
        res = self.cursor.execute(sql)
        self.increment_photo_count(album)
        self.db.commit()
        sql = f'SELECT * FROM photos WHERE path = \'{photo.get_path()}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        module_logger.debug(f'added photo {str(row)}')
        return plorn_photo.PlornPhoto(row['name'],
                                      id=row['id'], album_id=row['album_id'],
                                      path=row['path'],
                                      dated=row['dated'], notes=row['notes'],
                                      thumbnail=row['thumbnail'])

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
        return plorn_attr.PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_name_by_name(self, name, parent_id=0):
        sql  = f'SELECT * FROM names WHERE name = \'{name}\''
        sql += f' AND parent_id = \'{parent_id}\''
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return plorn_attr.PlornName(row['name'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_name_children(self, name_id):
        sql = f'SELECT * FROM names WHERE parent_id = {name_id}'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        result = []
        for ii in rows:
            p = plorn_attr.PlornName(ii['name'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_name_child(self, name_id, parent_id):
        sql  = f'SELECT * FROM names WHERE id = {name_id}'
        sql += ' AND parent_id = {parent_id}'
        res = self.cursor.execute(sql)
        row = res.fetchone()
        return plorn_attr.PlornName(row['name'], id=row['id'],
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
        module_logger.debug(f'removed name: {name_id} of {parent_id}')
        return 

    def get_names(self):
        sql = f'SELECT * FROM names'
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        rows.sort(key=lambda x: x['name'])
        result = []
        for ii in rows:
            p = plorn_attr.PlornName(ii['name'], id=ii['id'],
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
        module_logger.debug(msg)
        return plorn_attr.PlornName(row['name'], id=row['id'],
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
        module_logger.debug(f'get_place_children: sql {sql} for {place_id}')
        res = self.cursor.execute(sql)
        rows = res.fetchall()
        module_logger.debug(f'get_place_children: found {len(rows)} for {place_id}')
        result = []
        for ii in rows:
            p = plorn_attr.PlornPlace(ii['place'], id=ii['id'],
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
        module_logger.debug(f'get_places: {rows}')
        result = []
        for ii in rows:
            p = plorn_attr.PlornPlace(ii['place'], id=ii['id'],
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
        module_logger.debug(f'place obj by place \'{place}\': {str(row)}')
        return plorn_attr.PlornPlace(row['place'], id=row['id'],
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
        module_logger.debug(f'added to {table_name}: {str(row)}')
        return row

    def add_name(self, name):
        row = self.add_attr(name)
        return plorn_attr.PlornName(row['value'], id=row['id'],
                                    parent_id=row['parent_id'])

    def add_place(self, place):
        row = self.add_attr(place)
        return plorn_attr.PlornPlace(row['value'], id=row['id'],
                                     parent_id=row['parent_id'])

    def add_tag(self, tag):
        row = self.add_attr(tag)
        return plorn_attr.PlornTag(row['value'], id=row['id'],
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
        module_logger.debug(f'get_attr: {str(row)}')
        return row

    def get_name(self, name_id):
        row = self.get_attr(name_id, 'names')
        return plorn_attr.PlornName(row['value'], id=row['id'],
                                    parent_id=row['parent_id'])

    def get_place(self, place_id):
        row = self.get_attr(place_id, 'places')
        return plorn_attr.PlornPlace(row['value'], id=row['id'],
                                     parent_id=row['parent_id'])

    def get_tag(self, tag_id):
        row = self.get_attr(tag_id, 'tags')
        return plorn_attr.PlornTag(row['value'], id=row['id'],
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
            p = plorn_attr.PlornName(ii['value'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_place_children(self, place):
        rows = self.get_attr_children(place)
        result = []
        for ii in rows:
            p = plorn_attr.PlornPlace(ii['value'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_tag_children(self, tag):
        rows = self.get_attr_children(tag)
        result = []
        for ii in rows:
            p = plorn_attr.PlornTag(ii['value'], id=ii['id'],
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
        module_logger.debug(f'get_all_attrs: {rows}')
        return rows

    def get_all_names(self):
        rows = self.get_all_attrs('names')
        result = []
        for ii in rows:
            p = plorn_attr.PlornName(ii['value'], id=ii['id'],
                                     parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_all_places(self):
        rows = self.get_all_attrs('places')
        result = []
        for ii in rows:
            p = plorn_attr.PlornPlace(ii['value'], id=ii['id'],
                                      parent_id=ii['parent_id'])
            result.append(p)
        return result

    def get_all_tags(self):
        rows = self.get_all_attrs('tags')
        result = []
        for ii in rows:
            p = plorn_attr.PlornTag(ii['value'], id=ii['id'],
                                    parent_id=ii['parent_id'])
            result.append(p)
        return result

    def remove_attr(self, attr):
        table_name = attr.get_db_table_name()
        attr_id = attr.get_id()
        sql  = f'DELETE FROM {table_name} WHERE id = \'{attr_id}\''
        res = self.cursor.execute(sql)
        self.db.commit()
        module_logger.debug(f'removed attr: {attr_id} from {table_name}')
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
        module_logger.debug(msg)
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


def get_dbname(config):
    dbpath = config.get_datadir()
    dbname = config.get_dbname()
    return os.path.join(dbpath, dbname)

def open(dbname='plorn.db', cfgname='plorn.cfg'):
    global module_logger, current_db

    module_logger.debug('open db')
    module_logger.debug(f'config is \'{cfgname}\'')

    config = plorn_config.get_config(cfgname)
    if config.needs_db():
        module_logger.debug('need to create tables')
        current_db = PlornDb(get_dbname(config), config)
        config.db_done()

    if current_db == None:
        module_logger.debug(f'open existing db \'{get_dbname(config)}\'')
        current_db = PlornDb(get_dbname(config), config)

    return current_db

def close():
    global current_db

    if current_db != None:
        current_db.close()
        current_db = None


def get_dbname(config):
    dbpath = config.get_datadir()
    dbname = config.get_dbname()
    return os.path.join(dbpath, dbname)

def open(dbname='plorn.db', cfgname='plorn.cfg'):
    global module_logger, current_db

    module_logger.debug('open db')
    module_logger.debug(f'config is \'{cfgname}\'')

    config = plorn_config.get_config(cfgname)
    if config.needs_db():
        module_logger.debug('need to create tables')
        current_db = PlornDb(get_dbname(config), config)
        config.db_done()

    if current_db == None:
        module_logger.debug(f'open existing db \'{get_dbname(config)}\'')
        current_db = PlornDb(get_dbname(config), config)

    return current_db

def close():
    global current_db

    if current_db != None:
        current_db.close()
        current_db = None

