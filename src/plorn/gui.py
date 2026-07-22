#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import enum
#import filetype
import logging
import os.path
#import re
#import shutil
import sys
#import time

from PyQt6.QtCore import (
    QPoint,
    QRect,
    QSize,
    Qt,
)

from PyQt6.QtGui import (
    QAction,
    QColor,
    QIcon,
    QPalette,
    QPixmap,
    QValidator,
)

from PyQt6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)

from plorn.config import PlornConfig
from plorn.model import PlornDbModel
from plorn.widgets import *

#-- set up logging
module_logger = logging.getLogger('plorn.gui')
module_logger.setLevel(logging.DEBUG)

#-- some helper classes that simplify testing the GUI
class PlornAboutDialog(QMessageBox):
    @classmethod
    def ask(cls, parent):
        mbox = cls(parent)
        if mbox.exec() == QMessageBox.StandardButton.Ok:
            return True
        else:
            return False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = PlornConfig()
        photo_path = os.path.join('./src/plorn', config.get_default_photo())
        pmap = QPixmap(photo_path)
        icon = pmap.scaledToHeight(300)
        self.setIconPixmap(icon)
        self.setTextFormat(Qt.TextFormat.MarkdownText)
        self.setText(f'***Plorn: version {config.get_version()}***')
        self.setInformativeText('''
Plorn is a tool to build catalogs of photo albums, without requiring specific locations, image types, or indeed using specific photo applications.
  
Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>  
        ''')


class PlornNewCatalogDialog(QDialog):
    @classmethod
    def ask(cls, parent):
        global module_logger

        dlg = cls(parent)
        result = None
        name = None
        datadir = None
        dbname = None
        dlg.exec()
        if dlg.result() == QDialog.DialogCode.Rejected:
            return False
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setModal(True)
        self.setWindowTitle('New Catalog')
        layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        self.name_label = QLabel('Catalog Name:')
        layout.addWidget(self.name_label, 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1)

        self.ddir_label = QLabel('Data Directory (optional):')
        layout.addWidget(self.ddir_label, 1, 0)
        self.ddir_edit = QLineEdit()
        self.ddir_edit.setText(f'{" ":>40}')
        rect = self.ddir_edit.fontMetrics().boundingRect(self.ddir_edit.text())
        self.ddir_edit.setMinimumWidth(2*rect.width())
        layout.addWidget(self.ddir_edit, 1, 1)

        self.dbname_label = QLabel('Database Name:')
        layout.addWidget(self.dbname_label, 2, 0)
        self.dbname_edit = QLineEdit()
        layout.addWidget(self.dbname_edit, 2, 1)

        self.change_now = QCheckBox('Make this the current catalog')
        self.change_now.setChecked(True)
        layout.addWidget(self.change_now, 3, 1)
        self.make_default = QCheckBox('Make this the default catalog')
        self.make_default.setChecked(False)
        layout.addWidget(self.make_default, 4, 1)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel
        )
        self.bbox.clicked.connect(self.dlg_done)
        layout.addWidget(self.bbox, 5, 0, 1, 2)
        self.setLayout(layout)

    def check_inputs(self):
        if len(self.name_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Catalog Name Error',
                        'A name must be provided.')
            return QDialog.DialogCode.Rejected
        name = self.name_edit.text()
        catalog, datadir, dbname = config.get_catalog(name)
        if catalog != None:
            QMessageBox.warning(self, 'Catalog Name Error',
                     'There is already a catalog with that name.')
            return QDialog.DialogCode.Rejected

        datadir = self.ddir_edit.text()
        if len(datadir) < 1:
            datadir = None
        if len(self.dbname_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Catalog Database Name Error',
                        'A database name must be provided.')
            return QDialog.DialogCode.Rejected
        dbname = self.dbname_edit.text()

        return QDialog.DialogCode.Accepted

    def get_inputs(self):
        catalog = self.name_edit.text()
        datadir = self.ddir_edit.text()
        if len(datadir.strip()) < 1:
            datadir = None
        dbname = self.dbname_edit.text()
        return catalog, datadir, dbname

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Ok:
            module_logger.debug('new cat: Ok clicked')
            if self.check_inputs() == QDialog.DialogCode.Rejected:
                return
            datadir = self.ddir_edit.text()
            if len(datadir.strip()) < 1:
                datadir = None
            config.set_catalog(name=self.name_edit.text(),
                               datadir=datadir,
                               dbname=self.dbname_edit.text(),
            )
            config.write_config()
            self.setResult(QDialog.DialogCode.Accepted)
        elif role == QDialogButtonBox.StandardButton.Cancel:
            module_logger.debug('new cat: Cancel clicked')
            self.setResult(QDialog.DialogCode.Rejected)
        else:
            module_logger.debug('new cat: unknown button clicked')
        self.close()


