
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

from enum import IntEnum
import logging
import os

from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
)

from PyQt6.QtSql import (
    QSqlDatabase,
)

from PyQt6.QtGui import (
    QFont,
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QTreeView,
    QWidget,
)

from plorn import PlornAlbum
from plorn.config import PlornConfig

from plorn.model import (
    add_attrs,
    model_add_album,
    model_remove_album,
    populate_albums,
    populate_attrs,
    PlornDbOperations,
    remove_attrs,
)

from plorn.widgets.albums import (
    PlornAlbumDialog,
    PlornViewAlbumDialog,
)

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.DEBUG)

class TreeColumns(IntEnum):
    ID            = 0
    HIDDEN_ROW_ID = 1
    NAME          = 2
    DATED         = 3
    COUNT         = 4
    PATH          = 5


#####################################################################
#
#   Generally useful widgets
#
class PlornSizePolicy(QSizePolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalPolicy = QSizePolicy.Policy.Expanding
        self.verticalPolicy = QSizePolicy.Policy.Expanding

######################################################################
#
#   Widgets used directly by the main application window
#
class PlornAttrView(QDialog):
    '''
    common widget class for displaying and editing attributes, one
    data model at a time
    '''
    def __init__(self, title=None, table='names',
                 db=None, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug(f'entering PlornAttrView: table {table}')
        self.title = title
        self.table = table
        self.db = db
        self.model = QStandardItemModel()
        self.root = self.model.invisibleRootItem()

        if title:
            wtitle = f'Manage {title.capitalize()}'
        else:
            wtitle = 'Manage Attributes'
        self.setWindowTitle(wtitle)
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        tree = QTreeView(parent=self)
        tree.setModel(self.model)
        tree.setAlternatingRowColors(True)
        tree.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        tree.setItemsExpandable(True)
        tree.setUniformRowHeights(True)
        tree.setHeaderHidden(True)
        tree.header().setSectionHidden(TreeColumns.HIDDEN_ROW_ID, True)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.context_menu)
        tree.setToolTip('Right-click for actions')
        self.tree = tree
        layout.addWidget(self.tree, 0, 0)
        populate_attrs(self.root, table=self.table, db=self.db)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug(f'PlornAttrView all done: table {table}')
 
    def dlg_done(self, button):
        global module_logger

        role = self.bbox.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Ok:
            module_logger.debug('attrs: Ok clicked')
            self.setResult(QDialog.DialogCode.Accepted)

        elif role == QDialogButtonBox.StandardButton.Cancel:
            module_logger.debug('attrs: Cancel clicked')
            self.setResult(QDialog.DialogCode.Rejected)

        self.close()

    def context_menu(self, position):
        global module_logger

        module_logger.debug(f'context_menu entered: {self.table}')
        index = self.tree.indexAt(position)
        menu = QMenu()
        menu.setObjectName('attr_context_menu')
        menu.setTitle('Actions')
        if not index.isValid():
            module_logger.debug('context_menu: assume invisible root')
            add_sib_action = menu.addAction('Add',
                     lambda: self.add_attr_sib(self.model.invisibleRootItem()))
        else:
            item = self.model.itemFromIndex(index)
            add_sib_action = menu.addAction('Add Sibling',
                                   lambda: self.add_attr_sib(item))
            add_child_action = menu.addAction('Add Child',
                                   lambda: self.add_attr_child(item))
            remove_action = menu.addAction('Remove',
                                   lambda: self.remove_attr(item))
        expand_action = menu.addAction('Expand All', self.tree.expandAll)
        collapse_action = menu.addAction('Collapse All', self.tree.collapseAll)
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        module_logger.debug(f'context_menu done: {self.table}')

    def add_attr_sib(self, item):
        global module_logger

        module_logger.debug(f'add_attr_sib entered: {self.table}')
        title = f'Add Sibling {self.title.capitalize()}'
        label_txt = f'Add {self.title.capitalize()}:'
        if self.title[-1] == 's':    # English specific ...
            label_txt = f'Add {self.title[0:-1].capitalize()}:'

        ptxt = 'invisibleRoot'
        parent = self.model.invisibleRootItem()
        if item and item != self.model.invisibleRootItem():
            parent = item.parent()
            if parent and parent != self.model.invisibleRootItem():
                ptxt = f' parent = {parent.text()}'

        input_value, ok = QInputDialog.getText(self, title, label_txt)
        if ok and input_value:
            res = add_attrs(self.model.invisibleRootItem(), parent, input_value,
                            table=self.table, db=self.db)
            if res == 'cannot insert' or res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()} "{input_value}"'
                button = QMessageBox.critical(self, title, label_txt)
                return
            if res == 'duplicate attribute':
                title = 'Duplicate Attribute'
                label_txt  = f'"{input_value}" is already a sibling'
                if parent and parent != self.model.invisibleRootItem():
                    label_txt += f' of "{parent.text()}"'
                else:
                    label_txt += f' at the top most level'
                button = QMessageBox.critical(self, title, label_txt)
                return
            if parent != None:
                self.tree.setExpanded(parent.index(), True)
            module_logger.debug(f'add_attr_sib {res}: {input_value}, {ptxt}')
        else:
            module_logger.debug(f'add_attr_sib canceled: {input_value}, {ptxt}')

        module_logger.debug(f'add_attr_sib done: {self.table}')

    def add_attr_child(self, item):
        global module_logger

        module_logger.debug(f'add_attr_child entered: {self.table}')
        title = f'Add Child {self.title.capitalize()}'
        if self.title[-1] == 's':    # English specific ...
            label_txt = f'Add {self.title[0:-1].capitalize()}:'
        msg  = f'add_attr_child {self.table}:'
        msg += f' add child to {item.text()}'
        module_logger.debug(msg)
        label_txt = f'Add child to {item.text()}:'

        ptxt = 'invisibleRoot'
        if item and item != self.model.invisibleRootItem():
            ptxt = f' parent = {item.text()}'
        input_value, ok = QInputDialog.getText(self, title, label_txt)
        if ok and input_value:
            res = add_attrs(self.model.invisibleRootItem(), item, input_value,
                            table=self.table, db=self.db)
            if res == 'cannot insert' or res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()} "{input_value}"'
                button = QMessageBox.critical(self, title, label_txt)
                return
            if res == 'duplicate attribute':
                title = 'Duplicate Attribute'
                label_txt  = f'"{input_value} is already a child'
                if item and item != self.model.invisibleRootItem():
                    label_txt += f' of {item.text()}'
                else:
                    label_txt += f' at the top most level'
                button = QMessageBox.critical(self, title, label_txt)
                return
            self.tree.setExpanded(item.index(), True)
            module_logger.debug(
                f'add_attr_child add {res}: {input_value}, {ptxt}')
        else:
            module_logger.debug(
                f'add_attr_child canceled: {input_value}, {ptxt}')

        module_logger.debug(f'add_attr_child done: {self.table}')

    def remove_attr(self, item):
        global module_logger

        module_logger.debug(f'remove_attr entered: {self.table}')
        title = f'Remove {self.title.capitalize()}'
        if self.title[-1] == 's':    # English specific ...
            label_txt = f'Add {self.title[0:-1].capitalize()}:'
        msg  = f'remove_attr "{item.text()}" from {self.table}:'
        module_logger.debug(msg)
        label_txt = f'Remove "{item.text()}"'
        if item.hasChildren():
            label_txt += ' and children'
        label_txt += '?'
        parent = item.parent()
        if not parent:
            parent = self.model.invisibleRootItem()
        value = item.text()
        button = QMessageBox.question(self, title, label_txt)
        if button == QMessageBox.StandardButton.Yes:
            module_logger.debug(f'remove_attr? Yes')
            res = remove_attrs(self.model.invisibleRootItem(), item,
                               table=self.table, db=self.db)
            module_logger.debug(f'remove_attr: remove_attrs result "{res}"')
            if res == 'cannot delete root' or \
               res == 'cannot delete db index 0' or \
               res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()}'
                button = QMessageBox.critical(self, title, label_txt)
                return
            self.tree.setExpanded(parent.index(), True)
            module_logger.debug(
                f'remove_attr: removed "{value}" from "{parent.text()}"')
        else:
            module_logger.debug(f'remove_attr? No')

        module_logger.debug(f'remove_attr done: {self.table}')


