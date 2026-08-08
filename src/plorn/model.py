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
    QAbstractItemModel,
    QAbstractTableModel,
    QModelIndex,
    Qt,
)

from PyQt6.QtGui import (
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
        self.setHeaderData(AlbumFields.ID,
                           Qt.Orientation.Horizontal, 'ID')
        self.setHeaderData(AlbumFields.NAME,
                           Qt.Orientation.Horizontal, 'Album')
        self.setHeaderData(AlbumFields.DATED,
                           Qt.Orientation.Horizontal, 'Dated')
        self.setHeaderData(AlbumFields.NOTES,
                           Qt.Orientation.Horizontal, 'Notes')
        self.setHeaderData(AlbumFields.PHOTO_COUNT,
                           Qt.Orientation.Horizontal, 'Photo Count')
        res = self.select()
        module_logger.debug(f'album model init: select result {res}')


##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

_DBDATA = {}

def populate_attrs(root, table='names', db=QSqlDatabase()):
    global module_logger, _DBDATA

    msg  = f'populate_attrs:{table} init: db {db.connectionName()}'
    module_logger.debug(msg)

    dbdata = _collect_attr_dbdata(table, db)
    _DBDATA = dbdata
    dbtree = _build_attr_tree(root, dbdata)
    _dump_attr_tree(root, dbtree)
    module_logger.debug(f'populate_attrs: {table} init done')

def add_attrs(root, parent, value, table='names', db=QSqlDatabase()):
    global module_logger, _DBDATA

    msg  = f'add_attr: add {value} to {table} in db {db.connectionName()}'
    module_logger.debug(msg)

    if len(value) < 1:          # should be a string and actual QStandardItem
        return False
    if parent == None:
        parent = root
    msg  = f'add_attr: appending row {value} to "{parent.text()}"'
    module_logger.debug(msg)
    pid = 0
    if parent.data() and len(parent.data()) > 0:
        pid = parent.data()[AttrFields.PARENT_ID]
    # add to db to get an id and actual dbrow
    item = _build_attr_item([-1, pid, value])
    parent.appendRow(item)                  # add to treeview
    return True

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

