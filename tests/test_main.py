
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os

def test_main(plorn_test_env, GUI):
    tmpdir, cfgdir, datadir = plorn_test_env
    app, root, qtbot = GUI
    assert app != None
    assert root != None

