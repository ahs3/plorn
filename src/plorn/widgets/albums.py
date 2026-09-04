
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging

from PyQt6.QtCore import (
    Qt,
)

from PyQt6.QtGui import (
    QStandardItem,
)

from PyQt6.QtSql import (
    QSqlDatabase,
)

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QTextEdit,
)

from plorn.config import PlornConfig
from plorn.model import PlornDbOperations
from plorn.widgets.attrs import PlornAttrListView

module_logger = logging.getLogger('plorn.widgets.albums')
module_logger.setLevel(logging.DEBUG)


#######################################################################
#
#   widgets/views specific to manipulating albums and their contents
#
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
        self.bbox.setObjectName('add_album_bbox')
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
        self.name_edit.setReadOnly(True)
        self.dated_edit.setText(album.get_dated())
        self.dated_edit.setReadOnly(True)
        self.notes_edit.setPlainText(album.get_notes())
        self.notes_edit.setReadOnly(True)
        self.count.setText(str(album.get_photo_count()))
        for name in album.get_name_list():
            id = name.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='names', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: name {id} {value}')
            item = QStandardItem(value)
            self.name_list.appendRow(item)
        for place in album.get_place_list():
            id = place.get_id()
            fullattr = PlornDbOperations.get_full_attr(table='places', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: place {id} {value}')
            item = QStandardItem(value)
            self.place_list.appendRow(item)
        for tag in album.get_tag_list():
            id = int(tag.get_id())
            fullattr = PlornDbOperations.get_full_attr(table='tags', id=id)
            value = ', '.join(fullattr)
            module_logger.debug(f'PlornViewAlbumDialog: tag {str(tag)}')
            module_logger.debug(f'PlornViewAlbumDialog: tag {id} {value}')
            item = QStandardItem(value)
            self.tag_list.appendRow(item)
        module_logger.debug('PlornViewAlbumDialog: set_inputs done')

