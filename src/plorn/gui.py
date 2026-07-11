#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

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
)

from PyQt6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QDockWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
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

#from PIL import Image as pilImage
#from PIL import ImageTk

#import plorn.common
#from plorn.common import SearchDomains, SearchDomainStrings
#from plorn.common import SearchFields, SearchFieldStrings
#from plorn.common import AlbumSearchInfo, PhotoSearchInfo
from plorn.config import config
#import plorn.db
from plorn.model import PlornDbModel
#import plorn.search
from plorn.widgets import *


#-- set up logging
module_logger = logging.getLogger('plorn.gui')
module_logger.setLevel(logging.DEBUG)

#-- the actual plorn application
class Plorn(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- define the primary windows
        self.setWindowTitle('plorn')
        geometry = self.screen().availableGeometry()
        self.origin = QPoint(200, 200)
        self.size = QSize(int(geometry.width()*0.6), int(geometry.height()*0.7))
        self.setGeometry(QRect(self.origin, self.size))
        self.setWindowIcon(QIcon(config.get_default_photo()))
        self.setSizePolicy(PlornSizePolicy())
        self.build_menubar()

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
        layout.addStretch(1)

        self.catalog, clayout, self.tree, \
            self.expand_all, self.collapse_all = self.build_catalog()
        layout.addLayout(clayout)
        layout.addWidget(self.catalog, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(8)
        self.tree_data = PlornDbModel(self.tree)
        self.tree_data.add_albums()
        self.tree.expandAll()
        self.expand_all.setEnabled(False)

        self.build_statusbar()
        self.setCentralWidget(frame)
        self.set_status_message()

    def build_menubar(self):
        #mb = QMenuBar(self)
        mb = self.menuBar()
        mb.setNativeMenuBar(True)

        #-- catalogs menu
        catalogs = mb.addMenu('&Catalogs')
        new_action = QAction('New', parent=self)
        new_action.setShortcut('Ctrl+N')
        catalogs.addAction(new_action)
        open_action = QAction('Open', parent=self)
        open_action.setShortcut('Ctrl+O')
        catalogs.addAction(open_action)
        close_action = QAction('Close', parent=self)
        close_action.setShortcut('Ctrl+C')
        catalogs.addAction(close_action)
        quit_action = QAction('Quit', parent=self)
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
        about_action.triggered.connect(self.about_action)
        helpmenu.addAction(about_action)

        mb.show()
        return mb

    def build_header(self):
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
        sb.showMessage('no album currently open')

        return sb

    def set_status_message(self):
        msg = self.tree_data.get_sb_msg()
        self.statusBar().showMessage(msg)

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
        mbox = QMessageBox(self)
        photo_path = os.path.join('./src/plorn', config.get_default_photo())
        pmap = QPixmap(photo_path)
        icon = pmap.scaledToHeight(300)
        mbox.setIconPixmap(icon)
        mbox.setTextFormat(Qt.TextFormat.MarkdownText)
        mbox.setText(f'***Plorn: version {config.get_version()}***')
        mbox.setInformativeText('''
Plorn is a tool to build catalogs of photo albums, without
requiring specific locations, image types, or indeed using
specific photo applications.
  
  
Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>  
        ''')
        mbox.exec()


#-- the plorn GUI
def user_interface():
    plorn_app = QApplication(sys.argv)
    plorn_app.setApplicationName('plorn')
    plorn_app.setStyle('Fusion')

    plorn_root = Plorn()
    plorn_root.show()

    return plorn_app, plorn_root

