# -*- coding: utf-8 -*-

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""A X11 widget that may run any command and an XTermWidget runs a xterm.

.. note:: this widget only works on X11 systems.

Example::

    from taurus.external.qt import QtGui
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.x11 import XTermWindow

    app = Application()
    term = XTermWindow()
    term.start()
    term.show()
    app.exec_()"""

__docformat__ = 'restructuredtext'

from .xcmd import XCommandWidget
from .xterm import XTermWidget
