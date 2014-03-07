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

"""
A XTermWidget runs a xterm.

.. note:: this widgt only works on X11 systems.

Example::

    from taurus.external.qt import Qt
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.x11 import XTermWidget

    app = TaurusApplication()
    term = XTermWidget()
    term.show()
    term.start()
    app.exec_()

Example of a window with a restart button::

    from taurus.external.qt import Qt
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.x11 import XTermWidget

    app = TaurusApplication()
    w = Qt.QWidget()
    l = Qt.QVBoxLayout(w)
    b = Qt.QPushButton("Restart", w)
    term = XTermWidget(w)
    l.addWidget(b)
    l.addWidget(term)
    b.clicked.connect(term.restart)
    w.show()
    app.exec_()
"""

__all__ = ["XTermWidget"]

from taurus.qt import Qt

from taurus.qt.qtgui.x11.xcmd import XCommandWidget, XCommandWindow


class XTermWidget(XCommandWidget):
    """
    A widget with an xterm console inside. Example::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.application import TaurusApplication
        from taurus.qt.qtgui.x11 import XTermWidget
        
        app = TaurusApplication()
        term = XTermWidget()
        term.xtermCommand = "python"
        term.show()
        term.start()
        app.exec_()
    """

    DefaultUserHost = ''
    DefaultXTermCommand = ''
    
    def __init__(self, parent=None, designMode=False):
        XCommandWidget.__init__(self, parent=parent, designMode=designMode)
        self.__userHost = None
        self.__xtermCommand = None
        self.command = 'xterm'
        self.resetUserHost()
        self.resetXTermCommand()

    def _getExtraParams(self):
        userHost = str(self.userHost)
        xtermCmd = str(self.xtermCommand)
        result = XCommandWidget._getExtraParams(self)
        if xtermCmd:
            result.append('-e')
            if userHost:
                tmpcmd = ['ssh', '-X', '-t', self.userHost, '.', '~/.profile', ';']
                result.extend(tmpcmd)
            xtermCmd = xtermCmd.split()
            result.extend(xtermCmd)
        return result
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(icon=":/designer/xterm.png",
                    module="taurus.qt.qtgui.x11.xterm",
                    tooltip="XTerm widget")

    def getUserHost(self):
        return str(self.__userHost)

    def setUserHost(self, userHost):
        self.__userHost = userHost

    def resetUserHost(self):
        self.setUserHost(self.DefaultUserHost)

    def getXTermCommand(self):
        return str(self.__xtermCommand)

    def setXTermCommand(self, cmd):
        self.__xtermCommand = cmd

    def resetXTermCommand(self):
        self.setXTermCommand(self.DefaultXTermCommand)

    userHost = Qt.Property(str, getUserHost, setUserHost,
                           resetUserHost, doc="<user>@<host>")

    xtermCommand = Qt.Property(str, getXTermCommand, setXTermCommand,
                               resetXTermCommand, doc="Command to run on xterm")
    

class XTermWindow(XCommandWindow):
    """
    The QMainWindow version of :class:`XTermWidget`. Example::

        from qarbon.external.qt import Qt
        from qarbon.qt.gui.application import Application
        from qarbon.qt.gui.x11 import XTermWidget

        app = TaurusApplication()
        term = XTermWindow()
        term.show()
        term.start()
        app.exec_()
    """

    Widget = XTermWidget

    def getXTermCommand(self):
        return str(self.XWidget().xtermCommand)

    def setXTermCommand(self, cmd):
        self.XWidget().xtermCommand = cmd

    def resetXTermCommand(self):
        self.XWidget().resetXTermCommand()
            
    xtermCommand = Qt.Property(str, getXTermCommand, setXTermCommand,
                               resetXTermCommand, doc="Command to run on xterm")


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication([])
    w = XTermWidget()
    w.setFixedSize(800, 600)
    w.xtermCommand = 'python'
    w.show()
    w.start()
    app.exec_()

if __name__ == "__main__":
    main()
