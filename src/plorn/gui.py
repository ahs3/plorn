#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import enum
import logging
import os.path
import sys

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
    QStandardItem,
    QValidator,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlRelationalDelegate,
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
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QStatusBar,
    QTreeView,
    QTreeWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)

from plorn.album_widgets import PlornNewAlbumDialog
from plorn.config import PlornConfig
from plorn.db import AlbumFields
from plorn.model import album_stats
from plorn.widgets import (
    IDDelegate,
    PlornAlbumView,
    PlornAttrView,
    PlornSizePolicy,
)

#-- set up logging
module_logger = logging.getLogger('plorn.gui')
module_logger.setLevel(logging.DEBUG)


#-- some helper classes that simplify testing the GUI or whatever
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
        res = dlg.exec()
        info = dlg.get_inputs()
        return info

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
        self.ddir_edit.setText('')
        layout.addWidget(self.ddir_edit, 1, 1)

        self.dbname_label = QLabel('Database Name:')
        layout.addWidget(self.dbname_label, 2, 0)
        self.dbname_edit = QLineEdit()
        layout.addWidget(self.dbname_edit, 2, 1)

        self.make_current = QCheckBox('Make this the current catalog')
        self.make_current.setChecked(True)
        layout.addWidget(self.make_current, 3, 1)
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
        global module_logger

        if len(self.name_edit.text().strip()) < 1:
            QMessageBox.warning(self, 'Catalog Name Error',
                        'A name must be provided.')
            return QDialog.DialogCode.Rejected
        name = self.name_edit.text()
        config = PlornConfig()
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

        module_logger.debug('check_inputs returns accepted')
        return QDialog.DialogCode.Accepted

    def get_inputs(self):
        global module_logger

        info = {}
        info['catalog'] = self.name_edit.text()
        info['datadir'] = self.ddir_edit.text()
        datadir = self.ddir_edit.text()
        if len(datadir.strip()) < 1:
            datadir = None
        info['datadir'] = datadir
        info['dbname'] = self.dbname_edit.text()
        info['make_current'] = self.make_current.isChecked()
        info['make_default'] = self.make_default.isChecked()
        module_logger.debug(f'get_inputs returns {info}')
        return info

    def dlg_done(self, button):
        global module_logger

        role = self.bbox.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Ok:
            module_logger.debug('new cat: Ok clicked')
            if self.check_inputs() == QDialog.DialogCode.Rejected:
                return
            self.setResult(QDialog.DialogCode.Accepted)

        elif role == QDialogButtonBox.StandardButton.Cancel:
            module_logger.debug('new cat: Cancel clicked')
            self.setResult(QDialog.DialogCode.Rejected)

        module_logger.debug(f'dlg_done returns {self.result()}')
        self.close()


