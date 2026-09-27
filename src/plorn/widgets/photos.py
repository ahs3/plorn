
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os
#from PIL import Image as pilImage
#from PIL import ExifTags

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

import plorn
from plorn import (
    CatalogColumns,
    PlornAlbum,
    PlornPhoto,
)

from plorn.config import PlornConfig

from plorn.models.dbops import PlornDbOperations
from plorn.models.albums import PlornAlbumModel

from plorn.widgets.albums import PlornAlbumComboBox
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


class PlornImageDialog(QDialog):
    def __init__(self, id=0, name='', path='', *args, **kwargs):
        global module_logger

        super().__init__(*args, **kwargs)
        if len(path) < 1:
            return

        self.setWindowTitle(f'Showing [{id:04}] {name}')
        self.setModal(False)
        geometry = self.screen().availableGeometry()
        self.origin = QPoint(100, 100)
        self.size = QSize(int(geometry.width()*0.9), int(geometry.height()*0.9))
        self.rect = QRect(self.origin, self.size)
        self.setGeometry(self.rect)

        layout = QGridLayout()
        self.gview = QGraphicsView()
        layout.addWidget(self.gview, 0, 0)

        blayout = QGridLayout()
        self.full_screen = QPushButton('Maximize')
        self.full_screen.clicked.connect(lambda: self.bigger())
        blayout.addWidget(self.full_screen, 0, 1)
        self.doneb = QPushButton('Close')
        self.doneb.clicked.connect(lambda: self.close())
        blayout.addWidget(self.doneb, 0, 2)

        layout.addLayout(blayout, 1, 0)
        self.setLayout(layout)

        self.scene = QGraphicsScene()
        self.pixmap = QPixmap()
        fullpath = os.path.expandvars(os.path.expanduser(path))
        module_logger.debug(f'show_full_image: fullpath {fullpath}')
        self.pixmap.load(fullpath)
        smaller = QSize(int(self.size.width()*0.9), int(self.size.height()*0.9))
        module_logger.debug(f'show_full_image: smaller w,h {smaller.width()},{smaller.height()}')
        self.shrunk = self.pixmap.scaled(smaller,
                           aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                       transformMode=Qt.TransformationMode.SmoothTransformation)
        module_logger.debug(f'show_full_image: shrunk w,h {self.shrunk.rect().width()},{self.shrunk.rect().height()}')
        self.scene.setSceneRect(QRectF(self.shrunk.rect()))
        self.scene.addPixmap(self.shrunk)
        self.gview.setScene(self.scene)
        self.gview.show()

    def bigger(self):
        if self.full_screen.text() == 'Maximize':
            geometry = self.screen().availableGeometry()
            self.origin = QPoint(0, 0)
            self.size = QSize(geometry.width(), int(geometry.height()*0.95))
            self.rect = QRect(self.origin, self.size)
            self.setGeometry(self.rect)
            for ii in self.scene.items():
                self.scene.removeItem(ii)
            self.scene.addPixmap(self.pixmap)
            self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            self.full_screen.setText('Revert Size')
        else:
            geometry = self.screen().availableGeometry()
            self.origin = QPoint(100, 100)
            self.size = QSize(int(geometry.width()*0.9),
                              int(geometry.height()*0.9))
            self.rect = QRect(self.origin, self.size)
            self.setGeometry(self.rect)
            for ii in self.scene.items():
                self.scene.removeItem(ii)
            smaller = QSize(int(self.size.width()*0.9),
                            int(self.size.height()*0.9))
            self.shrunk = self.pixmap.scaled(smaller,
                           aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                       transformMode=Qt.TransformationMode.SmoothTransformation)
            self.scene.setSceneRect(QRectF(self.shrunk.rect()))
            self.scene.addPixmap(self.shrunk)
            self.full_screen.setText('Maximize')


