
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
    pyqtSignal,
    QPoint,
    QRect,
    QRectF,
    QSize,
    Qt,
)

from PyQt6.QtGui import (
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
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
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

import plorn
from plorn import (
    CatalogColumns,
    PlornAlbum,
    PlornPhoto,
)

from plorn.config import PlornConfig

from plorn.models.dbops import PlornDbOperations
from plorn.models.albums import PlornAlbumModel

from plorn.widgets.attrs import PlornAttrListView

module_logger = logging.getLogger('plorn.widgets.albums')
module_logger.setLevel(logging.DEBUG)


#######################################################################
#
#   widgets/views specific to manipulating albums and their contents
#
class PlornAlbumComboBox(QComboBox):
    albumSelected = pyqtSignal(int, name='albumSelected')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDuplicatesEnabled(False)
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.album_ids = {}
        self.addItem('')
        album_list = PlornAlbumModel.album_list()
        for album_id, album_name in album_list:
            album_str = f'[{album_id:04}] {album_name}'
            self.album_ids[album_str] = album_id
            self.addItem(album_str)
        self.selected_album = -1
        self.currentIndexChanged.connect(self.selection_made)
 
    def selection_made(self, index):
        global module_logger

        if index < 0:
            return
        self.selected_album = index
        self.albumSelected.emit(0)
        module_logger.debug(f'selection_made: {self.itemText(index)}')

    def get_selection(self):
        album_id = None
        if int(self.selected_album) > 0:
            album_id = self.album_ids[self.itemText(self.selected_album)]
        return album_id


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


class PlornAlbumDialog(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        if dlg.should_apply:
            return dlg.get_inputs()
        else:
            return {}

    def __init__(self, tree=None, title='Album Dialog', allow_edit=True,
                 select_album=False, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAlbumDialog: init')
        self.setObjectName('plorn_album_dialog')
        if tree == None:
            return
        self.tree = tree
        self.allow_edit = allow_edit
        self.select_album = select_album
        self.should_apply = False           # only true if check_inputs okay

        module_logger.debug('PlornAlbumDialog: started')
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

        hdr_alignment = Qt.AlignmentFlag.AlignLeft | \
                        Qt.AlignmentFlag.AlignVCenter
        label_alignment = Qt.AlignmentFlag.AlignRight | \
                          Qt.AlignmentFlag.AlignVCenter
        metrics = self.catalog_label.fontMetrics()
        rect = metrics.boundingRect(f'{" ":>40}')
        width = 2 * rect.width()

        album_layout = QGridLayout()
        self.id_label = QLabel('Album ID:', alignment=label_alignment)
        album_layout.addWidget(self.id_label, 0, 0)
        self.id_text = QLabel('', alignment=hdr_alignment)
        self.id_text.setMinimumWidth(width)
        album_layout.addWidget(self.id_text, 0, 1)

        self.select_label = QLabel('Album:', alignment=label_alignment)
        album_layout.addWidget(self.select_label, 1, 0)
        self.album_selection = PlornAlbumComboBox()
        self.album_selection.albumSelected.connect(self.set_inputs)
        self.album_selection.setMinimumWidth(width)
        album_layout.addWidget(self.album_selection, 1, 1)
        self.album = None

        self.name_label = QLabel('Album Name:', alignment=label_alignment)
        album_layout.addWidget(self.name_label, 2, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(width)
        album_layout.addWidget(self.name_edit, 2, 1)

        if self.allow_edit:
            self.id_label.setHidden(True)
            self.id_text.setHidden(True)

        if self.select_album:
            self.id_label.setHidden(True)
            self.id_text.setHidden(True)
            self.name_label.setHidden(True)
            self.name_edit.setHidden(True)
        else:
            self.select_label.setHidden(True)
            self.album_selection.setHidden(True)

        layout.addLayout(album_layout, 1, 0)

        info_layout = QGridLayout()
        self.dated_label = QLabel('Dated:', alignment=label_alignment)
        info_layout.addWidget(self.dated_label, 0, 0)
        self.dated_edit = QLineEdit()
        self.dated_edit.setMinimumWidth(width)
        info_layout.addWidget(self.dated_edit, 0, 1)

        self.notes_label = QLabel('<br><br><br><br>Notes:',
                                  alignment=label_alignment)
        info_layout.addWidget(self.notes_label, 1, 0)
        self.notes_edit = QTextEdit()
        metrics = self.id_label.fontMetrics()
        self.notes_edit.setMaximumWidth(width)
        info_layout.addWidget(self.notes_edit, 1, 1)
        layout.addLayout(info_layout, 2, 0)

        if not self.allow_edit:
            count_layout = QGridLayout()
            count_label = QLabel('Photo Count:', alignment=label_alignment)
            count_layout.addWidget(count_label, 0, 0)
            count = QLineEdit()
            count.setReadOnly(True)
            count_layout.addWidget(count, 0, 1)
            layout.addLayout(count_layout, 8, 0)
            if not hasattr(self, 'count_label'):
                setattr(self, 'count_label', count_label)
            if not hasattr(self, 'count'):
                setattr(self, 'count', count)

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
        layout.addWidget(self.bbox, 9, 2, 1, 2)

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
        layout.addLayout(attr_layout, 1, 2, 8, 1)

        self.setLayout(layout)
        module_logger.debug('PlornAlbumDialog: init done')

    def check_inputs(self):
        global module_logger

        if self.select_album and self.album_selection.get_selection() == None:
            QMessageBox.warning(self, 'Album Error',
                        'A album must be selected.')
            self.should_apply = False
            return QDialog.DialogCode.Rejected

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

        module_logger.debug('PlornAlbumDialog: get_inputs entered')
        info = {}
        info['apply'] = self.should_apply
        if self.select_album:
            info['id'] = self.album_selection.get_selection()
        else:
            info['id'] = int(self.id_text.text())
        info['album'] = self.name_edit.text()
        info['dated'] = self.dated_edit.text()
        info['notes'] = self.notes_edit.toPlainText()
        info['count'] = 0
        if not self.allow_edit:
            info['count'] = self.count.text()
        info['names'] = self.name_list.get_items()
        info['places'] = self.place_list.get_items()
        info['tags'] = self.tag_list.get_items()
        module_logger.debug(f'PlornAlbumDialog: get_inputs returns {info}')
        return info

    def set_inputs(self, album_id=-1):
        global module_logger
        
        module_logger.debug('PlornViewAlbumDialog: entered set_inputs')
        if album_id < 0 and (not self.select_album):
            return

        if self.select_album:
            album_id = self.album_selection.get_selection()

        album = PlornDbOperations.get_album_by_id(album_id)
        self.album = album
        self.id_text.setText(f'{album.get_id():04}')
        self.name_edit.setText(album.get_name())
        self.dated_edit.setText(album.get_dated())
        self.notes_edit.setPlainText(album.get_notes())
        if hasattr(self, 'count_label'):
            self.count.setText(str(album.get_photo_count()))
            self.count.setReadOnly(True)

        for name in album.get_name_list():
            id = name.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='names', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: name {id} {value}')
            item = QStandardItem(value)
            item.setData([id, name.get_parent_id(), value])
            self.name_list.appendRow(item)
        for place in album.get_place_list():
            id = place.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='places', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: place {id} {value}')
            item = QStandardItem(value)
            item.setData([id, place.get_parent_id(), value])
            self.place_list.appendRow(item)
        for tag in album.get_tag_list():
            id = int(tag.get_id())
            fullattr = PlornDbOperations.get_full_attr(table='tags', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: tag {str(tag)}')
            module_logger.debug(f'PlornViewAlbumDialog: tag {id} {value}')
            item = QStandardItem(value)
            item.setData([id, tag.get_parent_id(), value])
            self.tag_list.appendRow(item)

        if not self.allow_edit:
            if not self.select_album:
                self.name_edit.setReadOnly(True)
            self.dated_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
        module_logger.debug('PlornViewAlbumDialog: set_inputs done')

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


#class PlornViewAlbumDialog(PlornAlbumDialog):
#    def __init__(self, tree=None, title='Album Info', allow_edit=False,
#                 *args, **kwargs):
#        global module_logger
#        super().__init__(tree=tree, title=title, allow_edit=allow_edit,
#                         *args, **kwargs)
#
#    def set_inputs(self, album):
#        global module_logger
#        
#        module_logger.debug('PlornViewAlbumDialog: entered set_inputs')
#        self.id_text.setText(f'{album.get_id():04}')
#        self.name_edit.setText(album.get_name())
#        self.dated_edit.setText(album.get_dated())
#        self.notes_edit.setPlainText(album.get_notes())
#        if hasattr(self, 'count_label'):
#            self.count.setText(str(album.get_photo_count()))
#        for name in album.get_name_list():
#            id = name.get_id()
#            fullattr = PlornDbOperations.get_full_attr(table='names', id=id)
#            value = ', '.join(fullattr)
#            module_logger.debug(f'PlornViewAlbumDialog: name {id} {value}')
#            item = QStandardItem(value)
#            item.setData([id, name.get_parent_id(), value])
#            self.name_list.appendRow(item)
#        for place in album.get_place_list():
#            id = place.get_id()
#            fullattr = PlornDbOperations.get_full_attr(table='places', id=id)
#            value = ', '.join(fullattr)
#            module_logger.debug(f'PlornViewAlbumDialog: place {id} {value}')
#            item = QStandardItem(value)
#            item.setData([id, place.get_parent_id(), value])
#            self.place_list.appendRow(item)
#        for tag in album.get_tag_list():
#            id = int(tag.get_id())
#            fullattr = PlornDbOperations.get_full_attr(table='tags', id=id)
#            value = ', '.join(fullattr)
#            module_logger.debug(f'PlornViewAlbumDialog: tag {str(tag)}')
#            module_logger.debug(f'PlornViewAlbumDialog: tag {id} {value}')
#            item = QStandardItem(value)
#            item.setData([id, tag.get_parent_id(), value])
#            self.tag_list.appendRow(item)
#
#        if not self.allow_edit:
#            self.name_edit.setReadOnly(True)
#            self.dated_edit.setReadOnly(True)
#            self.notes_edit.setReadOnly(True)
#        self.count.setReadOnly(True)
#        module_logger.debug('PlornViewAlbumDialog: set_inputs done')


class PlornTableView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyReleaseEvent(self, event):
        global module_logger

        if event.key() == Qt.Key.Key_Up:
            module_logger.debug(f'keyPressEvent: "UP"')
            index = self.currentIndex()
            if index.row() > 0:
                up = self.photos.model().index(index.row()-1, index.column())
                self.setCurrentIndex(up)
        elif event.key() == Qt.Key.Key_Down:
            module_logger.debug(f'keyPressEvent: "DOWN"')
            index = self.currentIndex()
            if index.row() < self.photos.rowCount()-1:
                down = self.photos.model().index(index.row()-1, index.column())
                self.setCurrentIndex(down)
        else:
            super().keyReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        global module_logger

        module_logger.debug(f'mousePressEvent: "{str(event)}"')
        super().mouseReleaseEvent(event)


class PlornAlbumPhotosView(QDialog):
    @classmethod
    def ask(cls, dlg):
        global module_logger

        module_logger.debug(f'PlornAlbumPhotosView: ask, dlg {str(dlg)}')
        return dlg.exec()

    def build_item(self, value):
        item = QStandardItem(value)
        item.setSelectable(True)
        item.setEditable(False)
        return item

    def __init__(self, album_tree=None, select_album=False, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('PlornAlbumPhotosView: entering')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.album_tree = album_tree
        self.select_album = select_album

        self.album = None
        self.album_id = -1

        #if album_id != -1:
        #    self.album_id = album_id
        #    self.album = PlornDbOperations.get_album_by_id(int(album_id))
        #    module_logger.debug('PlornAlbumPhotosView: found album')
        #self.album_name = ''
        #if album_name != '':
        #    self.album_name = album_name

        self.setModal(True)
        self.setWindowTitle(f'Manage Photos in an Album')
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        origin = QPoint(200, 200)
        actual_origin = self.mapFromParent(origin)
        if origin == actual_origin:
            origin = QPoint(300, 300)
        size = QSize(1100, 600)
        self.setGeometry(QRect(origin, size))

        font = QFont()
        font.setBold(True)
        label_alignment = Qt.AlignmentFlag.AlignRight | \
                          Qt.AlignmentFlag.AlignVCenter
        data_alignment = Qt.AlignmentFlag.AlignLeft | \
                         Qt.AlignmentFlag.AlignVCenter

        album_layout = QGridLayout()
        if self.select_album:
            lab1 = QLabel('Album:', alignment=label_alignment)
            lab1.setMaximumWidth(150)
            lab1.setFont(font)
            album_layout.addWidget(lab1, 0, 0)

            self.album_selection = PlornAlbumComboBox()
            rect = lab1.fontMetrics().boundingRect(f'{" ":>40}')
            self.album_selection.setMinimumWidth(rect.width())
            self.album_selection.albumSelected.connect(self.set_album_id)
            album_layout.addWidget(self.album_selection, 0, 1)

        else:
            lab1 = QLabel('Album ID:', alignment=label_alignment)
            lab1.setMaximumWidth(150)
            lab1.setFont(font)
            album_layout.addWidget(lab1, 0, 0)
            self.album_id_label = QLabel('', alignment=data_alignment)
            self.album_id_label.setMaximumWidth(150)
            album_layout.addWidget(self.album_id_label, 0, 1)
            lab3 = QLabel('Name:', alignment=label_alignment)
            lab3.setMaximumWidth(150)
            lab3.setFont(font)
            album_layout.addWidget(lab3, 0, 2)
            self.album_name_label = QLabel('', alignment=data_alignment)
            self.album_name_label.setMaximumWidth(300)
            album_layout.addWidget(self.album_name_label, 0, 3)

        layout.addLayout(album_layout, 0, 0)

        self.photos = QTableView()
        self.photos.setSelectionMode(
                            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.photos.setSelectionBehavior(
                            QAbstractItemView.SelectionBehavior.SelectRows)
        model = QStandardItemModel()
        self.photos.setModel(model)
        hdr_id = QStandardItem('ID')
        hdr_id.setFont(font)
        hdr_name = QStandardItem('Photo Name')
        hdr_name.setFont(font)
        hdr_dated = QStandardItem('Dated')
        hdr_dated.setFont(font)
        hdr_path = QStandardItem('Path')
        hdr_path.setFont(font)
        self.photos.model().setHorizontalHeaderItem(0, hdr_id)
        self.photos.model().setHorizontalHeaderItem(1, hdr_name)
        self.photos.model().setHorizontalHeaderItem(2, hdr_dated)
        self.photos.model().setHorizontalHeaderItem(3, hdr_path)
        self.photos.setAlternatingRowColors(True)
        self.photos.verticalHeader().setVisible(False)
        self.photos.setShowGrid(True)
        self.photos.setColumnWidth(0, 100)
        self.photos.setColumnWidth(1, 300)
        self.photos.setColumnWidth(2, 200)
        self.photos.setColumnWidth(3, 800)
        self.photos.clicked.connect(self.show_current_image)
        self.photos.setMouseTracking(True)
        self.photos.entered.connect(self.show_current_image)
        layout.addWidget(self.photos, 1, 0)
        layout.setColumnStretch(0, 1)

        self.current_image = QGraphicsView(self)
        self.show_current_image()
        layout.addWidget(self.current_image, 1, 1)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_photos)
        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.remove_photos)
        self.done_button = QPushButton('Done')
        self.done_button.clicked.connect(self.dlg_done)
        self.done_button.setDefault(True)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.done_button)
        layout.addLayout(button_layout, 2, 1)

        self.setLayout(layout)
        module_logger.debug('PlornAlbumPhotosView: done')

    def set_album_id(self, id):
        if self.select_album:
            self.album_id = self.album_selection.get_selection()
        elif id != self.album_id:
            self.album_id = id
            album = PlornDbOperations.get_album_by_id(self.album_id)
            self.album_id_label.setText(f'{self.album_id:04}')
            self.album_name_label.setText(f'{album.get_name()}')
        self.set_photo_list(id)

    def set_photo_list(self, id):
        self.photos.model().removeRows(0, self.photos.model().rowCount())
        if self.current_image.scene():
            for item in self.current_image.scene().items():
                self.current_image.scene().removeItem(item)
        photo_list = PlornAlbumModel.photo_list(self.album_id)
        for photo_id, photo_name, photo_dated, photo_path in photo_list:
            msg  = 'PlornAlbumPhotosView: row '
            msg += f'[{photo_id}, {photo_name}, {photo_dated}, {photo_path}'
            module_logger.debug(msg)
            id_item = self.build_item(f'{photo_id:04}')
            name_item = self.build_item(photo_name)
            dated_item = self.build_item(photo_dated)
            path_item = self.build_item(photo_path)
            row = [id_item, name_item, dated_item, path_item]
            self.photos.model().appendRow(row)
        index = self.photos.model().index(0, 0)

    def update_current_image(self, selected, deselected):
        global module_logger

        module_logger.debug('update_current_image: entered')
        module_logger.debug(f'update_current_image: {len(selected)}, {len(deselected)}')

    def show_current_image(self, index=None):
        global module_logger

        module_logger.debug('show_current_image: entered')
        path = ''
        if index:
            item = self.photos.model().itemFromIndex(index)
            row = item.row()
            self.photos.selectRow(row)
            column = 3
            path_index = self.photos.model().index(row, column)
            path_item = self.photos.model().itemFromIndex(path_index)
            path = path_item.text()
            msg = f'show_current_image: row {row}, {path} selected'
            module_logger.debug(msg)
        else:
            indices = self.photos.selectedIndexes()
            if len(indices) < 1:
                return
            msg = f'show_current_image: {len(indices)} selections'
            module_logger.debug(msg)
            self.photos.selectRow(index[0].row())
            for index in indices:
                item = self.photos.model().itemFromIndex(index)
                if item.column() == 3:
                    path = item.text()
        scene = QGraphicsScene()
        pixmap = QPixmap()
        pixmap.load(os.path.expandvars(os.path.expanduser(path)))
        shrunk = pixmap.scaled(QSize(200, 200),
                     aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                     transformMode=Qt.TransformationMode.SmoothTransformation)
        scene.setSceneRect(QRectF(shrunk.rect()))
        scene.addPixmap(shrunk)
        self.current_image.setScene(scene)
        self.current_image.show()
        module_logger.debug('show_current_image: done')

    def get_file_names(self):
        global module_logger

        module_logger.debug('get_file_names: entered')
        config = PlornConfig()
        last_dir = config.get_last_directory_selected()

        filenames = []
        dlg = QFileDialog(parent=self,
                          caption='Select Photo File(s)',
                          directory=last_dir,
                          filter='Images: (*.png *.xpm *.jpg)')
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setViewMode(QFileDialog.ViewMode.Detail)
        dlg.directoryEntered.connect(plorn.capture_last_directory)
        if dlg.exec():
            filenames = dlg.selectedFiles()
        module_logger.debug(f'get_file_names: done {str(filenames)}')
        return filenames

    def add_photos(self):
        global module_logger

        module_logger.debug('add_photos: entered in dlg')
        filenames = self.get_file_names()
        for name in filenames:
            img = QImage(name)
            if img.format == QImage.Format.Format_Invalid:
                module_logger.debug(f'add_photos: {name} is not a valid image')
            else:
                info = plorn.get_metadata(name)
                msg = f'add_photos: {info}'
                created = ''
                if 'DateTime' in info:
                    created = info['DateTime']
                notes = ''
                if 'dated' in info:
                    notes += info['dated']
                if 'location' in info:
                    notes += f'\n{info["location"]}'
                photo = PlornPhoto(os.path.basename(name),
                                   id=None, album_id=self.album_id,
                                   dated=created, notes=notes,
                                   path=name)
                res = PlornAlbumModel.add_photo(
                            self.album_tree.model().invisibleRootItem(), photo)
                if res == 'okay':
                    photo = PlornDbOperations.get_photos_by_album_and_path( \
                                                self.album_id, name)
                    id_item = self.build_item(f'{photo.get_id():04}')
                    name_item = self.build_item(photo.get_name())
                    dated_item = self.build_item(photo.get_dated())
                    path_item = self.build_item(photo.get_path())
                    row = [id_item, name_item, dated_item, path_item]
                    self.photos.model().appendRow(row)
                module_logger.debug(msg)

        module_logger.debug('add_photos: done in dlg')

    def remove_photos(self):
        global module_logger

        module_logger.debug('widgets.remove_photos: entered in dlg')
        indices = self.photos.selectedIndexes()
        if len(indices) < 1:
            QMessageBox.warning(self, 'Photo Selection Error',
                        'One or more photos must be selected.')
            return

        ids_to_remove = {}
        for index in indices:
            item = self.photos.model().itemFromIndex(index)
            row = item.row()
            if row not in ids_to_remove:
                ids_to_remove[row] = [item]
            else:
                ids_to_remove[row].append(item)
        msg  = f'widgets.remove_photos: ids_to_remove '
        for key in ids_to_remove.keys():
            msg += f' {str(key)}'
        module_logger.debug(msg)
        for row, item_list in ids_to_remove.items():
            msg  = f'widgets.remove_photos: row {row}, cols'
            photo_id = 0
            photo_path = ''
            root = None
            for item in item_list:
                if item.column() == 0:
                    photo_id = int(item.text())
                    photo_parent = item.parent()
                    root = item.model().invisibleRootItem()
                elif item.column() == 3:
                    photo_path = item.text()
                msg += f' {item.column()}'
            module_logger.debug(msg)
            if photo_id != 0:
                module_logger.debug('widgets.remove_photos: remove from view')
                PlornAlbumModel.remove_photo( \
                        self.album_tree.model().invisibleRootItem(), photo_id)
                self.photos.model().removeRow(row)

        module_logger.debug('widgets.remove_photos: done in dlg')

    def dlg_done(self):
        global module_logger

        module_logger.debug('dlg_done: Done clicked')
        self.setResult(QDialog.DialogCode.Rejected)
        self.close()


