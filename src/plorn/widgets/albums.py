
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging

from PyQt6.QtCore import (
    Qt,
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
from plorn.widgets.attrs import PlornAttrListView

module_logger = logging.getLogger('plorn.widgets.albums')
module_logger.setLevel(logging.DEBUG)


#######################################################################
#
#   widgets/views specific to manipulating albums and their contents
#
class PlornAlbumDialog(QDialog):
    @classmethod
    #def ask(cls, parent):
    def ask(cls, dlg):
        dlg.exec()
        return dlg.get_inputs()

    def __init__(self, tree=None, title='Album Dialog', *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        module_logger.debug('entering PlornAlbumDialog: init')
        self.setObjectName('plorn_album_dialog')
        if tree == None:
            return
        self.tree = tree

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

        self.bbox = QDialogButtonBox()
        self.bbox.setObjectName('add_album_bbox')
        done=self.bbox.addButton('Done', QDialogButtonBox.ButtonRole.RejectRole)
        doit=self.bbox.addButton('Apply', QDialogButtonBox.ButtonRole.ApplyRole)
        self.done_button = done
        self.done_button.setDefault(True)
        self.apply_button = doit
        self.apply_button.setObjectName('add_album_apply_button')
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 2, 1, 1, 2)

        attr_layout = QGridLayout()
        self.name_list = PlornAttrListView('names', 'Name Attributes')
        attr_layout.addWidget(self.name_list, 1, 0)
        self.place_list = PlornAttrListView('places', 'Place Attributes')
        attr_layout.addWidget(self.place_list, 2, 0)
        self.tag_list = PlornAttrListView('tags', 'Tag Attributes')
        attr_layout.addWidget(self.tag_list, 3, 0)
        layout.addLayout(attr_layout, 1, 1)

        self.setLayout(layout)
        module_logger.debug('PlornAlbumDialog: init done')

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

        module_logger.debug('PlornAlbumDialog: get_inputs entered')
        info = {}
        info['album'] = self.name_edit.text()
        info['dated'] = self.dated_edit.text()
        info['notes'] = self.notes_edit.toPlainText()
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
                return
            self.setResult(QDialog.DialogCode.Accepted)
            module_logger.debug('album dialog: Apply clicked, and accepted')

        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            module_logger.debug('album dialog: Done clicked')
            self.setResult(QDialog.DialogCode.Rejected)
            module_logger.debug('album dialog: Done clicked, and rejected')

        module_logger.debug(f'dlg_done: Accepted == {QDialog.DialogCode.Accepted}')
        module_logger.debug(f'dlg_done: Rejected == {QDialog.DialogCode.Rejected}')
        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()

