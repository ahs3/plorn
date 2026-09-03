
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
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlRelation,
    QSqlRelationalTableModel,
    QSqlTableModel,
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
    QTableView,
    QWidget,
)

from plorn import (
    AlbumFields,
    AttrFields,
    PhotoFields,
    PlornAlbum,
    PlornAttr,
)

from plorn.config import PlornConfig

from plorn.model import (
    PlornAlbumModel,
    PlornAttrModel,
    PlornDbOperations,
)

module_logger = logging.getLogger('plorn.widgets.raw')
module_logger.setLevel(logging.DEBUG)


########################################################################
#
#   models specific to showing db tables in raw-ish form
#
class PlornRawConfigModel(QSqlRelationalTableModel):
    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'raw config model init: {db.connectionName()}')
        self.setTable('config')
        res = self.select()
        module_logger.debug(f'raw config model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger
        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        if orientation == Qt.Orientation.Vertical:
            return

        section_text = ['Application', 'Version', 'User Name', 'Full Name']
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


class PlornRawAttrModel(QSqlRelationalTableModel):
    def __init__(self, table='names', parent=None, db=QSqlDatabase(),
                 *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'raw attr model init: {db.connectionName()}')
        self.table = table
        self.setTable(table)
        self.setRelation(1, QSqlRelation(self.table, 'id', 'value'))
        res = self.select()
        module_logger.debug(f'raw attr model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger
        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        if orientation == Qt.Orientation.Vertical:
            return

        objname = self.table[:-1].capitalize()
        section_text = ['ID', 'Parent', objname]
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


class PlornRawObjAttrModel(QSqlRelationalTableModel):
    def __init__(self, obj='album', attrs='names', parent=None,
                 db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'raw obj attr model init: {db.connectionName()}')
        self.object = obj
        self.attrs = attrs
        self.setTable(f'{obj}_{attrs}')
        self.setRelation(1, QSqlRelation('albums', 'id', 'name'))
        self.setRelation(2, QSqlRelation(attrs, 'id', 'value'))
        res = self.select()
        module_logger.debug(f'raw obj attr model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger
        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        if orientation == Qt.Orientation.Vertical:
            return

        section_text = ['ID',self.object.capitalize(),self.attrs.capitalize()]
        if role == Qt.ItemDataRole.DisplayRole:
            module_logger.debug(f'headerData: display {section}')
            return str(section_text[section])

        elif role == Qt.ItemDataRole.FontRole:
            return Qt.AlignmentFlag.AlignLeft


class PlornRawAlbumModel(QSqlRelationalTableModel):
    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'album model init: {db.connectionName()}')
        self.setTable('albums')
        res = self.select()
        module_logger.debug(f'album model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger
        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        if orientation == Qt.Orientation.Vertical:
            return

        section_text = ['ID', 'Album', 'Dated', 'Notes', 'Photo Count']
        if role == Qt.ItemDataRole.DisplayRole:
            module_logger.debug(f'headerData: display {section}')
            return str(section_text[section])

        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        elif section==AttrFields.ID and role==Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft

        elif section > AttrFields.ID:
            return Qt.AlignmentFlag.AlignLeft
        

class PlornRawPhotoModel(QSqlRelationalTableModel):
    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'photo model init: {db.connectionName()}')
        self.setTable('photos')
        self.setRelation(1, QSqlRelation('albums', 'id', 'name'))
        res = self.select()
        module_logger.debug(f'photo model init: select result {res}')

    def headerData(self, section, orientation,
                   role=Qt.ItemDataRole.DisplayRole):
        global module_logger
        super().headerData(section, orientation, role)
        module_logger.debug(f'headerData: {section, role}')

        if orientation == Qt.Orientation.Vertical:
            return

        section_text = ['ID', 'Album', 'Photo', 'Path', 'Dated', 'Notes']
        if role == Qt.ItemDataRole.DisplayRole:
            module_logger.debug(f'headerData: display {section}')
            return str(section_text[section])

        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        elif section==AttrFields.ID and role==Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft

        elif section > AttrFields.ID:
            return Qt.AlignmentFlag.AlignLeft
        

########################################################################
#
#   widgets/views specific to showing db tables in raw-ish form
#
class IDDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def displayText(self, value, locale):
        return f'{value:04}'


class PlornRawConfigView(QDialog):
    def __init__(self, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornRawConfigView')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        self.setWindowTitle(f'Raw Config Table')
        origin = QPoint(200, 200)
        self.origin = self.mapFromParent(origin)
        if origin == self.origin:
            self.origin = QPoint(300, 300)
        self.size = QSize(900, 150)
        self.setGeometry(QRect(self.origin, self.size))

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.table = QTableView()
        self.table.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        model = PlornRawConfigModel(db=self.db)
        self.table.setModel(model)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 350)
        layout.addWidget(self.table, 0, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug('PlornRawConfigView done')

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'dlg_done: Done clicked')

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


class PlornRawAttrView(QDialog):
    def __init__(self, table='names', db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug(f'entering PlornRawAttrView: table {table}')
        self.table_name = table
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        self.setWindowTitle(f'Raw {self.table_name.capitalize()} Table')
        origin = QPoint(200, 200)
        self.origin = self.mapFromParent(origin)
        if origin == self.origin:
            self.origin = QPoint(300, 300)
        self.size = QSize(600, 450)
        self.setGeometry(QRect(self.origin, self.size))

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.table = QTableView()
        self.table.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        model = PlornRawAttrModel(table=self.table_name, db=self.db)
        self.table.setModel(model)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setItemDelegateForColumn(AttrFields.ID, IDDelegate())
        self.table.setColumnWidth(AttrFields.PARENT_ID, 250)
        self.table.setColumnWidth(AttrFields.VALUE, 250)
        layout.addWidget(self.table, 0, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug(f'PlornRawAttrView done: table {table}')

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'{self.table} selected: Done clicked')

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


class PlornRawObjAttrView(QDialog):
    def __init__(self, obj='album', attrs='names', db=QSqlDatabase(),
                 *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        self.table_name = f'{obj}_{attrs}'
        msg = f'entering PlornRawObjAttrView: {self.table_name}'
        module_logger.debug(msg)
        self.object = obj
        self.attrs = attrs
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        title = f'Raw {obj.capitalize()} {attrs.capitalize()} Table'
        self.setWindowTitle(title)
        origin = QPoint(200, 200)
        self.origin = self.mapFromParent(origin)
        if origin == self.origin:
            self.origin = QPoint(300, 300)
        self.size = QSize(600, 450)
        self.setGeometry(QRect(self.origin, self.size))

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.table = QTableView()
        self.table.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        model = PlornRawObjAttrModel(obj=obj, attrs=attrs, db=self.db)
        self.table.setModel(model)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setItemDelegateForColumn(AttrFields.ID, IDDelegate())
        self.table.setColumnWidth(AttrFields.PARENT_ID, 250)
        self.table.setColumnWidth(AttrFields.VALUE, 250)
        layout.addWidget(self.table, 0, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug(f'PlornRawObjAttrView done: {self.table_name}')

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'{self.table} selected: Done clicked')

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


class PlornRawAlbumView(QDialog):
    def __init__(self, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornRawAlbumView')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        self.setWindowTitle(f'Raw Albums Table')
        origin = QPoint(200, 200)
        self.origin = self.mapFromParent(origin)
        if origin == self.origin:
            self.origin = QPoint(300, 300)
        self.size = QSize(990, 450)
        self.setGeometry(QRect(self.origin, self.size))

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.table = QTableView()
        self.table.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        model = PlornRawAlbumModel(db=self.db)
        self.table.setModel(model)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setItemDelegateForColumn(AlbumFields.ID, IDDelegate())
        self.table.setColumnWidth(AlbumFields.NAME, 250)
        self.table.setColumnWidth(AlbumFields.DATED, 150)
        self.table.setColumnWidth(AlbumFields.NOTES, 300)
        self.table.setColumnWidth(AlbumFields.PHOTO_COUNT, 150)
        layout.addWidget(self.table, 0, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug('PlornRawAlbumView done')

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'{self.table} selected: Done clicked')

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


class PlornRawPhotoView(QDialog):
    def __init__(self, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornRawPhotoView')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.info = {}

        self.setModal(True)
        self.setWindowTitle(f'Raw Photos Table')
        origin = QPoint(200, 200)
        self.origin = self.mapFromParent(origin)
        if origin == self.origin:
            self.origin = QPoint(300, 300)
        self.size = QSize(990, 450)
        self.setGeometry(QRect(self.origin, self.size))

        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.table = QTableView()
        self.table.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setWordWrap(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        model = PlornRawPhotoModel(db=self.db)
        self.table.setModel(model)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setItemDelegateForColumn(PhotoFields.ID, IDDelegate())
        self.table.setColumnWidth(PhotoFields.ALBUM_ID, 250)
        self.table.setColumnWidth(PhotoFields.NAME, 250)
        self.table.setColumnWidth(PhotoFields.PATH, 600)
        self.table.setColumnWidth(PhotoFields.DATED, 250)
        self.table.setColumnWidth(PhotoFields.NOTES, 600)
        layout.addWidget(self.table, 0, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug('PlornRawPhotoView done')

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug(f'{self.table} selected: Done clicked')

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


