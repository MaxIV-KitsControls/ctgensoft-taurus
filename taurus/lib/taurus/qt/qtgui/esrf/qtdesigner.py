# -*- coding: utf-8 -*-
#
# This file is part of ESRF taurus widgets
# (http://gitlab.esrf.fr/taurus/taurus-esrf)
#
# Copyright (c) 2014 European Synchrotron Radiation Facility, Grenoble, France
#
# Distributed under the terms of the GNU Lesser General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#

import os

def start_qtdesigner(app_package_name):
    from taurus.external.qt import Qt
    from taurus.qt.qtdesigner.taurusdesigner import (qtdesigner_start,
                                                     qtdesigner_prepare_taurus,
                                                     append_or_create_env)

    package = __import__(app_package_name)
    package_dir = os.path.dirname(os.path.realpath(package.__file__))
    gui_dir = os.path.realpath(os.path.join(package_dir, os.path.pardir))
    ui_dir = os.path.join(package_dir, 'ui')
    ui_files = [os.path.join(ui_dir, f) for f in os.listdir(ui_dir)
                if f.endswith('.ui')]
    # If too many ui files exist, open the main window only
    if len(ui_files) > 3:
        ui_files = [os.path.join(ui_dir, 'BaseWindow.ui')]

    env = Qt.QProcess.systemEnvironment()
    qtdesigner_prepare_taurus(env, taurus_extra_package=app_package_name)
    append_or_create_env(env, "PYTHONPATH", gui_dir)
    return qtdesigner_start(ui_files, env=env, wait_for_finished=False)
