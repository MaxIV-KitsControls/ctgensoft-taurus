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

import sys

from taurus.core.util.argparse import get_taurus_parser
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.esrf.qtdesigner import start_qtdesigner


def Application(app_info):
    parser = get_taurus_parser()
    parser.usage = "%prog [options]"
    design_args = "-d", "--design-mode"
    parser.add_option(*design_args, default=False, action="store_true",
                      help="start GUI in design mode (with qtdesigner window)")

    app = TaurusApplication(cmd_line_parser=parser,
                            app_name=app_info.name,
                            app_version=app_info.version,
                            org_name=app_info.org_abbrev,
                            org_domain=app_info.org_url)

    opts = app.get_command_line_options()

    if opts.design_mode:
        designer = start_qtdesigner(app_info.package_name)
        # remove design arguments so that if a restart app happens, the
        # designer is not started again
        for arg in design_args:
            if arg in sys.argv:
                sys.argv.remove(arg)
        def on_quit():
            if designer:
                designer.terminate()
                designer.waitForFinished(-1)
        app.aboutToQuit.connect(on_quit)

    return app
