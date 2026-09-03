
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
from enum import IntEnum
import logging
import os

from PyQt6.QtCore import (
    QSize,
    Qt,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlRelationalDelegate,
)

from PyQt6.QtGui import (
    QFont,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtWidgets import (
    QAbstractItemView,
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
    PlornAttr,
)

from plorn.config import PlornConfig

from plorn.model import (
    PlornAlbumModel,
    PlornAttrModel,
    PlornDbOperations,
)

module_logger = logging.getLogger('plorn.widgets.attrs')
module_logger.setLevel(logging.DEBUG)


########################################################################
#
#   widgets/views specific to manipulating attributes
#
class PlornAttrSelection(QDialog):
    def __init__(self, table='names', db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug(f'entering PlornAttrSelection: table {table}')
        self.table = table
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        self.setWindowTitle(f'Select {self.table.capitalize()}')
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        model = QStandardItemModel()
        self.tree.setModel(model)
        layout.addWidget(self.tree, 0, 0)

        root = self.tree.model().invisibleRootItem()
        PlornAttrModel.populate_attrs(root, self.table, db=self.db)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.addButton('Apply', QDialogButtonBox.ButtonRole.ApplyRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug(f'PlornAttrSelection done: table {table}')

    def get_inputs(self):
        global module_logger

        module_logger.debug(f'{self.table} selection: get_inputs entered')
        res = self.exec()
        result = self.info
        msg  = f'{self.table} selection: get_inputs returns '
        msg += f'{len(self.info)} items'
        module_logger.debug(msg)
        return result

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.ApplyRole:
            module_logger.debug(f'{self.table} selection: Apply clicked')
            msg  = f'dlg_done: {len(self.tree.selectedIndexes())} '
            msg += f'from {self.table}'
            module_logger.debug(msg)
            for index in self.tree.selectedIndexes():
                item = self.tree.model().itemFromIndex(index)
                msg = f'dlg_done: selected {item.text()} from {self.table}'
                module_logger.debug(msg)
                self.info[item.text()] = item
            self.setResult(QDialog.DialogCode.Accepted)

        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'{self.table} selected: Done clicked')
            self.setResult(QDialog.DialogCode.Rejected)

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()

class PlornAttrListView(QWidget):
    '''
    widget class to be used for adding/removing attributes to
    an album or photo, best embedded as part of the album/photo view
    when adding or editing albums/photos
    '''
    def __init__(self, table, title, allow_edit=True, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAttListView')
        self.table = table
        self.title = title
        self.allow_edit = allow_edit
        
        self.setWindowTitle(self.title)
        layout = QGridLayout()
        attr_label = QLabel(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.attr_list = QListView()
        self.attr_list.setAlternatingRowColors(True)
        model = QStandardItemModel()
        self.attr_list.setModel(model)
        layout.addWidget(attr_label, 0, 0)
        layout.addWidget(self.attr_list, 1, 0)

        self.add_attr = None
        self.remove_attr = None
        if self.allow_edit:
            blayout = QGridLayout()
            plus = QIcon.fromTheme(QIcon.ThemeIcon.ListAdd)
            self.add_attr = QPushButton(plus, None)
            self.add_attr.setDefault(False)
            self.add_attr.clicked.connect(self.add_selected)
            blayout.addWidget(self.add_attr, 0, 0)
            minus = QIcon.fromTheme(QIcon.ThemeIcon.ListRemove)
            self.remove_attr = QPushButton(minus, None)
            self.remove_attr.setDefault(False)
            self.remove_attr.clicked.connect(self.remove_selected)
            blayout.addWidget(self.remove_attr, 1, 0)
            layout.addLayout(blayout, 1, 1)

        self.setLayout(layout)
        module_logger.debug('PlornAttListView done')

    def add_selected(self):
        global module_logger

        module_logger.debug('add_selected: entered')
        dlg = PlornAttrSelection(table=self.table)
        info = dlg.get_inputs()
        for value in info.keys():
            if info[value] != None:
                msg  = f'add_selected: data {info[value].data()}'
                module_logger.debug(msg)
                data = info[value].data()
                fullattr = PlornDbOperations.get_full_attr(table=self.table,
                                                         id=data[AttrFields.ID])
                module_logger.debug(f'add_selected: full attr {fullattr}')
                value = ', '.join(fullattr)
                item = QStandardItem(value)
                item.setData(data)
                item.setEditable(False)
                if len(self.attr_list.model().findItems(value)) < 1:
                    self.attr_list.model().appendRow(item)
        module_logger.debug(f'add_selected: info count {len(info)}')

    def appendRow(self, item):
        self.attr_list.model().appendRow(item)

    def rowCount(self):
        return self.attr_list.model().rowCount()

    def remove_selected(self):
        global module_logger

        module_logger.debug('remove_selected: entered')
        for index in self.attr_list.selectedIndexes():
            self.attr_list.model().removeRow(index.row())
        module_logger.debug('remove_selected: entered')

    def get_items(self):
        global module_logger

        module_logger.debug('get_items: entered')
        res = []
        model = self.attr_list.model()
        for ii in range(model.rowCount()):
            item = model.item(ii)
            dbrow = item.data()
            attr = PlornAttr(dbrow[AttrFields.VALUE],
                             id=dbrow[AttrFields.ID],
                             parent_id=dbrow[AttrFields.PARENT_ID],
                             table_name=self.table)
            res.append(attr)
        module_logger.debug(f'get_items: res {str(res)}')
        return res