#-- the actual plorn application
class Plorn(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- define the primary windows
        config = PlornConfig()
        self.setWindowTitle('plorn')
        geometry = self.screen().availableGeometry()
        self.origin = QPoint(200, 200)
        self.size = QSize(int(geometry.width()*0.6), int(geometry.height()*0.7))
        self.setGeometry(QRect(self.origin, self.size))
        self.setWindowIcon(QIcon(config.get_default_photo()))
        self.setSizePolicy(PlornSizePolicy())
        photo_path = os.path.join('./src/plorn', config.get_default_photo())
        self.setWindowIcon(QIcon(photo_path))

        #-- menubar
        self.catalog_menu, self.edit_menu, self.help_menu = self.build_menubar()

        #-- central window
        frame = QFrame()
        palette = frame.palette()
        color = palette.color(frame.backgroundRole())
        palette.setColor(frame.backgroundRole(), color.darker(125))
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)
        margin = 20
        width = self.frameSize().width()

        layout = QVBoxLayout()
        layout.setObjectName('main')
        layout.setDirection(QBoxLayout.Direction.TopToBottom)
        layout.setSpacing(10)
        layout.setContentsMargins(margin,margin,margin,0)
        frame.setLayout(layout)

        self.header, hlayout, lhdr, mhdr, rhdr = self.build_header()
        self.left_header = lhdr
        self.mid_header = mhdr
        self.right_header = rhdr
        layout.addLayout(hlayout)
        layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignTop)

        self.catalog, clayout, self.tree, \
            self.expand_all, self.collapse_all = self.build_catalog()
        layout.addLayout(clayout)
        layout.addWidget(self.catalog, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(8)
        self.tree_data = PlornDbModel(self.tree)
        self.tree_data.add_albums()
        self.tree.expandAll()
        self.expand_all.setEnabled(False)

        sb, counts, catname = self.build_statusbar()
        self.catname = catname                  # so it can be changed later
        self.sbcounts = counts                  # so it can be changed later
        self.setCentralWidget(frame)
        self.set_status_message()

    def get_db(self):
        return self.tree_data.get_db()

    def build_menubar(self):
        #mb = QMenuBar(self)
        mb = self.menuBar()
        mb.setNativeMenuBar(True)

        #-- catalogs menu
        catalogs = mb.addMenu('&Catalogs')
        new_action = QAction('New', parent=self)
        new_action.setObjectName('new_catalog_action')
        new_action.triggered.connect(self.new_catalog_action)
        new_action.setShortcut('Ctrl+N')
        catalogs.addAction(new_action)
        open_action = QAction('Open', parent=self)
        open_action.setObjectName('open_catalog_action')
        open_action.setShortcut('Ctrl+O')
        catalogs.addAction(open_action)
        close_action = QAction('Close', parent=self)
        close_action.setObjectName('close_catalog_action')
        close_action.setShortcut('Ctrl+C')
        catalogs.addAction(close_action)
        quit_action = QAction('Quit', parent=self)
        quit_action.setObjectName('quit_action')
        quit_action.triggered.connect(self.exit_action)
        quit_action.setShortcut('Ctrl+Q')
        catalogs.addAction(quit_action)
        catalogs.insertSeparator(quit_action)

        #-- edit menu
        editmenu = mb.addMenu('&Edit')
        pref_action = QAction('Preferences', parent=self)
        editmenu.addAction(pref_action)
        catalogs.insertSeparator(quit_action)

        #-- help menu
        helpmenu = mb.addMenu('&Help')
        help_action = QAction('Help', parent=self)
        helpmenu.addAction(help_action)
        about_action = QAction('About', parent=self)
        about_action.setObjectName('about_action')
        about_action.triggered.connect(self.about_action)
        helpmenu.addAction(about_action)

        mb.show()
        return catalogs, editmenu, helpmenu

    def build_header(self):
        config = PlornConfig()
        header = QFrame()
        layout = QHBoxLayout()
        layout.setObjectName('header')
        layout.setDirection(QBoxLayout.Direction.LeftToRight)
        header.setSizePolicy(PlornSizePolicy())
        lhdr = QLabel('***plorn: catalog photos***',
                      parent=header,
                      textFormat=Qt.TextFormat.MarkdownText)
        layout.addWidget(lhdr, alignment=Qt.AlignmentFlag.AlignLeft)
        mhdr = QLabel('')
        layout.addWidget(mhdr, alignment=Qt.AlignmentFlag.AlignCenter)
        rhdr = QLabel(f'***version {config.get_version()}***',
                      textFormat=Qt.TextFormat.MarkdownText)
        layout.addWidget(rhdr, alignment=Qt.AlignmentFlag.AlignRight)

        return header, layout, lhdr, mhdr, rhdr

    def build_catalog(self):
        global module_logger

        module_logger.debug('entering build_catalog')
        frame = QFrame()
        layout = QGridLayout()
        layout.setObjectName('catalog')

        tree = QTreeWidget()
        tree.setAlternatingRowColors(True)
        tree.setSizeAdjustPolicy(QTreeWidget.SizeAdjustPolicy.AdjustToContents)
        tree.setHeaderLabels(['Name', 'Photos', 'Type', 'ID'])
        tree.header().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        tree.header().resizeSection(0, 500)
        tree.header().resizeSection(1, 100)
        tree.header().resizeSection(2, 100)
        tree.header().resizeSection(3, 100)
        tree.header().setSectionHidden(3, True)
        hdrItem = tree.headerItem()
        hdrItem.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
        tree.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        layout.addWidget(tree, 0, 0)
        tree.itemExpanded.connect(self.set_expansion_button_state)
        tree.itemCollapsed.connect(self.set_expansion_button_state)

        row_count = tree.topLevelItemCount()
        for row in range(row_count):
            item = self.tree.topLevelItem(row)

        controls = QFrame()
        blayout = QVBoxLayout()
        blayout.setObjectName('catalog controls')
        blayout.setDirection(QBoxLayout.Direction.TopToBottom)
        controls.setSizePolicy(PlornSizePolicy())
        xbutton = PlornPushButton('expand all', default=False,
                                  parent=controls)
        xbutton.clicked.connect(self.expand_all)
        blayout.addWidget(xbutton, alignment=Qt.AlignmentFlag.AlignCenter)
        cbutton = PlornPushButton('collapse all', default=False,
                                  parent=controls)
        cbutton.clicked.connect(self.collapse_all)
        blayout.addWidget(cbutton, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(blayout, 0, 1)
        layout.addWidget(controls, 0, 1)

        return frame, layout, tree, xbutton, cbutton

    def expand_all(self):
        self.tree.expandAll()
        self.set_expansion_button_state()

    def collapse_all(self):
        self.tree.collapseAll()
        self.set_expansion_button_state()

    def build_statusbar(self):
        sb = self.statusBar()
        sb.setSizeGripEnabled(False)
        sb.setSizeGripEnabled(True)

        catname = QLabel('')
        sb.addPermanentWidget(catname)
        spacer = QLabel('     ')
        sb.addPermanentWidget(spacer)
        counts = QLabel('')
        sb.addPermanentWidget(counts)

        sb.showMessage('no catalog currently open')
        return sb, counts, catname

    def set_status_message(self, msg=None):
        if msg:
            txt = msg
        else:
            config = PlornConfig()
            catalog, datadir, dbname = config.get_current_catalog()
            txt = f'opened catalog {catalog}'
            nalbums = self.tree_data.album_count()
            asuffix = 's'
            if nalbums == 1:
                asuffix = ''
            nphotos = self.tree_data.photo_count()
            psuffix = 's'
            if nphotos == 1:
                psuffix = ''
            counts = f'{nalbums} album{asuffix}, {nphotos} photo{psuffix}'
            self.catname.setText(f'catalog: {catalog}')
            self.sbcounts.setText(counts)
        self.statusBar().showMessage(txt)

    def set_expansion_button_state(self):
        expanded = 0
        row_count = self.tree.topLevelItemCount()
        for row in range(row_count):
            #yield item
            item = self.tree.topLevelItem(row)
            if item.isExpanded():
                expanded += 1

        if expanded == 0:
            self.expand_all.setEnabled(True)
            self.collapse_all.setEnabled(False)
        elif expanded == row_count:
            self.expand_all.setEnabled(False)
            self.collapse_all.setEnabled(True)
        else:
            self.expand_all.setEnabled(True)
            self.collapse_all.setEnabled(True)

    def exit_action(self):
        self.close()

    def about_action(self):
        mbox = PlornAboutDialog()
        mbox.ask(self)

    def new_catalog_action(self):
        global module_logger

        newcat = PlornNewCatalogDialog()
        res = newcat.ask(self)
        catalog, datadir, dbname = newcat.get_inputs()
        module_logger.debug(f'new cat action: {catalog}, {datadir}, {dbname}')
            

#-- the plorn GUI
def user_interface():
    plorn_app = QApplication(sys.argv)
    plorn_app.setApplicationName('plorn')
    plorn_app.setStyle('Fusion')

    plorn_root = Plorn()
    plorn_root.show()

    return plorn_app, plorn_root

