
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os
from PIL import Image as pilImage
from PIL import ExifTags

from PyQt6.QtCore import (
    QPoint,
    QRect,
    QRectF,
    QSize,
    Qt,
)

from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QKeySequence,
    QPixmap,
    QStandardItem,
    QStandardItemModel,
)

from PyQt6.QtSql import (
    QSqlDatabase,
)

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableView,
    QTextEdit,
)

from plorn import (
    CatalogColumns,
    PlornAlbum,
    PlornPhoto,
)

from plorn.config import PlornConfig

from plorn.models.dbops import PlornDbOperations
from plorn.models.albums import PlornAlbumModel

from plorn.widgets.attrs import PlornAttrListView

module_logger = logging.getLogger('plorn.widgets.photos')
module_logger.setLevel(logging.DEBUG)


#######################################################################
#
#   widgets/views specific to manipulating photos and their contents
#
class PlornAlbumSelection(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        return dlg.get_inputs()

    def __init__(self, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('PlornAlbumSelection: entering')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()

        self.setModal(True)
        self.setWindowTitle(f'Select an Album')
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        origin = QPoint(200, 200)
        actual_origin = self.mapFromParent(origin)
        if origin == actual_origin:
            origin = QPoint(300, 300)
        size = QSize(525, 300)
        self.setGeometry(QRect(origin, size))

        self.albums = QTableView()
        self.albums.setSelectionMode(
                            QAbstractItemView.SelectionMode.SingleSelection)
        self.albums.setSelectionBehavior(
                            QAbstractItemView.SelectionBehavior.SelectRows)
        model = QStandardItemModel()
        self.albums.setModel(model)
        font = QFont()
        font.setBold(True)
        hdr_id = QStandardItem('ID')
        hdr_id.setFont(font)
        hdr_name = QStandardItem('Album Name')
        hdr_name.setFont(font)
        self.albums.model().setHorizontalHeaderItem(0, hdr_id)
        self.albums.model().setHorizontalHeaderItem(1, hdr_name)
        self.albums.setAlternatingRowColors(True)
        self.albums.verticalHeader().setVisible(False)
        self.albums.setShowGrid(True)
        self.albums.setColumnWidth(0, 100)
        self.albums.setColumnWidth(1, 400)
        layout.addWidget(self.albums, 0, 0)

        album_list = PlornAlbumModel.album_list()
        for album_id, album_name in album_list:
            id_item = QStandardItem(f'{album_id:04}')
            id_item.setSelectable(True)
            id_item.setEditable(False)
            name_item = QStandardItem(album_name)
            name_item.setSelectable(True)
            name_item.setEditable(False)
            self.albums.model().appendRow([id_item, name_item])

        self.bbox = QDialogButtonBox()
        self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.bbox.addButton('Apply', QDialogButtonBox.ButtonRole.ApplyRole)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 1, 0)
        self.setLayout(layout)
        module_logger.debug('PlornAlbumSelection: done')

    def get_inputs(self):
        global module_logger

        module_logger.debug('get_inputs: entered')
        info = {}
        for index in self.albums.selectedIndexes():
            item = self.albums.model().itemFromIndex(index)
            module_logger.debug(f'get_inputs: selected {item.text()}')
            if item.column() == 0:
                info['id'] = item.text()
            elif item.column() == 1:
                info['album'] = item.text()
        if len(info) > 0:
            info['apply'] = True
        else:
            info['apply'] = False
        module_logger.debug(f'get_inputs: returns {len(info)} items')
        return info

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.ApplyRole:
            module_logger.debug('dlg_done: Apply clicked')
            self.setResult(QDialog.DialogCode.Accepted)

        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug('dlg_done: Done clicked')
            self.setResult(QDialog.DialogCode.Rejected)

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


class PlornPhotoDialog(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        if dlg.should_apply:
            return dlg.get_inputs()
        else:
            return {}

    def __init__(self, tree=None, title='Album Dialog', allow_edit=True,
                 *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornPhotoDialog: init')
        self.setObjectName('plorn_album_dialog')
        if tree == None:
            return
        self.tree = tree
        self.allow_edit = allow_edit
        self.should_apply = False           # only true if check_inputs okay

        module_logger.debug('PlornPhotoDialog: started')
        self.setWindowTitle(title)
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.catalog_label = QLabel(f'***Catalog: {catalog}***',
                                    textFormat=Qt.TextFormat.MarkdownText)
        layout.addWidget(self.catalog_label, 0, 0)

        label_alignment = Qt.AlignmentFlag.AlignRight | \
                          Qt.AlignmentFlag.AlignVCenter
        album_layout = QGridLayout()
        self.name_label = QLabel('Album Name:', alignment=label_alignment)
        album_layout.addWidget(self.name_label, 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setText(f'{" ":>40}')
        rect = self.name_edit.fontMetrics().boundingRect(self.name_edit.text())
        self.name_edit.setMinimumWidth(2*rect.width())
        self.name_edit.setText('')
        album_layout.addWidget(self.name_edit, 0, 1)

        self.dated_label = QLabel('Dated:', alignment=label_alignment)
        album_layout.addWidget(self.dated_label, 1, 0)
        self.dated_edit = QLineEdit()
        self.dated_edit.setText(f'{" ":>40}')
        rect = self.dated_edit.fontMetrics().boundingRect(self.dated_edit.text())
        self.dated_edit.setMinimumWidth(2*rect.width())
        self.dated_edit.setText('')
        album_layout.addWidget(self.dated_edit, 1, 1)

        self.notes_label = QLabel('Notes:', alignment=label_alignment)
        album_layout.addWidget(self.notes_label, 2, 0,
                         alignment=Qt.AlignmentFlag.AlignTop)
        self.notes_edit = QTextEdit()
        album_layout.addWidget(self.notes_edit, 2, 1)
        layout.addLayout(album_layout, 1, 0)

        self.bbox = QDialogButtonBox()
        self.bbox.setObjectName('album_dlg_bbox')
        done=self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        self.done_button = done
        self.apply_button = None
        if self.allow_edit:
            doit=self.bbox.addButton('Apply',
                                     QDialogButtonBox.ButtonRole.ApplyRole)
            self.apply_button = doit
            self.apply_button.setObjectName('add_album_apply_button')
        self.done_button.setDefault(True)
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 2, 1, 1, 2)

        attr_layout = QGridLayout()
        self.name_list = PlornAttrListView('names', 'Name Attributes',
                                           allow_edit=allow_edit)
        attr_layout.addWidget(self.name_list, 1, 0)
        self.place_list = PlornAttrListView('places', 'Place Attributes',
                                            allow_edit=allow_edit)
        attr_layout.addWidget(self.place_list, 2, 0)
        self.tag_list = PlornAttrListView('tags', 'Tag Attributes',
                                          allow_edit=allow_edit)
        attr_layout.addWidget(self.tag_list, 3, 0)
        layout.addLayout(attr_layout, 1, 1)

        self.setLayout(layout)
        module_logger.debug('PlornPhotoDialog: init done')

    def check_inputs(self):
        global module_logger

        if len(self.name_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Album Name Error',
                        'A name must be provided.')
            self.should_apply = False
            return QDialog.DialogCode.Rejected
       
        module_logger.debug('check_inputs returns accepted')
        self.should_apply = True
        return QDialog.DialogCode.Accepted

    def get_inputs(self):
        global module_logger

        module_logger.debug('PlornPhotoDialog: get_inputs entered')
        info = {}
        info['apply'] = self.should_apply
        info['album'] = self.name_edit.text()
        info['dated'] = self.dated_edit.text()
        info['notes'] = self.notes_edit.toPlainText()
        info['count'] = 0
        if hasattr(self, 'count_label'):
            info['count'] = self.count.text()
        info['names'] = self.name_list.get_items()
        info['places'] = self.place_list.get_items()
        info['tags'] = self.tag_list.get_items()
        module_logger.debug(f'PlornPhotoDialog: get_inputs returns {info}')
        return info

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.ApplyRole:
            module_logger.debug('album dialog: Apply clicked')
            if self.check_inputs() == QDialog.DialogCode.Rejected:
                module_logger.debug('album dialog: Apply clicked, but rejected')
                self.setResult(QDialog.DialogCode.Rejected)
                self.should_apply = False
                return
            self.setResult(QDialog.DialogCode.Accepted)
            module_logger.debug('album dialog: Apply clicked, and accepted')

        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug('album dialog: Done clicked')
            self.setResult(QDialog.DialogCode.Rejected)
            self.should_apply = False
            module_logger.debug('album dialog: Done clicked, and rejected')

        module_logger.debug(f'dlg_done returns {self.should_apply}')
        self.close()


class PlornViewPhotoDialog(PlornPhotoDialog):
    def __init__(self, tree=None, title='Album Info', allow_edit=False,
                 *args, **kwargs):
        global module_logger
        super().__init__(tree=tree, title=title, allow_edit=allow_edit,
                         *args, **kwargs)

    def set_inputs(self, album):
        global module_logger
        
        module_logger.debug('PlornViewPhotoDialog: entered set_inputs')
        self.name_edit.setText(album.get_name())
        self.dated_edit.setText(album.get_dated())
        self.notes_edit.setPlainText(album.get_notes())
        if hasattr(self, 'count_label'):
            self.count.setText(str(album.get_photo_count()))
        for name in album.get_name_list():
            id = name.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='names', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewPhotoDialog: name {id} {value}')
            item = QStandardItem(value)
            item.setData([id, name.get_parent_id(), value])
            self.name_list.appendRow(item)
        for place in album.get_place_list():
            id = place.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='places', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewPhotoDialog: place {id} {value}')
            item = QStandardItem(value)
            item.setData([id, place.get_parent_id(), value])
            self.place_list.appendRow(item)
        for tag in album.get_tag_list():
            id = int(tag.get_id())
            fullattr = PlornDbOperations.get_full_attr(table='tags', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewPhotoDialog: tag {str(tag)}')
            module_logger.debug(f'PlornViewPhotoDialog: tag {id} {value}')
            item = QStandardItem(value)
            item.setData([id, tag.get_parent_id(), value])
            self.tag_list.appendRow(item)

        if not self.allow_edit:
            self.name_edit.setReadOnly(True)
            self.dated_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
        module_logger.debug('PlornViewPhotoDialog: set_inputs done')