class PlornAlbumView(QWidget):
    '''
    widget class for displaying and editing albums and their photos
    '''
    catalogChanged = pyqtSignal(int, name='catalogChanged')

    def __init__(self, db=None, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAlbumView')
        self.setObjectName('PlornAlbumView')
        self.db = db
        self.model = QStandardItemModel()
        self.root = self.model.invisibleRootItem()

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        font = QFont()
        font.setBold(True)
        self.model.setColumnCount(5)
        hdr_id = QStandardItem('ID')
        hdr_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_id.setFont(font)
        self.model.setHorizontalHeaderItem(0, hdr_id)
        hdr_name = QStandardItem('Album/Photo')
        hdr_name.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                                  Qt.AlignmentFlag.AlignVCenter)
        hdr_name.setFont(font)
        self.model.setHorizontalHeaderItem(2, hdr_name)
        hdr_dated = QStandardItem('Dated')
        hdr_dated.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_dated.setFont(font)
        self.model.setHorizontalHeaderItem(3, hdr_dated)
        hdr_count = QStandardItem('Photo\nCount')
        hdr_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_count.setFont(font)
        self.model.setHorizontalHeaderItem(4, hdr_count)
        hdr_path = QStandardItem('Path')
        hdr_path.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_path.setFont(font)
        self.model.setHorizontalHeaderItem(5, hdr_path)

        tree = QTreeView(parent=self)
        tree.setModel(self.model)
        tree.setAlternatingRowColors(True)
        tree.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        tree.setItemsExpandable(True)
        tree.setUniformRowHeights(True)
        tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.context_menu)
        tree.setToolTip('Right-click for actions')
        tree.doubleClicked.connect(self.view_object)
        self.tree = tree
        layout.addWidget(self.tree, 0, 0)

        tree.setHeaderHidden(False)
        tree.header().setSectionHidden(TreeColumns.HIDDEN_ROW_ID, True)
        tree.header().resizeSection(TreeColumns.ID, 100)
        tree.header().resizeSection(TreeColumns.HIDDEN_ROW_ID, 10)
        tree.header().resizeSection(TreeColumns.NAME, 440)
        tree.header().resizeSection(TreeColumns.DATED, 240)
        tree.header().resizeSection(TreeColumns.COUNT, 100)

        self.setLayout(layout)
        populate_albums(root=self.root, db=self.db)
        self.tree.expandAll()
        module_logger.debug('PlornAlbumView all done')
 
    def selected_rows(self):
        return self.tree.selectedIndexes()

    def item_from_index(self, index):
        return self.tree.model().itemFromIndex(index)

    def current_index(self):
        return self.tree.currentIndex()

    def select_all(self):
        return self.tree.selectAll()

    def set_focus(self):
        return self.tree.setFocus()

    def has_focus(self):
        return self.tree.hasFocus()

    def switch_model(self):
        global module_logger

        res = None
        module_logger.debug('switch_model entered: album view')
        self.model.removeRows(0, self.model.rowCount())
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        if catalog not in QSqlDatabase.connectionNames():
            self.db = QSqlDatabase.addDatabase('QSQLITE',
                                               connectionName=catalog)
            dbpath = os.path.expanduser(os.path.join(datadir, dbname))
            self.db.setDatabaseName(dbpath)
            self.db.open()
        self.db = QSqlDatabase.database(connectionName=catalog)
        if self.db.isOpen():
            res = self.db
        else:
            module_logger.debug(f'switch_model db open? {self.db.isOpen()}')
        populate_albums(root=self.root, db=self.db)
        module_logger.debug('switch_model done: album view')
        return res

    def context_menu(self, position):
        global module_logger

        module_logger.debug(f'context_menu entered: album view')
        index = self.tree.indexAt(position)
        menu = QMenu()
        menu.setObjectName('album_context_menu')
        menu.setTitle('Actions')
        add_album_action = None
        if not index.isValid():
            module_logger.debug('context_menu: assume invisible root')
            add_album_action = menu.addAction('Add Album',
                                    lambda: self.add_album_action())
        else:
            item = self.model.itemFromIndex(index)
            if item.parent() == None:           # album selected
                add_album_action = menu.addAction('Add Album',
                                    lambda: self.add_album_action())
                edit_album_action = menu.addAction('Edit Album',
                                    lambda: self.edit_album_action())
                remove_album_action = menu.addAction('Remove Album',
                                    lambda: self.remove_album_action())
                menu.addSeparator()
                sshow_album_action = menu.addAction('Slide Show',
                                    lambda: self.slide_show_action())
            else:                               # photo selected
                add_child_action = menu.addAction('Add Photo(s)',
                                   lambda: self.add_photos_action(item.parent()))
                edit_photo_action = menu.addAction('Edit Photo',
                                    lambda: self.edit_photo_action(item))
                remove_action = menu.addAction('Remove Photo',
                                   lambda: self.remove_photo_action(item))

        expand_action = menu.addAction('Expand All', self.tree.expandAll)
        collapse_action = menu.addAction('Collapse All', self.tree.collapseAll)
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        if hasattr(self, 'context_add_album_action'):
            add_album_action.setObjectName('context_add_album_action')
            self.context_add_album_action = add_album_action
        else:
            setattr(self, 'context_add_album_action', add_album_action)
        module_logger.debug(f'context_menu done: album view')

    def view_album(self, id):
        global module_logger

        module_logger.debug(f'view_album: entered for album {id}')
        album = PlornDbOperations.get_album_by_id(id)
        if album == None:
            raise PlornDbError('album selected that does not exist')
        else:
            dlg = PlornViewAlbumDialog(tree=self.tree,
                                       title='View Album',
                                       allow_edit=False)
            dlg.set_inputs(album)
            info = PlornViewAlbumDialog.ask(dlg)
        module_logger.debug(f'view_album: done for album {id}')

    def view_photo(self, index):
        global module_logger

        item = self.tree.model().itemFromIndex(index)
        module_logger.debug(f'view_photo: entered for "{item.text()}"')
        pass

    def view_object(self, index):
        global module_logger

        item = self.tree.model().itemFromIndex(index)
        value = item.text()
        module_logger.debug(f'view_object: entered for "{value}"')
        indices = self.tree.selectedIndexes()
        id = 0
        found_count = False
        found_path  = False
        for idx in indices:
            item = self.tree.model().itemFromIndex(idx)
            #module_logger.debug(f'view_object: column {item.column()}')
            if item.column() == TreeColumns.ID:
                id = int(item.text())
            elif item.column() == TreeColumns.COUNT:
                if len(item.text()) >= 1:
                    found_count = True
            elif item.column() == TreeColumns.PATH:
                if len(item.text()) >= 1:
                    found_path = True
        if found_count and not found_path:          # object is an album
            #module_logger.debug(f'view_object: it is an album')
            self.view_album(id)
        elif found_path and not found_count:        # object is a photo
            module_logger.debug(f'view_object: it is a photo')
        module_logger.debug(f'view_object: done for "{value}"')

    def add_album(self, name, dated, notes):
        global module_logger

        module_logger.debug(f'add_album: entered "{name}" "{dated}"')
        album = PlornAlbum(name, id=None, dated=dated, notes=notes)
        root = self.model.invisibleRootItem()
        res = model_add_album(root, album, db=self.db)
        if res == 'cannot insert' or res == 'retrieve failed':
            title = 'Internal Album Database Failure'
            label_txt  = f'{res.capitalize()} "{name}"'
            button = QMessageBox.critical(self, title, label_txt)
            return False
        module_logger.debug(f'add_album: done "{name}"')
        return True

    def add_album_action(self):
        global module_logger

        module_logger.debug(f'add_album_action: entered')
        new_album_dlg = PlornAlbumDialog(tree=self.tree, title='Add Album')
        info = PlornAlbumDialog.ask(new_album_dlg)
        if len(info) > 0:
            res = self.add_album(info['album'], info['dated'], info['notes'])
        new_album_dlg.close()

    def remove_album_action(self):
        global module_logger

        module_logger.debug(f'remove_album_action: entered')
        indices = self.selected_rows()
        if len(indices) < 1:
            title = 'Remove an Album'
            text = 'No album has been selected for removal.'
            button = QMessageBox.critical(self, title, text)
        else:
            album_name = ''
            album_id = 0
            album_row = -1
            for index in indices:
                item = self.item_from_index(index)
                if item.column() == TreeColumns.ID:
                    album_id = int(item.text())
                    album_row = item.row()
                if item.column() == TreeColumns.NAME:
                    album_name = item.text()

            root = self.tree.model().invisibleRootItem()
            res = model_remove_album(root, album_id, album_name)
            self.catalogChanged.emit(0)
        module_logger.debug(f'remove_album_action: done')

    def remove_album(self, item):
        global module_logger

        module_logger.debug(f'remove_album entered: {self.table}')
        title = f'Remove {self.title.capitalize()}'
        if self.title[-1] == 's':    # English specific ...
            label_txt = f'Add {self.title[0:-1].capitalize()}:'
        msg  = f'remove_album "{item.text()}" from {self.table}:'
        module_logger.debug(msg)
        label_txt = f'Remove "{item.text()}"'
        if item.hasChildren():
            label_txt += ' and children'
        label_txt += '?'
        parent = item.parent()
        if not parent:
            parent = self.model.invisibleRootItem()
        value = item.text()
        button = QMessageBox.question(self, title, label_txt)
        if button == QMessageBox.StandardButton.Yes:
            module_logger.debug(f'remove_album? Yes')
            res = remove_albums(self.model.invisibleRootItem(), item,
                               table=self.table, db=self.db)
            if res == 'cannot delete root' or \
               res == 'cannot delete db index 0' or \
               res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()}'
                button = QMessageBox.critical(self, title, label_txt)
                return
            self.tree.setExpanded(parent.index(), True)
            module_logger.debug(
                f'remove_album: removed "{value}" from "{parent.text()}"')
        else:
            module_logger.debug(f'remove_album? No')

        module_logger.debug(f'remove_album done: {self.table}')


