#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import sys

from PyQt6.QtCore import (
    Qt,
)

from PyQt6.QtGui import (
    QStandardItem,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlQuery,
)

from plorn import (
    AttrFields,
)

module_logger = logging.getLogger('plorn.model.attrs')
module_logger.setLevel(logging.DEBUG)


##########################################################################
#
#   data model for Attributes -- use QStandardItem model directly, so
#   these are helper functions to populate the model
#

class PlornAttrModel:
    _NAMES_DATA = {}
    _PLACES_DATA = {}
    _TAGS_DATA = {}
    
    @staticmethod
    def _set_table_data(table, dbdata):
        global module_logger
    
        if table == 'name':
            PlornAttrModel._NAMES_DATA = dbdata
        elif table == 'places':
            PlornAttrModel._PLACES_DATA = dbdata
        elif table == 'tags':
            PlornAttrModel._TAGS_DATA = dbdata
        else:
            return None
    
    @staticmethod
    def _add_table_data(table, id, data):
        global module_logger
    
        if table == 'name':
            PlornAttrModel._NAMES_DATA[id] = data
        elif table == 'places':
            PlornAttrModel._PLACES_DATA[id] = data
        elif table == 'tags':
            PlornAttrModel._TAGS_DATA[id] = data
        else:
            return None
    
    @staticmethod
    def _del_table_data(table, id):
        global module_logger
    
        if table == 'name':
            del PlornAttrModel._NAMES_DATA[id]
        elif table == 'places':
            del PlornAttrModel._PLACES_DATA[id]
        elif table == 'tags':
            del PlornAttrModel._TAGS_DATA[id]
        else:
            return None
    
    @staticmethod
    def _in_table_keys(table, id):
        global module_logger
    
        if table == 'name':
            return id in PlornAttrModel._NAMES_DATA.keys()
        elif table == 'places':
            return id in PlornAttrModel._PLACES_DATA.keys()
        elif table == 'tags':
            return id in PlornAttrModel._TAGS_DATA.keys()
        else:
            return False
    
    @staticmethod
    def populate_attrs(root, table='names', db=QSqlDatabase()):
        global module_logger
    
        module_logger.debug(f'populate_attrs: {table} init')
        dbdata = PlornAttrModel._collect_attr_dbdata(table, db)
        PlornAttrModel._set_table_data(table, dbdata)
        dbtree = PlornAttrModel._build_attr_tree(root, dbdata)
        PlornAttrModel._dump_attr_tree(root, dbtree)
        module_logger.debug(f'populate_attrs: {table} init done')
    
    @staticmethod
    def add_attrs(root, parent, value, table='names', db=QSqlDatabase()):
        global module_logger
    
        msg  = f'add_attrs: add {value} to {table} in db {db.connectionName()}'
        module_logger.debug(msg)
    
        if len(value) < 1:        # should be a string and actual QStandardItem
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
        item = PlornAttrModel._build_attr_item(row)
        parent.appendRow(item)                          # add to treeview
        PlornAttrModel._add_table_data(table, id, item) # save for the "model"
        module_logger.debug(f'add_attrs: okay and done')
        return 'okay'
    
    @staticmethod
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
            res = PlornAttrModel.remove_attrs(root, item.child(0),
                                              table=table, db=db)
    
        sql  = f'DELETE FROM {table} WHERE id = {id};'
        query = QSqlQuery(sql, db=db)
        if not query:
            module_logger.debug(f'remove_attrs: retrieval of row failed')
            return 'retrieve failed'
        module_logger.debug(f'remove_attrs: deleted {row} from {table}')
    
        module_logger.debug(msg)
        value = item.text()
        parent.removeRow(item.row())                    # remove from treeview
        if PlornAttrModel._in_table_keys(table, id):
            msg = f'remove_attrs: deleting "{value}" from _ATTR_DATA'
            module_logger.debug(msg)
            PlornAttrModel._del_table_data(table, id)
        module_logger.debug(f'remove_attrs: okay and done')
        return 'okay'
    
    @staticmethod
    def _build_attr_item(dbrow):
        id = dbrow[AttrFields.ID]
        parent_id = dbrow[AttrFields.PARENT_ID]
        value = dbrow[AttrFields.VALUE]
        item = QStandardItem(str(value))
        item.setEditable(True)
        item.setCheckable(False)
        item.setData([id, parent_id, value])
        return item
    
    @staticmethod
    def _collect_attr_dbdata(table, db):
        global module_logger
    
        module_logger.debug('_collect_dbdata: entered')
        dbdata = {}
        query = QSqlQuery(f'SELECT * FROM {table};', db=db)
        while query.next():
            row_data = [query.value(AttrFields.ID),
                        query.value(AttrFields.PARENT_ID),
                        query.value(AttrFields.VALUE)]
            dbdata[query.value(AttrFields.ID)] = \
                                    PlornAttrModel._build_attr_item(row_data)
        module_logger.debug(f'_collect_dbdata: keys {str(dbdata.keys())}')
        module_logger.debug(f'_collect_dbdata: done, {len(dbdata)} records')
        return dbdata
    
    @staticmethod
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
    
    @staticmethod
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
                 PlornAttrModel._dump_attr_tree(root, dbtree, ii, level+1)
            if level == 0:
                module_logger.debug('<= _dump_attr_tree end')
    
