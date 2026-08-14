
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

from enum import IntEnum
import logging

from PyQt6.QtCore import (
    QSize,
    Qt,
)

from PyQt6.QtSql import (
    QSqlRelationalDelegate,
)

from PyQt6.QtGui import (
    QFont,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListView,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTextEdit,
    QTreeView,
    QWidget,
)

from plorn import (
    AlbumFields,
    AttrFields,
    PlornAlbum,
)

from plorn.config import PlornConfig

from plorn.model import (
    populate_albums,
    populate_attrs,
    add_attrs,
    remove_attrs,
    model_add_album,
)

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.DEBUG)

class IDDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def displayText(self, value, locale):
        return f'{value:04}'

class SizeHintDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sizeHint(self, option, index):
        return QSize(100, 20)

class PlornSizePolicy(QSizePolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalPolicy = QSizePolicy.Policy.Expanding
        self.verticalPolicy = QSizePolicy.Policy.Expanding

class PlornButtonSize(QSize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHeight(200)
        self.setWidth(500)

class PlornPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sizeHint = PlornButtonSize()
        self.setSizePolicy(PlornSizePolicy())
        self.flat = False

class PlornAttrView(QDialog):
    '''
    common widget class for displaying and editing attributes, one
    data model at a time
    '''
    def __init__(self, title=None, table='names',
                 db=None, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAttrView')
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
        tree.header().setSectionHidden(1, True)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.context_menu)
        tree.setToolTip('Right-click for actions')
        self.tree = tree
        layout.addWidget(self.tree, 0, 0)
        populate_attrs(root=self.root, table=self.table, db=self.db)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug('PlornAttrView all done')
 
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
    def __init__(self, db=None, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAlbumView')
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
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.context_menu)
        tree.setToolTip('Right-click for actions')
        self.tree = tree
        layout.addWidget(self.tree, 0, 0)

        tree.setHeaderHidden(False)
        tree.header().setSectionHidden(1, True)
        tree.header().resizeSection(0, 100)
        tree.header().resizeSection(1, 10)
        tree.header().resizeSection(2, 440)
        tree.header().resizeSection(3, 240)
        tree.header().resizeSection(4, 100)

        self.setLayout(layout)
        populate_albums(root=self.root, db=self.db)
        self.tree.expandAll()
        module_logger.debug('PlornAlbumView all done')
 
    def context_menu(self, position):
        global module_logger

        module_logger.debug(f'context_menu entered: album view')
        index = self.tree.indexAt(position)
        menu = QMenu()
        menu.setTitle('Actions')
        if not index.isValid():
            module_logger.debug('context_menu: assume invisible root')
            add_album_action = menu.addAction('Add Album',
                     lambda: self.add_album_sib(self.model.invisibleRootItem()))
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
        module_logger.debug(f'context_menu done: album view')

    def add_album(self, name, dated, notes):
        global module_logger

        module_logger.debug(f'add_album: entered "{name}" "{dated}"')
        album = PlornAlbum(name, id=None, dated=dated, notes=notes)
        root = self.model.invisibleRootItem()
        res = model_add_album(root, album, db=self.db)
        if res == 'cannot insert' or res == 'retrieve failed':
            title = 'Internal Attribute Database Failure'
            label_txt  = f'{res.capitalize()} "{name}"'
            button = QMessageBox.critical(self, title, label_txt)
            return
        module_logger.debug(f'add_album: done "{name}"')

    def add_album_action(self):
        global module_logger

        module_logger.debug(f'add_album_action: entered')
        new_album_dlg = PlornNewAlbumDialog()
        info = new_album_dlg.ask(self)
        self.add_album(info['album'], info['dated'], info['notes'])
        new_album_dlg.close()

    def add_album_sib(self, item):
        global module_logger

        module_logger.debug(f'add_album_sib entered: {self.table}')
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
            res = add_albums(self.model.invisibleRootItem(), parent, input_value,
                            table=self.table, db=self.db)
            if res == 'cannot insert' or res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()} "{input_value}"'
                button = QMessageBox.critical(self, title, label_txt)
                return
            if res == 'duplicate albumibute':
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
            module_logger.debug(f'add_album_sib {res}: {input_value}, {ptxt}')
        else:
            module_logger.debug(f'add_album_sib canceled: {input_value}, {ptxt}')

        module_logger.debug(f'add_album_sib done: {self.table}')

    def add_album_child(self, item):
        global module_logger

        module_logger.debug(f'add_album_child entered: {self.table}')
        title = f'Add Child {self.title.capitalize()}'
        if self.title[-1] == 's':    # English specific ...
            label_txt = f'Add {self.title[0:-1].capitalize()}:'
        msg  = f'add_album_child {self.table}:'
        msg += f' add child to {item.text()}'
        module_logger.debug(msg)
        label_txt = f'Add child to {item.text()}:'

        ptxt = 'invisibleRoot'
        if item and item != self.model.invisibleRootItem():
            ptxt = f' parent = {item.text()}'
        input_value, ok = QInputDialog.getText(self, title, label_txt)
        if ok and input_value:
            res = add_albums(self.model.invisibleRootItem(), item, input_value,
                            table=self.table, db=self.db)
            if res == 'cannot insert' or res == 'retrieve failed':
                title = 'Internal Attribute Database Failure'
                label_txt  = f'{res.capitalize()} "{input_value}"'
                button = QMessageBox.critical(self, title, label_txt)
                return
            if res == 'duplicate albumibute':
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
                f'add_album_child add {res}: {input_value}, {ptxt}')
        else:
            module_logger.debug(
                f'add_album_child canceled: {input_value}, {ptxt}')

        module_logger.debug(f'add_album_child done: {self.table}')

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


