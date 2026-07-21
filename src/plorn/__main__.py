#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

#-- global imports
import logging
import sys

#-- plorn specific imports
from plorn.config import PlornConfig
from plorn.gui import user_interface

#-- set up logging
root_logger = logging.getLogger('')
root_logger.setLevel(logging.INFO)
fh = logging.FileHandler('plorn.log')
fh.setLevel(logging.DEBUG)
fhformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fhformat)
fh.setFormatter(formatter)
root_logger.addHandler(fh)

module_logger = logging.getLogger('plorn')
module_logger.setLevel(logging.INFO)

#-- the plorn GUI
if __name__ == '__main__':
    plorn_app, plorn_root = user_interface()
    sys.exit(plorn_app.exec())