class PlornPhotoDialog(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        if dlg.should_apply:
            return dlg.get_inputs()
        else:
            return {}

    def __init__(self, tree=None, title='Photo Dialog', allow_edit=True,
                 *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornPhotoDialog: init')
        self.setObjectName('plorn_photo_dialog')
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

        hdr_alignment = Qt.AlignmentFlag.AlignLeft | \
                        Qt.AlignmentFlag.AlignVCenter
        label_alignment = Qt.AlignmentFlag.AlignRight | \
                          Qt.AlignmentFlag.AlignVCenter

        album_grid = QGridLayout()
        if self.allow_edit:
            self.album_label = QLabel(f'Album:',
                                      textFormat=Qt.TextFormat.MarkdownText,
                                      alignment=hdr_alignment)
            self.album_selection = PlornAlbumComboBox()
            album_grid.addWidget(self.album_label, 0, 0)
            album_grid.addWidget(self.album_selection, 0, 1, 1, 5)
            
        else:
            metrics = self.catalog_label.fontMetrics()
            album_rect = metrics.boundingRect(f'{" ":>20}')
            self.album_id_label = QLabel(f'***Album ID:***',
                                         textFormat=Qt.TextFormat.MarkdownText,
                                         alignment=hdr_alignment)
            self.album_id_label.setMaximumWidth(2*album_rect.width())
            self.album_id = QLabel('',
                                   textFormat=Qt.TextFormat.MarkdownText,
                                   alignment=hdr_alignment)
            self.album_name_label = QLabel(f'***Album Name:***',
                                          textFormat=Qt.TextFormat.MarkdownText,
                                          alignment=hdr_alignment)
            self.album_name_label.setMaximumWidth(2*album_rect.width())
            self.album_name = QLabel('',
                                     textFormat=Qt.TextFormat.MarkdownText,
                                     alignment=hdr_alignment)
            album_grid.addWidget(self.album_id_label, 0, 0)
            album_grid.addWidget(self.album_id, 0, 1)
            album_grid.addWidget(self.album_name_label, 1, 0)
            album_grid.addWidget(self.album_name, 1, 1)
        layout.addLayout(album_grid, 1, 0, 1, 2)

        photo_layout = QGridLayout()
        if not self.allow_edit:
            self.id_label = QLabel('Photo ID:', alignment=label_alignment)
            photo_layout.addWidget(self.id_label, 0, 0)
            self.id_text = QLabel('', alignment=hdr_alignment)
            photo_layout.addWidget(self.id_text, 0, 1)
        self.name_label = QLabel('Name:', alignment=label_alignment)
        photo_layout.addWidget(self.name_label, 1, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setText(f'{" ":>40}')
        rect = self.name_edit.fontMetrics().boundingRect(self.name_edit.text())
        self.name_edit.setMinimumWidth(2*rect.width())
        self.name_edit.setText('')
        self.name_edit.setReadOnly(allow_edit)
        photo_layout.addWidget(self.name_edit, 1, 1)

        self.path_label = QLabel('Path:', alignment=label_alignment)
        photo_layout.addWidget(self.path_label, 2, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setText(f'{" ":>60}')
        rect = self.path_edit.fontMetrics().boundingRect(self.path_edit.text())
        self.path_edit.setMinimumWidth(2*rect.width())
        self.path_edit.setText('')
        self.path_edit.setReadOnly(allow_edit)
        photo_layout.addWidget(self.path_edit, 2, 1)
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.select_file)
        photo_layout.addWidget(self.browse_button, 2, 2)

        self.dated_label = QLabel('Dated:', alignment=label_alignment)
        photo_layout.addWidget(self.dated_label, 3, 0)
        self.dated_edit = QLineEdit()
        self.dated_edit.setText(f'{" ":>40}')
        metrics = self.dated_edit.fontMetrics()
        rect = metrics.boundingRect(self.dated_edit.text())
        self.dated_edit.setMinimumWidth(2*rect.width())
        self.dated_edit.setText('')
        self.dated_edit.setReadOnly(allow_edit)
        photo_layout.addWidget(self.dated_edit, 3, 1)

        self.notes_label = QLabel('<br><br><br><br>Notes:',
                                  alignment=label_alignment)
        photo_layout.addWidget(self.notes_label, 4, 0,
                         alignment=Qt.AlignmentFlag.AlignTop)
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(allow_edit)
        photo_layout.addWidget(self.notes_edit, 4, 1)
        layout.addLayout(photo_layout, 2, 0, 1, 2)

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
        layout.addWidget(self.bbox, 4, 3, 1, 2)

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
        layout.addLayout(attr_layout, 1, 2, 3, 2)

        image_layout = QGridLayout()
        self.gview = QGraphicsView()
        self.gview.setMinimumWidth(450)
        image_layout.addWidget(self.gview, 0, 0)
        self.scene = QGraphicsScene()
        self.show_image = QPushButton('Show Larger Image')
        self.show_image.clicked.connect(self.show_full_image)
        self.show_image.setEnabled(False)
        image_layout.addWidget(self.show_image, 1, 0)
        layout.addLayout(image_layout, 0, 4, 3, 1)

        self.setLayout(layout)
        module_logger.debug('PlornPhotoDialog: init done')

    def show_current_image(self):
        global module_logger

        module_logger.debug('show_current_image: entered')
        pixmap = QPixmap()
        path = self.path_edit.text()
        if len(path) < 1:
            return
        fullpath = os.path.expandvars(os.path.expanduser(path))
        pixmap.load(fullpath)
        shrunk = pixmap.scaled(QSize(400, 400),
                     aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                     transformMode=Qt.TransformationMode.SmoothTransformation)
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.scene.setSceneRect(QRectF(shrunk.rect()))
        self.scene.addPixmap(shrunk)
        self.gview.setScene(self.scene)
        self.gview.show()
        self.show_image.setEnabled(True)

    def show_full_image(self):
        global module_logger

        module_logger.debug('show_full_image: entered')
        if len(self.path_edit.text()) < 1:
            return
        module_logger.debug('show_full_image: open the dialog')
        dlg = PlornImageDialog(parent=self,
                               #id=self.id_text.text(),
                               name=self.name_edit.text(),
                               path=self.path_edit.text())
        dlg.show()

    def select_file(self):
        global module_logger

        config = PlornConfig()
        last_dir = config.get_last_directory_selected()
        dlg = QFileDialog(parent=self,
                          caption='Select Photo',
                          directory=last_dir,
                          filter='Images: (*.png *xpm, *jpg)')
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        dlg.setViewMode(QFileDialog.ViewMode.Detail)
        dlg.directoryEntered.connect(plorn.capture_last_directory)
        filename = None
        if dlg.exec():
            filenames = dlg.selectedFiles()
            if len(filenames) > 0:
                filename = filenames[0]
                module_logger.debug(f'select_file: {filename}')
                img = QImage(filename)
                if img.format == QImage.Format.Format_Invalid:
                    QMessageBox.critical(self, 'Image Format Error',
                                     'File chosen is not a valid image format.')
                    return None
                info = plorn.get_metadata(filename)
                self.path_edit.setText(filename)
                if self.name_edit.text() == '':
                    self.name_edit.setText(os.path.basename(filename))
                dated = self.dated_edit.text()
                notes = self.notes_edit.toPlainText()
                if len(dated) < 1:
                    if 'dated' in info.keys() and len(info['dated']) > 0:
                        dated = f'{info["dated"]}'.replace('Date and Time: ','')
                        self.dated_edit.setText(dated)
                if len(notes) > 0:
                    notes += '\n'
                if 'dated' in info.keys() and len(info['dated']) > 0:
                    notes += f'{info["dated"]}'
                if len(notes) > 0:
                    notes += '\n'
                if 'location' in info.keys() and len(info['location']) > 0:
                    notes += f'{info["location"]}'
                self.notes_edit.setPlainText(notes)
                self.show_current_image()
        return filename

    def check_inputs(self):
        global module_logger

        if self.allow_edit:
            if self.album_selection.get_selection() == None:
                QMessageBox.warning(self, 'Album Selection Error',
                            'An album must be selected.')
                self.should_apply = False
                return QDialog.DialogCode.Rejected

        if len(self.name_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Photo Name Error',
                        'A name must be provided.')
            self.should_apply = False
            return QDialog.DialogCode.Rejected
       
        module_logger.debug('check_inputs returns accepted')
        self.should_apply = True
        return QDialog.DialogCode.Accepted

    def set_album_info(self, album_id, album_name=' '):
        global module_logger

        msg = f'set_album_info: id "{album_id}", name "{album_name}"'
        module_logger.debug(msg)
        if int(album_id) < 0 or len(album_name) < 1:
            return
        if self.allow_edit:
            txt = f'[{album_id:04}]'
            index = self.album_selection.findText(txt,
                                            flags=Qt.MatchFlag.MatchContains)
            msg  = f'set_album_info: search for id "{txt}", '
            msg += f' found at index {index}'
            module_logger.debug(msg)
            if index >= 0:
                self.album_selection.setCurrentIndex(index)
        else:
            module_logger.debug(f'set_album_info: not editing')
            self.album_id.setText(f'{album_id:04}')
            self.album_name.setText(f'{album_name}')
        module_logger.debug(f'set_album_info: done')

    def get_inputs(self):
        global module_logger

        module_logger.debug('PlornPhotoDialog: get_inputs entered')
        info = {}
        info['apply'] = self.should_apply
        if self.allow_edit:
            info['album_id'] = self.album_selection.get_selection()
        else:
            info['album_id'] = self.album_id.text()
        info['photo'] = self.name_edit.text()
        info['path']  = self.path_edit.text()
        info['dated'] = self.dated_edit.text()
        info['notes'] = self.notes_edit.toPlainText()
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
    def __init__(self, tree=None, title='Photo Info', allow_edit=False,
                 *args, **kwargs):
        global module_logger
        super().__init__(tree=tree, title=title, allow_edit=allow_edit,
                         *args, **kwargs)

    def set_inputs(self, photo):
        global module_logger
        
        module_logger.debug('PlornViewPhotoDialog: entered set_inputs')
        self.album_id.setText(f'{photo.get_album_id():04}')
        album = PlornDbOperations.get_album_by_id(photo.get_album_id())
        self.album_name.setText(f'{album.get_name()}')
        self.id_text.setText(f'{photo.get_id():04}')
        self.name_edit.setText(photo.get_name())
        self.path_edit.setText(photo.get_path())
        self.dated_edit.setText(photo.get_dated())
        self.notes_edit.setPlainText(photo.get_notes())
        for name in photo.get_name_list():
            id = name.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='names', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewPhotoDialog: name {id} {value}')
            item = QStandardItem(value)
            item.setData([id, name.get_parent_id(), value])
            self.name_list.appendRow(item)
        for place in photo.get_place_list():
            id = place.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='places', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewPhotoDialog: place {id} {value}')
            item = QStandardItem(value)
            item.setData([id, place.get_parent_id(), value])
            self.place_list.appendRow(item)
        for tag in photo.get_tag_list():
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
            self.path_edit.setReadOnly(True)
            self.dated_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)

        pixmap = QPixmap()
        fullpath = os.path.expandvars(os.path.expanduser(photo.get_path()))
        pixmap.load(fullpath)
        shrunk = pixmap.scaled(QSize(400, 400),
                     aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                     transformMode=Qt.TransformationMode.SmoothTransformation)
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.scene.setSceneRect(QRectF(shrunk.rect()))
        self.scene.addPixmap(shrunk)
        self.gview.setScene(self.scene)
        self.gview.show()
        self.show_image.setEnabled(True)

        module_logger.debug('PlornViewPhotoDialog: set_inputs done')