class PlornAttrListView(QWidget):
    '''
    widget class to be used for adding/removing attributes to
    an album or photo, best embedded as part of the album/photo view
    when adding or editing albums/photos
    '''
    ADD    = 42
    REMOVE = 99

    def __init__(self, table, title, allow_edit=True, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAttListView')
        self.table = table
        self.title = title
        self.allow_edit = allow_edit

        self.setWindowTitle(self.title)
        layout = QGridLayout()
        name_label = QLabel(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.name_list = QListView()
        model = QStandardItemModel()
        self.name_list.setModel(model)
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_list, 1, 0)

        blayout = QGridLayout()
        plus = QIcon.fromTheme(QIcon.ThemeIcon.ListAdd)
        self.add_attr = QPushButton(plus, None)
        blayout.addWidget(self.add_attr, 0, 0)
        minus = QIcon.fromTheme(QIcon.ThemeIcon.ListRemove)
        self.remove_attr = QPushButton(minus, None)
        blayout.addWidget(self.remove_attr, 1, 0)
        layout.addLayout(blayout, 1, 1)

        self.setLayout(layout)
        module_logger.debug('PlornAttListView done')


class PlornNewAlbumDialog(QDialog):
    @classmethod
    def ask(cls, parent):
        global module_logger

        dlg = cls(parent)
        result = None
        name = None
        datadir = None
        dbname = None
        res = dlg.exec()
        info = dlg.get_inputs()
        return info

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setModal(True)
        self.setWindowTitle('New Album')
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.catalog_label = QLabel(f'***Catalog: {catalog}***',
                                    textFormat=Qt.TextFormat.MarkdownText)
        layout.addWidget(self.catalog_label, 0, 0)

        album_layout = QGridLayout()
        self.name_label = QLabel('Album Name:',
                                 alignment=Qt.AlignmentFlag.AlignRight)
        album_layout.addWidget(self.name_label, 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setText(f'{" ":>40}')
        rect = self.name_edit.fontMetrics().boundingRect(self.name_edit.text())
        self.name_edit.setMinimumWidth(2*rect.width())
        self.name_edit.setText('')
        album_layout.addWidget(self.name_edit, 0, 1)

        self.dated_label = QLabel('Dated:',
                                  alignment=Qt.AlignmentFlag.AlignRight)
        album_layout.addWidget(self.dated_label, 1, 0)
        self.dated_edit = QLineEdit()
        self.dated_edit.setText(f'{" ":>40}')
        rect = self.dated_edit.fontMetrics().boundingRect(self.dated_edit.text())
        self.dated_edit.setMinimumWidth(2*rect.width())
        self.dated_edit.setText('')
        album_layout.addWidget(self.dated_edit, 1, 1)

        self.notes_label = QLabel('Notes:',
                                  alignment=Qt.AlignmentFlag.AlignRight)
        album_layout.addWidget(self.notes_label, 2, 0,
                         alignment=Qt.AlignmentFlag.AlignTop)
        self.notes_edit = QTextEdit()
        album_layout.addWidget(self.notes_edit, 2, 1)
        layout.addLayout(album_layout, 1, 0)

        attr_layout = QGridLayout()
        self.name_list = PlornAttrListView('names', 'Name Attributes')
        attr_layout.addWidget(self.name_list, 1, 0)
        self.place_list = PlornAttrListView('places', 'Place Attributes')
        attr_layout.addWidget(self.place_list, 2, 0)
        self.tag_list = PlornAttrListView('tags', 'Tag Attributes')
        attr_layout.addWidget(self.tag_list, 3, 0)
        layout.addLayout(attr_layout, 1, 1)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel
        )
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 2, 1, 1, 2)
        self.setLayout(layout)

    def check_inputs(self):
        global module_logger

        if len(self.name_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Album Name Error',
                        'A name must be provided.')
            return QDialog.DialogCode.Rejected
       
        module_logger.debug('check_inputs returns accepted')
        return QDialog.DialogCode.Accepted

    def get_inputs(self):
        global module_logger

        info = {}
        info['album'] = self.name_edit.text()
        info['dated'] = self.dated_edit.text()
        info['notes'] = self.notes_edit.toPlainText()
        module_logger.debug(f'get_inputs returns {info}')
        return info

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Ok:
            module_logger.debug('new cat: Ok clicked')
            if self.check_inputs() == QDialog.DialogCode.Rejected:
                return
            self.setResult(QDialog.DialogCode.Accepted)

        elif role == QDialogButtonBox.StandardButton.Cancel:
            module_logger.debug('new cat: Cancel clicked')
            self.setResult(QDialog.DialogCode.Rejected)

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


