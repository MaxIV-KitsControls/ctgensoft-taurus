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
    term.start()
    term.show()
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

__all__ = ["XTermWidget", "XTermWindow"]

from taurus.external.qt import Qt
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

    By default, the widget is set to auto restart if it detects that the
    underlying process the widget embeds finishes.

    By default, the widget is set to *not* auto update. This means you have
    to explicitly call `start()`.
    """

    DefaultUserHost = ''
    DefaultXTermCommand = ''
    DefaultWinIdParam = '-into'

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
        return dict(label="XTerm Widget",
                    icon=":/designer/xterm.png",
                    module="taurus.qt.qtgui.x11.xterm",
                    group="Taurus X11 Widgets",
                    tooltip="XTerm widget")

    def getUserHost(self):
        """
        Returns the current user and host (ex: homer@nano)

        :return: the current user and host
        :rtype: str
        """
        return str(self.__userHost)

    @Qt.Slot(str)
    def setUserHost(self, userHost):
        """
        Sets the remote user and host (empty for no remote connection).
        Emits *commandChanged* signal.

        :param userHost: user and host (ex: homer@nano)
        :type userHost: str
        """
        self.__userHost = userHost
        self.commandChanged.emit()

    def resetUserHost(self):
        """
        Resets the user host to empty. Emits *commandChanged* signal.
        """
        self.setUserHost(self.DefaultUserHost)

    def getXTermCommand(self):
        """
        Returns the command to run on the xterm (if any)

        :return: the command to run on the xterm (if any)
        :rtype: str
        """
        return str(self.__xtermCommand)

    @Qt.Slot(str)
    def setXTermCommand(self, cmd):
        """
        Sets the command to run on the xterm (empty string for None)
        (ex: python). Emits *commandChanged* signal.

        :param cmd: command to run on xterm (ex: python)
        :type cmd: str
        """
        self.__xtermCommand = cmd
        self.commandChanged.emit()

    def resetXTermCommand(self):
        """
        Resets the xterm command to empty string.
        Emits *commandChanged* signal.
        """
        self.setXTermCommand(self.DefaultXTermCommand)

    #:
    #: Specifies user and host if xterm is to connect to a remote host (uses
    #: ssh)
    #:
    userHost = Qt.Property(str, getUserHost, setUserHost,
                           resetUserHost, doc="<user>@<host>")
    #:
    #: Specifies the command to run on the xterm. Use empty string (default for
    #: no command (ex: python)
    #:
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

    By default, the widget is set to auto restart if it detects that the
    underlying process the widget embeds finishes.

    By default, the widget is set to *not* auto update. This means you have
    to explicitly call `start()`.
    """

    Widget = XTermWidget

    def getUserHost(self):
        return self.XWidget().userHost

    @Qt.Slot(str)
    def setUserHost(self, userHost):
        self.XWidget().userHost = userHost

    def resetUserHost(self):
        self.XWidget().resetUserHost

    def getXTermCommand(self):
        return str(self.XWidget().xtermCommand)

    @Qt.Slot()
    def setXTermCommand(self, cmd):
        self.XWidget().xtermCommand = cmd

    def resetXTermCommand(self):
        self.XWidget().resetXTermCommand()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(label="XTerm Window",
                    icon=":/designer/xterm.png",
                    module="taurus.qt.qtgui.x11.xterm",
                    group="Taurus X11 Widgets",
                    tooltip="XTerm window")

    getUserHost.__doc__ = Widget.getUserHost.__doc__
    setUserHost.__doc__ = Widget.setUserHost.__doc__
    resetUserHost.__doc__ = Widget.resetUserHost.__doc__
    getXTermCommand.__doc__ = Widget.getXTermCommand.__doc__
    setXTermCommand.__doc__ = Widget.setXTermCommand.__doc__
    resetXTermCommand.__doc__ = Widget.resetXTermCommand.__doc__

    #:
    #: Specifies user and host if xterm is to connect to a remote host (uses
    #: ssh)
    #:
    userHost = Qt.Property(str, getUserHost, setUserHost,
                           resetUserHost, doc="<user>@<host>")

    #:
    #: Specifies the command to run on the xterm. Use empty string (default for
    #: no command (ex: python)
    #:
    xtermCommand = Qt.Property(str, getXTermCommand, setXTermCommand,
                               resetXTermCommand, doc="Command to run on xterm")


def main():
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication([])
    w = XTermWindow()
    w.setFixedSize(800, 600)
    w.xtermCommand = 'python'
    w.show()
    w.start()
    app.exec_()

if __name__ == "__main__":
    main()