#-- the actual plorn application
class Plorn(QMainWindow):
    def __init__(self, *args, **kwargs):
        global module_logger
        super().__init__(*args, **kwargs)

        #-- open up the data base
        config = PlornConfig()
        catname, datadir, dbname = config.get_current_catalog()
        if not catname:
            catname, datadir, dbname = config.get_default_catalog()
        self.dbname = dbname
        dbpath = os.path.join(datadir, dbname)

        #-- define the primary windows
        self.setWindowTitle('plorn')
        geometry = self.screen().availableGeometry()
        self.origin = QPoint(200, 200)
        self.size = QSize(int(geometry.width()*0.8), int(geometry.height()*0.7))
        self.setGeometry(QRect(self.origin, self.size))
        self.setWindowIcon(QIcon(config.get_default_photo()))
        self.setSizePolicy(PlornSizePolicy())
        photo_path = os.path.join('./src/plorn', config.get_default_photo())
        self.setWindowIcon(QIcon(photo_path))

        #-- menubar
        mb, cats, albs, phos, tools, helpmenu = self.build_menubar()
        self.catalogs_menu = cats
        self.albums_menu = albs
        self.photos_menu = phos
        self.tools_menu = tools
        self.help_menu = helpmenu

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

        spacer = QSpacerItem(800, 50, hPolicy=QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        tree, hdr = self.build_catalog(layout)
        self.album_tree = tree
        self.catalog_header = hdr

        sb, counts, catname = self.build_statusbar()
        self.catname = catname                  # so it can be changed later
        self.sbcounts = counts                  # so it can be changed later
        self.setCentralWidget(frame)
        self.set_catalog_info()
        self.set_status_message('ready')

    def set_status_message(self, msg, timeout=5000):
        self.statusBar().showMessage(msg, msecs=timeout)

    def get_db(self):
        config = PlornConfig()
        catname, datadir, dbname = config.get_current_catalog()
        return QSqlDatabase.database(catname)

    def _catalogs_menu(self, mb):
        catalogs = mb.addMenu('&Catalogs')
        new_action = QAction('&New', parent=self)
        new_action.setObjectName('new_catalog_action')
        new_action.triggered.connect(self.new_catalog_action)
        catalogs.addAction(new_action)

        open_menu = catalogs.addMenu('&Open')
        open_menu.aboutToShow.connect(self.update_open_catalogs)
        open_menu.triggered.connect(self.open_catalog)
        if not hasattr(self, 'open_catalog_menu'):
            setattr(self, 'open_catalog_menu', open_menu)

        delete_menu = catalogs.addMenu('&Delete')
        delete_menu.aboutToShow.connect(self.update_removable_catalogs)
        delete_menu.triggered.connect(self.delete_catalog)
        if not hasattr(self, 'delete_catalog_menu'):
            setattr(self, 'delete_catalog_menu', delete_menu)

        return catalogs

    def _albums_menu(self, mb):
        albums = mb.addMenu('&Albums')
        new_action = QAction('&New', parent=self)
        new_action.setObjectName('new_album_action')
        new_action.triggered.connect(self.new_album_action)
        albums.addAction(new_action)

        open_action = QAction('&Open', parent=self)
        open_action.setObjectName('open_album_action')
        albums.addAction(open_action)
        edit_action = QAction('&Edit', parent=self)
        edit_action.setObjectName('edit_album_action')
        albums.addAction(edit_action)
        del_action = QAction('&Delete', parent=self)
        del_action.setObjectName('del_album_action')
        albums.addAction(del_action)
        return albums

    def _photos_menu(self, mb):
        photos = mb.addMenu('&Photos')
        new_action = QAction('New', parent=self)
        new_action.setObjectName('new_photo_action')
        new_action.triggered.connect(self.new_photo_action)
        photos.addAction(new_action)
        open_action = QAction('Open', parent=self)
        open_action.setObjectName('open_photo_action')
        photos.addAction(open_action)
        edit_action = QAction('Edit', parent=self)
        edit_action.setObjectName('edit_photo_action')
        photos.addAction(edit_action)
        del_action = QAction('Delete', parent=self)
        del_action.setObjectName('del_photo_action')
        photos.addAction(del_action)
        return photos

    def _attrs_menu(self, mb):
        attrs = mb.addMenu('&Attrbutes')
        names_action = QAction('&Names', parent=self)
        names_action.setObjectName('name_attr_action')
        names_action.triggered.connect(self.names_attr_action)
        attrs.addAction(names_action)

        places_action = QAction('&Places', parent=self)
        places_action.setObjectName('place_attr_action')
        places_action.triggered.connect(self.places_attr_action)
        attrs.addAction(places_action)

        tags_action = QAction('&Tags', parent=self)
        tags_action.setObjectName('tag_attr_action')
        tags_action.triggered.connect(self.tags_attr_action)
        attrs.addAction(tags_action)

        return attrs

    def _tools_menu(self, mb):
        tools = mb.addMenu('&Tools')
        pref_action = QAction('Preferences', parent=self)
        tools.addAction(pref_action)
        return tools

    def _help_menu(self, mb):
        helpmenu = mb.addMenu('&Help')
        help_action = QAction('Help', parent=self)
        helpmenu.addAction(help_action)
        about_action = QAction('About', parent=self)
        about_action.setObjectName('about_action')
        about_action.triggered.connect(self.about_action)
        helpmenu.addAction(about_action)
        return helpmenu

    def build_menubar(self):
        mb = self.menuBar()
        mb.setNativeMenuBar(True)

        #-- catalogs menu
        catalogs = self._catalogs_menu(mb)
        quit_action = QAction('Quit', parent=self)
        quit_action.setObjectName('quit_action')
        quit_action.triggered.connect(self.exit_action)
        quit_action.setShortcut('Ctrl+Q')
        catalogs.addAction(quit_action)
        catalogs.insertSeparator(quit_action)

        #-- submenus ....
        albums   = self._albums_menu(mb)
        photos   = self._photos_menu(mb)
        attrs    = self._attrs_menu(mb)
        tools    = self._tools_menu(mb)
        helpmenu = self._help_menu(mb)

        mb.show()
        return mb, catalogs, albums, photos, tools, helpmenu

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

    def open_db(self):
        global module_logger

        module_logger.debug('entering build_db')
        module_logger.debug(f'build_db: {QSqlDatabase.connectionNames()}')
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        
        olddb = QSqlDatabase.database(catalog)
        if olddb.isOpen() and olddb.isValid():
            module_logger.debug(f'build_db: using {olddb.connectionName()}')
            return olddb

        db = QSqlDatabase.addDatabase('QSQLITE', connectionName=catalog)
        dbpath = os.path.join(datadir, dbname)
        db.setDatabaseName(dbpath)
        res = db.open()
        if res:
            module_logger.debug(f'build_db: db opened for {catalog}')
        else:
            module_logger.debug(f'build_db: db open failed for {catalog}')
            module_logger.debug(f'build_db fail: {db.lastError().text()}')
        return db

    def prettify_album_tree(self, tree):
        global module_logger

        tree.setAlternatingRowColors(True)
        tree.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        tree.setItemsExpandable(False)

        tree.header().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        tree.header().setSectionHidden(AlbumFields.NOTES, True)

        chunk = 25
        tree.header().setMaximumSectionSize(int(40*chunk))
        tree.header().resizeSection(AlbumFields.ID, int(4*chunk))
        tree.header().resizeSection(AlbumFields.NAME, int(24*chunk))
        tree.header().resizeSection(AlbumFields.DATED, int(8*chunk))
        tree.header().resizeSection(AlbumFields.PHOTO_COUNT, int(4*chunk))

        tree.setItemDelegateForColumn(AlbumFields.ID, IDDelegate())
        #tree.setItemDelegate(QSqlRelationalDelegate(tree))


    def build_catalog(self, layout):
        global module_logger

        module_logger.debug('entering build_catalog')

        config = PlornConfig()
        catname, ddir, dbname = config.get_current_catalog()
        cathdr = QLabel(f'**Catalog:** {catname}',
                      textFormat=Qt.TextFormat.MarkdownText)
        layout.addWidget(cathdr)

        #--- build the album tree view
        db = self.open_db()
        tree = PlornAlbumView(db=db)
        layout.addWidget(tree, stretch=1)

        return tree, cathdr

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

    def set_catalog_info(self):
        global module_logger

        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.catalog_header.setText(f'**Catalog:** {catalog}')
        nalbums, nphotos = album_stats()
        asuffix = 's'
        if nalbums == 1:
            asuffix = ''
        psuffix = 's'
        if nphotos == 1:
            psuffix = ''
        counts = f'{nalbums} album{asuffix}, {nphotos} photo{psuffix}'
        self.catname.setText(f'database: {os.path.basename(dbname)}')
        self.sbcounts.setText(counts)

    def exit_action(self):
        self.close()

    def about_action(self):
        mbox = PlornAboutDialog()
        mbox.ask(self)

    def new_catalog_action(self):
        global module_logger

        catdlg = PlornNewCatalogDialog()
        info = catdlg.ask(self)
        msg  = f'new cat action: '
        msg += f'cat {info['catalog']}, '
        msg += f'ddir {info['datadir']}, '
        msg += f'db {info['dbname']}, '
        msg += f'chg {info['make_current']}, '
        msg += f'def {info['make_default']}'
        module_logger.debug(msg)

        #-- input values have already been checked for validity
        config = PlornConfig()
        new_cat = info['catalog']
        new_ddir = info['datadir']
        new_dbnm = info['dbname']
        if new_ddir != None and len(new_ddir.strip()) < 1:
            new_ddir = None
        catalog, datadir, dbname = config.get_current_catalog()
        module_logger.debug(f'new cat: current is {catalog}')
        if len(info['catalog']) > 0 and info['make_current'] == True:
            if catalog != new_cat:
                config.set_catalog(name=new_cat,
                                   datadir=new_ddir,
                                   dbname=new_dbnm)
                config.write_config()
                module_logger.debug(f'new cat: make {new_cat} current')
                config.set_current_catalog(new_cat)
                config.write_config()

                model = self.album_tree.model()
                model.setFilter('')
                model.setSort(-1, Qt.SortOrder.AscendingOrder)
                model.submitAll()
                model.select()
                db = self.open_db()
                new_model = PlornAlbumModel(parent=self.album_tree, db=db)
                self.album_tree.setModel(new_model)

                module_logger.debug(f'new cat: current is now {new_cat}')
                self.prettify_album_tree(self.album_tree)
                self.set_catalog_info()

        if len(info['catalog']) > 0 and info['make_default'] == True:
            catalog, datadir, dbname = config.get_default_catalog()
            module_logger.debug(f'new cat: default is {catalog}')
            if catalog != new_cat:
                config.set_catalog(name=new_cat,
                                   datadir=new_ddir,
                                   dbname=new_dbnm)
                config.write_config()
                config.set_default_catalog(new_cat)
                config.write_config()
                module_logger.debug(f'new cat: {new_cat} is now default')

    def update_open_catalogs(self):
        global module_logger

        module_logger.debug('entering upd_open_cat')
        self.open_catalog_menu.clear()
        self.open_catalog_menu.addSection('Catalogs')
        config = PlornConfig()
        current, cur_ddir, curdbname = config.get_current_catalog()
        catlist = config.get_catalog_list()
        for name in catlist:
            open_action = self.open_catalog_menu.addAction(f'{name}')
            open_action.setCheckable(True)
            if name == current:
                open_action.setChecked(True)
            else:
                open_action.setChecked(False)
            open_action.setData(name)

    def open_catalog(self, action):
        config = PlornConfig()
        config.set_current_catalog(action.data())
        config.write_config()
        db = self.open_db()
        model = PlornAlbumModel(parent=self.album_tree, db=db)
        self.album_tree.setModel(model)
        self.prettify_album_tree(self.album_tree)
        self.set_catalog_info()

    def update_removable_catalogs(self):
        global module_logger

        module_logger.debug('entering upd_remv_cat')
        self.delete_catalog_menu.clear()
        self.delete_catalog_menu.addSection('Catalogs')
        config = PlornConfig()
        current, cur_ddir, curdbname = config.get_current_catalog()
        catlist = config.get_catalog_list()
        for name in catlist:
            if name == current:
                continue
            del_action = self.delete_catalog_menu.addAction(f'{name}')
            del_action.setCheckable(True)
            del_action.setChecked(False)
            del_action.setData(name)

    def delete_catalog(self, action):
        '''
        make sure they _really_ want to do this ....
        '''
        config = PlornConfig()
        catalog, ddir, dbname = self.get_catalog(action.data())

        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Warning)
        mbox.setText(f'This only removes the catalog information from the configuration file.  The database "{dbname}" must be removed manually.')
        msg = f'Are you SURE you want to delete the {action.data()} catalog?'
        mbox.setInformativeText(msg)
        mbox.setStandardButtons(QMessageBox.StandardButton.Yes | \
                                QMessageBox.StandardButton.Cancel)
        mbox.setDefaultButton(QMessageBox.StandardButton.Cancel)
        ret = mbox.exec()

        if ret == QMessageBox.StandardButton.Cancel:
            return

        config.remove_catalog(action.data())
        config.write_config()

    def new_album_action(self):
        global module_logger

        new_album_dlg = PlornNewAlbumDialog()
        info = new_album_dlg.ask(self)
        #msg  = f'new cat action: '
        #msg += f'cat {info['catalog']}, '
        #msg += f'ddir {info['datadir']}, '
        #msg += f'db {info['dbname']}, '
        #msg += f'chg {info['make_current']}, '
        #msg += f'def {info['make_default']}'
        #module_logger.debug(msg)

        #-- input values have already been checked for validity
        #config = PlornConfig()
        #new_cat = info['catalog']
        #new_ddir = info['datadir']
        #new_dbnm = info['dbname']
        #if new_ddir != None and len(new_ddir.strip()) < 1:
        #    new_ddir = None
        #config.set_catalog(name=new_cat, datadir=new_ddir, dbname=new_dbnm)
        #config.write_config()
        #if info['make_current']:
        #    catalog, datadir, dbname = config.get_current_catalog()
        #    module_logger.debug(f'new cat: current is {catalog}')
        #    if catalog != new_cat:
        #        module_logger.debug(f'new cat: make {new_cat} current')
        #        config.set_current_catalog(new_cat)
        #        config.write_config()

        #        model = self.album_tree.model()
        #        model.setFilter('')
        #        model.setSort(-1, Qt.SortOrder.AscendingOrder)
        #        model.submitAll()
        #        model.select()
        #        db = self.open_db()
        #        new_model = PlornAlbumModel(parent=self.album_tree, db=db)
        #        self.album_tree.setModel(new_model)

        #        module_logger.debug(f'new cat: current is now {new_cat}')
        #        self.prettify_album_tree(self.album_tree)
        #        self.set_catalog_info()

        #if info['make_default']:
        #    catalog, datadir, dbname = config.get_default_catalog()
        #    module_logger.debug(f'new cat: default is {catalog}')
        #    if catalog != new_cat:
        #        config.set_default_catalog(new_cat)
        #        config.write_config()
        #        module_logger.debug(f'new cat: {new_cat} is now default')


    def new_photo_action(self):
        pass

    def names_attr_action(self):
        global module_logger
        
        db = self.open_db()
        name_view = PlornAttrView(title='Names', table='names', db=db)
        name_view.exec()
        module_logger.debug('name_attr_action done')

    def places_attr_action(self):
        global module_logger
        
        db = self.open_db()
        place_view = PlornAttrView(title='Places', table='places', db=db)
        place_view.exec()
        module_logger.debug('place_attr_action done')

    def tags_attr_action(self):
        global module_logger
        
        db = self.open_db()
        tag_view = PlornAttrView(title='Tags', table='tags', db=db)
        tag_view.exec()
        module_logger.debug('tag_attr_action done')


#-- the plorn GUI
def user_interface():
    plorn_app = QApplication(sys.argv)
    plorn_app.setApplicationName('plorn')
    plorn_app.setStyle('Fusion')

    plorn_root = Plorn()
    plorn_root.show()

    return plorn_app, plorn_root

