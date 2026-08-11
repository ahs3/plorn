#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os.path
import sys
import traceback

from plorn.config import PlornConfig
from plorn.db import AlbumFields, PhotoFields

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

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.DEBUG)

from plorn.db import AttrFields

##########################################################################
#
#   data model for Albums -- use simple relational model
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

_ALBUM_DATA = {}

def populate_albums(root, db=QSqlDatabase()):
    global module_logger, _ALBUM_DATA

    msg  = f'populate_albums: init: db {db.connectionName()}'
    module_logger.debug(msg)

    root.setColumnCount(5)
    dbdata = _collect_album_dbdata(db)
    _ALBUM_DATA = dbdata
    dbtree = _build_album_tree(root, dbdata)
    _dump_album_tree(root, dbtree)
    module_logger.debug(f'populate_albums: init done')

def album_stats():
    global module_logger, _ALBUM_DATA

    album_count = len(_ALBUM_DATA)
    photo_count = 0
    for ii in _ALBUM_DATA.keys():
        module_logger.debug(f'album_stats: {_ALBUM_DATA[ii][AlbumFields.NAME]}')
        nphotos = _ALBUM_DATA[ii][AlbumFields.PHOTO_COUNT]
        photo_count += nphotos
    return album_count, photo_count

def _build_album_id_item(dbrow):
    id = dbrow[AlbumFields.ID]
    item = QStandardItem(f'{id:04}')
    item.setEditable(False)
    item.setCheckable(False)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item

def _build_album_name_item(dbrow):
    name = dbrow[AlbumFields.NAME]
    item = QStandardItem(str(name))
    item.setEditable(True)
    item.setCheckable(False)
    return item

def _build_album_count_item(dbrow):
    count = dbrow[AlbumFields.PHOTO_COUNT]
    item = QStandardItem(str(count))
    item.setEditable(False)
    item.setCheckable(False)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item

def _build_photo_path_item(dbrow):
    #id = dbrow[AlbumFields.ID]
    #item = QStandardItem(f'{id:04}')
    item = QStandardItem('')
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

def _build_album_tree(root, dbdata):
    global module_logger
    '''
        NB: whilst the database itself if a 1-based array,
        with ID pointing to parents, Qt expects an actual tree
        structure when working with QTreeView.  So, build the
        structure up from our dbdata.
    '''
    module_logger.debug('_build_albumr_tree: entered')
    dbtree = {}
    row = 0
    for ii, dbrow in dbdata.items():
        id_item = _build_album_id_item(dbrow)
        root.model().setItem(row, 1, id_item)
        name_item = _build_album_name_item(dbrow)
        root.model().setItem(row, 2, name_item)
        count_item = _build_album_count_item(dbrow)
        root.model().setItem(row, 3, count_item)

        #-- the model is zero-based, but the db fields are one-based,
        #   and we only want certain columns anyway
        id = dbrow[AlbumFields.ID]
        dbtree[id] = [id_item, name_item, count_item]
        row += 1
    module_logger.debug('_build_album_tree: done')
    return dbtree

def _dump_album_tree(root, dbtree):
    pass


##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

_ATTR_DATA = {}

def populate_attrs(root, table='names', db=QSqlDatabase()):
    global module_logger, _ATTR_DATA

    msg  = f'populate_attrs:{table} init: db {db.connectionName()}'
    module_logger.debug(msg)

    dbdata = _collect_attr_dbdata(table, db)
    _ATTR_DATA = dbdata
    dbtree = _build_attr_tree(root, dbdata)
    _dump_attr_tree(root, dbtree)
    module_logger.debug(f'populate_attrs: {table} init done')

def add_attrs(root, parent, value, table='names', db=QSqlDatabase()):
    global module_logger, _ATTR_DATA

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
    _ATTR_DATA[id] = item                              # save if for the "model"
    module_logger.debug(f'add_attrs: okay and done')
    return 'okay'

def remove_attrs(root, item, table='names', db=QSqlDatabase()):
    global module_logger, _ATTR_DATA

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
    if id in _ATTR_DATA.keys():
        msg = f'remove_attrs: deleting "{value}" from _ATTR_DATA'
        module_logger.debug(msg)
        del _ATTR_DATA[id]
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

