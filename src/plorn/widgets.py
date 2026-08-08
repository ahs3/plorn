
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging

from PyQt6.QtCore import (
    QSize,
    Qt,
)

from PyQt6.QtSql import (
    QSqlRelationalDelegate,
)

from PyQt6.QtGui import (
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTreeView,
    QWidget,
)

from plorn.config import PlornConfig
from plorn.db import AttrFields
from plorn.model import populate_attrs, add_attrs

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
                           lambda: self.add_attr_sib(self.invisibleRootItem()))
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
        msg  = f'remove_attr {self.table}:'
        msg += f' add child to {item.text()}'
        module_logger.debug(msg)
        label_txt = f'Remove "{item.text()}"'
        if item.hasChildren():
            label_txt += ' and children'
        label_txt += '?'
        button = QMessageBox.question(self, title, label_txt)
        if button == QMessageBox.StandardButton.Yes:
            response = 'Yes'
        else:
            response = 'No'
        module_logger.debug(f'remove_attr? {response}')
        module_logger.debug(f'remove_attr done: {self.table}')

