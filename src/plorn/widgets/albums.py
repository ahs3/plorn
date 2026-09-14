
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
    QSize,
    Qt,
)

from PyQt6.QtGui import (
    QFont,
    QImage,
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
    PlornAlbum,
    PlornPhoto,
)

from plorn.config import PlornConfig

from plorn.model import (
    PlornDbOperations,
    PlornAlbumModel,
)

from plorn.widgets.attrs import PlornAttrListView

module_logger = logging.getLogger('plorn.widgets.albums')
module_logger.setLevel(logging.DEBUG)


#######################################################################
#
#   widgets/views specific to manipulating albums and their contents
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


class PlornAlbumDialog(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        if dlg.should_apply:
            return dlg.get_inputs()
        else:
            return {}

    def __init__(self, tree=None, title='Album Dialog', allow_edit=True,
                 show_count=True, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAlbumDialog: init')
        self.setObjectName('plorn_album_dialog')
        if tree == None:
            return
        self.tree = tree
        self.allow_edit = allow_edit
        self.show_count = show_count
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

        grid_row = 2
        if show_count:
            count_layout = QGridLayout()
            count_label = QLabel('Photo Count:', alignment=label_alignment)
            count_layout.addWidget(count_label, 0, 0)
            count = QLineEdit()
            count.setReadOnly(True)
            count_layout.addWidget(count, 0, 1)
            layout.addLayout(count_layout, grid_row, 0)
            if not hasattr(self, 'count_label'):
                setattr(self, 'count_label', count_label)
            if not hasattr(self, 'count'):
                setattr(self, 'count', count)
            grid_row += 1

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
        layout.addWidget(self.bbox, grid_row, 1, 1, 2)

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
        module_logger.debug('PlornAlbumDialog: init done')

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

        module_logger.debug('PlornAlbumDialog: get_inputs entered')
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
        module_logger.debug(f'PlornAlbumDialog: get_inputs returns {info}')
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


class PlornViewAlbumDialog(PlornAlbumDialog):
    def __init__(self, tree=None, title='Album Info', allow_edit=False,
                 *args, **kwargs):
        global module_logger
        super().__init__(tree=tree, title=title, allow_edit=allow_edit,
                         *args, **kwargs)

    def set_inputs(self, album):
        global module_logger
        
        module_logger.debug('PlornViewAlbumDialog: entered set_inputs')
        self.name_edit.setText(album.get_name())
        self.dated_edit.setText(album.get_dated())
        self.notes_edit.setPlainText(album.get_notes())
        if hasattr(self, 'count_label'):
            self.count.setText(str(album.get_photo_count()))
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
            self.name_edit.setReadOnly(True)
            self.dated_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
        self.count.setReadOnly(True)
        module_logger.debug('PlornViewAlbumDialog: set_inputs done')


class PlornAlbumPhotosView(QDialog):
    @classmethod
    def ask(cls, dlg):
        dlg.exec()
        return dlg.get_inputs()

    def build_item(self, value):
        item = QStandardItem(value)
        item.setSelectable(True)
        item.setEditable(False)
        return item

    def __init__(self, album_tree, album_id, album_name, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('PlornAlbumPhotosView: entering')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.db = QSqlDatabase.database(catalog)
        self.db.open()
        self.album = PlornDbOperations.get_album_by_id(int(album_id))
        assert int(album_id) == int(self.album.get_id())
        module_logger.debug('PlornAlbumPhotosView: found album')
        self.album_id = album_id
        self.album_name = album_name
        self.album_tree = album_tree
        self.filenames = []

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
        lab1 = QLabel('Album ID:', alignment=label_alignment)
        lab1.setMaximumWidth(150)
        lab1.setFont(font)
        album_layout.addWidget(lab1, 0, 0)
        lab2 = QLabel(f'{self.album_id:04}', alignment=data_alignment)
        lab2.setMaximumWidth(150)
        album_layout.addWidget(lab2, 0, 1)
        lab3 = QLabel('Name:', alignment=label_alignment)
        lab3.setMaximumWidth(150)
        lab3.setFont(font)
        album_layout.addWidget(lab3, 0, 2)
        lab4 = QLabel(self.album_name, alignment=data_alignment)
        lab4.setMaximumWidth(300)
        album_layout.addWidget(lab4, 0, 3)
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
        layout.addWidget(self.photos, 1, 0)

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
        layout.addLayout(button_layout, 2, 0)

        self.setLayout(layout)
        module_logger.debug('PlornAlbumPhotosView: done')

    def get_inputs(self):
        global module_logger

        module_logger.debug('get_inputs: entered')
        #info = {}
        #for index in self.photos.selectedIndexes():
        #    item = self.photos.model().itemFromIndex(index)
        #    module_logger.debug(f'get_inputs: selected {item.text()}')
        #    if item.column() == 0:
        #        info['id'] = item.text()
        #    elif item.column() == 1:
        #        info['album'] = item.text()
        #if len(info) > 0:
        #    info['apply'] = True
        #    info['filenames'] = self.filenames
        #else:
        #    info['apply'] = False
        info = self.filenames
        module_logger.debug(f'get_inputs: returns {len(info)} items')
        return info

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
        dlg.directoryEntered.connect(self.capture_last_directory)
        if dlg.exec():
            filenames = dlg.selectedFiles()
        module_logger.debug(f'get_file_names: done {str(filenames)}')
        return filenames

    def capture_last_directory(self, directory):
        global module_logger

        module_logger.debug(f'capture_last_directory: dir {directory}')
        config = PlornConfig()
        config.set_last_directory_selected(directory)
        msg = f'capture_last_directory: {config.get_last_directory_selected()}'
        module_logger.debug(msg)

    def get_metadata(self, path):
        global module_logger
        '''
        Get EXIF metadata from the image if we can.  NB: we scarf up
        everything we can, just in case, but may not use it (that's
        what garbage collection is for ...?)
        '''
        module_logger.debug(f'get_metadata: entered for {path}')

        def format_dms(degrees, minutes, seconds, direction):
            degree_symbol = u'\N{DEGREE SIGN}'
            value  = float(degrees)
            value += float(float(minutes) / 60.0)
            value += float(float(seconds) / 3600.0)
            return f'{value:.6}{degree_symbol} {direction}'

        info = {}
        try:
            with pilImage.open(path) as img:
                info['format'] = f'Image Format: {img.format}'
                exif = img.getexif()
                for tag, value in exif.items():
                    text = ExifTags.TAGS[tag]
                    info[text] = value
                exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                for tag, value in exif_ifd.items():
                    text = ExifTags.TAGS[tag]
                    info[text] = value
                gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
                for tag, value in gps_ifd.items():
                    text = ExifTags.GPSTAGS[tag]
                    info[text] = value
            img.close()
        except (IOError, AttributeError, KeyError, IndexError) as e:
            return {}

        if 'DateTime' in info:
            dt = info['DateTime'].split()
            date = dt[0].replace(':', '-')
            tm = dt[1]
            dated = f'{date}  {tm}'
            msg = f'Date and Time: {date}  {tm}'
            if 'OffsetTime' in info:
                msg += f'{info["OffsetTime"]}'
            info['dated'] = msg

        if 'GPSInfo' in info:
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            loc = ''
            if len(gps_ifd) > 0:
                lat_deg = None
                lat_min = None
                lat_sec = None
                long_deg = None
                long_min = None
                long_sec = None
                if ExifTags.GPS.GPSLatitude in gps_ifd:
                    lat_deg, lat_min, lat_sec = info['GPSLatitude']
                    lat_dir = info['GPSLatitudeRef']
                if ExifTags.GPS.GPSLongitude in gps_ifd:
                    long_deg, long_min, long_sec = info['GPSLongitude']
                    long_dir = info['GPSLongitudeRef']
                if (lat_deg != None and lat_min!= None and \
                        lat_sec!= None ) and \
                        (long_deg!= None  and long_min!= None \
                        and long_sec!= None ):
                    lat = format_dms(lat_deg, lat_min, lat_sec, lat_dir)
                    long = format_dms(long_deg, long_min, long_sec, long_dir)
                    loc += f'Latitude, Longitude: {lat}, {long}'
                    info['location'] = loc

        module_logger.debug(f'get_metadata: done, info {info}')
        return info

    def add_photos(self):
        global module_logger

        module_logger.debug('add_photos: entered in dlg')
        self.filenames = self.get_file_names()
        for name in self.filenames:
            img = QImage(name)
            if img.format == QImage.Format.Format_Invalid:
                module_logger.debug(f'add_photos: {name} is not a valid image')
            else:
                info = self.get_metadata(name)
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
                    photo = PlornDbOperations.get_photo_by_album_and_path( \
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

        module_logger.debug('remove_photos: entered in dlg')
        photos = {}
        for index in self.photos.selectedIndexes():
            item = self.photos.model().itemFromIndex(index)
            if item.row() not in photos.keys():
                photos[item.row()] = {}
        for index in self.photos.selectedIndexes():
            item = self.photos.model().itemFromIndex(index)
            row = item.row()
            module_logger.debug(f'get_inputs: selected {item.text()}')
            if item.column() == 0:
                photos[row]['id'] = item.text()
            elif item.column() == 1:
                photos[row]['photo'] = item.text()
            elif item.column() == 3:
                photos[row]['path'] = item.text()
            module_logger.debug(f'remove_photos: rm {photos[row]}')
        if len(photos) > 0:
            #info['apply'] = True
            #info['filenames'] = self.filenames
            module_logger.debug(f'remove_photos: rm {len(photos)} photos')
        else:
            QMessageBox.critical(self, 'Photo Selection Error',
                        'No photos were selected for removal.')
            #info['apply'] = False
        module_logger.debug('remove_photos: done in dlg')

    def dlg_done(self):
        global module_logger

        module_logger.debug('dlg_done: Done clicked')
        self.setResult(QDialog.DialogCode.Rejected)
        self.close()


