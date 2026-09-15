#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

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

from plorn import CatalogColumns

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

from plorn.models.dbops import PlornDbOperations

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.DEBUG)


##########################################################################
#
#   data model for Albums -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

class PlornAlbumModel:
    _ALBUM_DATA = {}
    _PHOTO_DATA = {}

    @staticmethod
    def populate_albums(root, db=QSqlDatabase()):
        global module_logger

        msg  = f'populate_albums: init: db {db.connectionName()} is '
        msg += f'{db.databaseName()}'
        module_logger.debug(msg)

        if not db.isOpen():
            raise PlornDbException('cannot get albums from closed db')
        if not db.isValid():
            raise PlornDbException('cannot get albums from invalid db')

        dbdata = PlornAlbumModel._collect_album_dbdata(db)
        PlornAlbumModel._ALBUM_DATA = dbdata
        dbtree = PlornAlbumModel._build_album_tree(root, db, dbdata)
        PlornAlbumModel._dump_album_tree(root, dbtree)
        module_logger.debug(f'populate_albums: init done')

    @staticmethod
    def album_stats():
        global module_logger

        album_count = len(PlornAlbumModel._ALBUM_DATA)
        photo_count = 0
        for ii, data in PlornAlbumModel._ALBUM_DATA.items():
            module_logger.debug(f'album_stats: row "{ii}", {data}')
            nphotos = data[AlbumFields.PHOTO_COUNT]
            photo_count += nphotos
            album_name = data[AlbumFields.NAME]
            module_logger.debug(f'album_stats: "{album_name}", {nphotos}')
        module_logger.debug(f'album_stats: {album_count}, {photo_count}')
        return album_count, photo_count

    @staticmethod
    def _build_id_item(id):
        item = QStandardItem(f'{id:04}')
        item.setSelectable(True)
        item.setEditable(False)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        return item
    
    @staticmethod
    def _build_album_id_item(dbrow):
        id = dbrow[AlbumFields.ID]
        item = PlornAlbumModel._build_id_item(id)
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        item.setFont(font)
        return item
    
    @staticmethod
    def _build_photo_id_item(dbrow):
        id = dbrow[PhotoFields.ID]
        return PlornAlbumModel._build_id_item(id)
    
    @staticmethod
    def _build_name_item(name):
        item = QStandardItem(str(name))
        item.setSelectable(True)
        item.setEditable(False)
        return item
    
    @staticmethod
    def _build_album_name_item(dbrow):
        name = dbrow[AlbumFields.NAME]
        item = PlornAlbumModel._build_name_item(str(name))
        item.setSelectable(True)
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        item.setFont(font)
        item.setEnabled(True)
        return item
    
    @staticmethod
    def _build_photo_name_item(dbrow):
        name = dbrow[PhotoFields.NAME]
        return PlornAlbumModel._build_name_item(str(name))
    
    @staticmethod
    def _build_dated_item(dated):
        item = QStandardItem(str(dated))
        item.setSelectable(True)
        item.setEditable(False)
        return item
    
    @staticmethod
    def _build_album_dated_item(dbrow):
        dated = dbrow[AlbumFields.DATED]
        item = PlornAlbumModel._build_dated_item(dated)
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        item.setFont(font)
        return item
    
    @staticmethod
    def _build_photo_dated_item(dbrow):
        dated = dbrow[PhotoFields.DATED]
        return PlornAlbumModel._build_dated_item(dated)
    
    @staticmethod
    def _build_count_item(count):
        item = QStandardItem(str(count))
        item.setSelectable(True)
        item.setEditable(False)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    
    @staticmethod
    def _build_album_count_item(dbrow):
        count = dbrow[AlbumFields.PHOTO_COUNT]
        item = PlornAlbumModel._build_count_item(str(count))
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        item.setFont(font)
        return item
    
    @staticmethod
    def _build_photo_count_item(dbrow):
        count = ''
        return PlornAlbumModel._build_count_item(str(count))
    
    @staticmethod
    def _build_path_item(path):
        MAX_PATH = 48
        home = os.environ['HOME']
        path = path.replace(home, '~')
        if len(path) > MAX_PATH:
            rem = len(path) - MAX_PATH
            path = '...' + path[rem:]
        item = QStandardItem(path)
        item.setSelectable(True)
        item.setEditable(False)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        return item
    
    @staticmethod
    def _build_album_path_item(dbrow):
        path = ''
        return PlornAlbumModel._build_path_item(path)
    
    @staticmethod
    def _build_photo_path_item(dbrow):
        path = dbrow[PhotoFields.PATH]
        return PlornAlbumModel._build_path_item(path)
    
    @staticmethod
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
        module_logger.debug(f'_collect_album_dbdata: done, {len(dbdata)} recs')
        return dbdata
    
    @staticmethod
    def _collect_photo_dbdata(db, album_id):
        global module_logger
    
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
            if id not in PlornAlbumModel._PHOTO_DATA:
                PlornAlbumModel._PHOTO_DATA[id] = row_data
    
        module_logger.debug(f'_collect_photo_dbdata: keys {str(dbdata.keys())}')
        module_logger.debug(f'_collect_photo_dbdata: done, {len(dbdata)} recs')
        return dbdata
    
    @staticmethod
    def _build_album_tree(root, db, dbdata):
        global module_logger
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
            id_item = PlornAlbumModel._build_album_id_item(dbrow)
            id = int(id_item.text())
            row_item = QStandardItem(str(row))
            name_item = PlornAlbumModel._build_album_name_item(dbrow)
            dated_item = PlornAlbumModel._build_album_dated_item(dbrow)
            count_item = PlornAlbumModel._build_album_count_item(dbrow)
            path_item = PlornAlbumModel._build_album_path_item(dbrow)
            root.appendRow([id_item, row_item, name_item,
                            dated_item, count_item, path_item])
            current = root.child(row)
    
            #-- the model is zero-based, but the db fields are one-based,
            #   and we only want certain columns anyway
            album_id = dbrow[AlbumFields.ID]
            dbtree[album_id] = [id_item, name_item, dated_item, count_item]
            row += 1
            
            nphotos = 0
            photos = PlornAlbumModel._collect_photo_dbdata(db, album_id)
            for jj, photo_row in photos.items():
                msg  = f'_build_album_tree: photo row {nphotos}, '
                msg += f'{photo_row}'
                module_logger.debug(msg)
                prow_item = QStandardItem(str(nphotos))
                pid_item = PlornAlbumModel._build_photo_id_item(photo_row)
                pid = int(pid_item.text())
                pname_item = PlornAlbumModel._build_photo_name_item(photo_row)
                pdated_item = PlornAlbumModel._build_photo_dated_item(photo_row)
                pcount_item = PlornAlbumModel._build_photo_count_item(photo_row)
                ppath_item = PlornAlbumModel._build_photo_path_item(photo_row)
                current.appendRow([pid_item, prow_item, pname_item,
                                   pdated_item, pcount_item, ppath_item])
                nphotos += 1
    
        module_logger.debug('_build_album_tree: done')
        return dbtree
    
    @staticmethod
    def _dump_album_tree(root, dbtree):
        global module_logger
    
        if module_logger.isEnabledFor(logging.DEBUG):
            module_logger.debug('=> _dump_album_tree start')
            if root.hasChildren():
                for row in range(len(PlornAlbumModel._ALBUM_DATA)):
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
    
    @staticmethod
    def add_album(root, album, db=None):
        global module_logger
    
        msg  = f'add_album: {str(album)}'
        module_logger.debug(msg)
    
        if db == None:
            config = PlornConfig()
            catalog, dirname, dbname = config.get_current_catalog()
            db = QSqlDatabase.database(connectionName=catalog)
            msg  = f'add_album: using db connection {catalog}'
            module_logger.debug(msg)
    
        if not db.isOpen():
            msg  = 'add_album: cannot open database'
            module_logger.debug(msg)
            return 'cannot open db'
    
        if not db.isValid():
            msg  = 'add_album: database is not valid'
            module_logger.debug(msg)
            return 'db is invalid'
    
        # add to db to get an id and actual dbrow
        # ...we do not care about duplicate names, so try adding it
        added_album = PlornDbOperations.add_album(album)
        module_logger.debug(f'add_album: added album {str(added_album)}')
        assert added_album != None and added_album.get_id() != 0
    
        row_data = [added_album.get_id(),
                    added_album.get_name(),
                    added_album.get_dated(),
                    added_album.get_notes(),
                    added_album.get_photo_count()]
        PlornAlbumModel._ALBUM_DATA[added_album.get_id()] = row_data
        module_logger.debug(f'add_album: added {row_data}')
        row_item = QStandardItem(str(root.rowCount()+1))
        id_item = PlornAlbumModel._build_album_id_item(row_data)
        name_item = PlornAlbumModel._build_album_name_item(row_data)
        dated_item = PlornAlbumModel._build_album_dated_item(row_data)
        count_item = PlornAlbumModel._build_album_count_item(row_data)
        path_item = PlornAlbumModel._build_album_path_item(row_data)
        root.appendRow([id_item, row_item, name_item, dated_item, count_item,
                        path_item])
        module_logger.debug(f'add_album: okay and done')
        return 'okay'
        
    @staticmethod
    def update_album(root, album, updates, db=None):
        global module_logger
    
        msg  = f'update_album: {str(album)}'
        module_logger.debug(msg)
    
        if db == None:
            config = PlornConfig()
            catalog, dirname, dbname = config.get_current_catalog()
            db = QSqlDatabase.database(connectionName=catalog)
            msg  = f'update_album: using db connection {catalog}'
            module_logger.debug(msg)
    
        if not db.isOpen():
            msg  = 'update_album: cannot open database'
            module_logger.debug(msg)
            return 'cannot open db'
    
        if not db.isValid():
            msg  = 'update_album: database is not valid'
            module_logger.debug(msg)
            return 'db is invalid'
    
        album = PlornDbOperations.update_album(album, updates)
        module_logger.debug(f'add_album: updated album {str(album)}')
        assert album != None and album.get_id() != 0
    
        row_data = [album.get_id(),
                    album.get_name(),
                    album.get_dated(),
                    album.get_notes(),
                    album.get_photo_count()]
        PlornAlbumModel._ALBUM_DATA[album.get_id()] = row_data
        module_logger.debug(f'update_album: added {row_data}')
        album_id = f'{album.get_id():04}'
        model = root.model()
        row_items = model.findItems(album_id, column=0)
        if len(row_items) < 1:
            return 'cannot find entry in tree view'
        row = row_items[0].row()
        name = model.item(row, CatalogColumns.NAME)
        name.setText(album.get_name())
        dated = model.item(row, CatalogColumns.DATED)
        dated.setText(album.get_dated())
        count = model.item(row, CatalogColumns.COUNT)
        count.setText(str(album.get_photo_count()))
        module_logger.debug(f'update_album: okay and done')
        return 'okay'
        
    @staticmethod
    def remove_album(root, album_id, album_name, db=None):
        global module_logger
    
        msg  = f'remove_album: {album_name}'
        module_logger.debug(msg)
    
        if db == None:
            config = PlornConfig()
            catalog, dirname, dbname = config.get_current_catalog()
            db = QSqlDatabase.database(connectionName=catalog)
            msg  = f'remove_album: using db connection {catalog}'
            module_logger.debug(msg)
    
        if not db.isOpen():
            msg  = 'remove_album: cannot open database'
            module_logger.debug(msg)
            return 'cannot open db'
    
        if not db.isValid():
            msg  = 'remove_album: database is not valid'
            module_logger.debug(msg)
            return 'db is invalid'
    
        # remove from db and model
        items = root.model().findItems(album_name, column=2)
        module_logger.debug(f'remove_album: items {str(items)}')
        res = PlornDbOperations.remove_album_by_id(album_id)
        if res:
            module_logger.debug(f'remove_album: album {album_name} gone')
        if len(items) > 0:
            module_logger.debug(f'remove_album: found {len(items)}')
            row = items[0].row()
            root.model().beginRemoveRows(root.index(), row, row)
            root.model().removeRow(row, root.index())
            root.model().endRemoveRows()
        row_data = PlornAlbumModel._ALBUM_DATA[album_id]
        del PlornAlbumModel._ALBUM_DATA[album_id]
        module_logger.debug(f'remove_album: okay and done')
        return 'okay'
    
    @staticmethod
    def album_list():
        global module_logger

        albums = []
        for ii, data in PlornAlbumModel._ALBUM_DATA.items():
            album_id = data[AlbumFields.ID]
            album_name = data[AlbumFields.NAME]
            albums.append([album_id, album_name])
        return albums

    @staticmethod
    def photo_list(album_id):
        global module_logger

        module_logger.debug(f'photo_list: look for album {album_id}')
        photos = []
        for ii, data in PlornAlbumModel._PHOTO_DATA.items():
            module_logger.debug(f'photo_list: found {ii}, {data}')
            photo_id = data[PhotoFields.ID]
            parent_id = data[PhotoFields.ALBUM_ID]
            if int(parent_id) == int(album_id):
                photo_name = data[PhotoFields.NAME]
                photo_dated = data[PhotoFields.DATED]
                photo_path = data[PhotoFields.PATH]
                photos.append([photo_id, photo_name, photo_dated, photo_path])
        module_logger.debug(f'photo_list: found {len(photos)} photos')
        return photos

    @staticmethod
    def _increment_photo_count(root, album_id):
        global module_logger

        row = PlornAlbumModel._ALBUM_DATA[int(album_id)]
        module_logger.debug(f'_increment_photo_count: row {row}')
        name = row[AlbumFields.NAME]
        count = row[AlbumFields.PHOTO_COUNT]
        count += 1
        row[AlbumFields.PHOTO_COUNT] = count
        module_logger.debug(f'_increment_photo_count: album {name}, {count}')
        row_items = root.model().findItems(f'{int(album_id):04}', column=0)
        if len(row_items) > 0:
            item = root.model().item(row_items[0].row(), CatalogColumns.COUNT)
            item.setText(str(count))

    @staticmethod
    def add_photo(root, photo, db=None):
        global module_logger 
    
        msg  = f'add_photo: {str(photo)}'
        module_logger.debug(msg)
    
        if db == None:
            config = PlornConfig()
            catalog, dirname, dbname = config.get_current_catalog()
            db = QSqlDatabase.database(connectionName=catalog)
            msg  = f'add_photo: using db connection {catalog}'
            module_logger.debug(msg)
    
        if not db.isOpen():
            msg  = 'add_photo: cannot open database'
            module_logger.debug(msg)
            return 'cannot open db'
    
        if not db.isValid():
            msg  = 'add_photo: database is not valid'
            module_logger.debug(msg)
            return 'db is invalid'
    
        # add to db to get an id and actual dbrow
        # ...we do not care about duplicate names, so try adding it
        added_photo = PlornDbOperations.add_photo(photo)
        module_logger.debug(f'add_photo: added photo {str(added_photo)}')
        assert added_photo != None and added_photo.get_id() != 0
    
        row_data = [added_photo.get_id(),
                    added_photo.get_album_id(),
                    added_photo.get_name(),
                    added_photo.get_path(),
                    added_photo.get_dated(),
                    added_photo.get_notes()]
        PlornAlbumModel._PHOTO_DATA[added_photo.get_id()] = row_data
        PlornAlbumModel._increment_photo_count(root, added_photo.get_album_id())
        module_logger.debug(f'add_photo: added {row_data}')

        row_item = QStandardItem(str(root.rowCount()+1))
        id_item = PlornAlbumModel._build_photo_id_item(row_data)
        name_item = PlornAlbumModel._build_photo_name_item(row_data)
        dated_item = PlornAlbumModel._build_photo_dated_item(row_data)
        count_item = PlornAlbumModel._build_photo_count_item(row_data)
        path_item = PlornAlbumModel._build_photo_path_item(row_data)

        row_items = root.model().findItems(f'{added_photo.get_album_id():04}',
                                           column=0)
        if len(row_items) > 0:
            row_items[0].appendRow([id_item, row_item, name_item,
                                    dated_item, count_item, path_item])
        module_logger.debug(f'add_photo: okay and done')
        return 'okay'
        
