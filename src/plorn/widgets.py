#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging

from PyQt6.QtCore import (
    QSize,
)

from PyQt6.QtWidgets import (
    QPushButton,
    QSizePolicy,
)

from plorn.config import PlornConfig

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.INFO)

class PlornSizePolicy(QSizePolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalPolicy = QSizePolicy.Policy.Expanding
        self.verticalPolicy = QSizePolicy.Policy.Expanding

class PlornButtonSize(QSize):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHeight(200)
        self.setWidth(500)

class PlornPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sizeHint = PlornButtonSize()
        self.setSizePolicy(PlornSizePolicy())
        self.flat = False

def make_button(parent, text='Button', command=None, width=10, **kwargs):
    return ttk.Button(parent, text=text, command=command, width=width,
                      bootstyle="outline-primary", **kwargs)

def make_header_label(parent, width=20, text='', size=None):
    lbl = ttk.Label(parent, width=width, text=text)
    if not size:
        size = get_config().get_fontsize()+4
    lbl.configure(font=(font.nametofont('TkDefaultFont'),
                        size, 'bold', 'italic'))
    return lbl

