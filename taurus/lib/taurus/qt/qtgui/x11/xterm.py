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
        term.xtermcommand = "python"
        term.show()
        term.start()
        app.exec_()

    By default, the widget is set to auto restart if it detects that the
    underlying process the widget embeds finishes.

    By default, the widget is set to *not* auto update. This means you have
    to explicitly call `start()`.
    """

    DefaultCommand = 'xterm'
    DefaultWinIdParam = '-into'

    DefaultUserHost = ''
    DefaultXTermCommand = ''
    DefaultXTermArguments = ''

    def __init__(self, parent=None, designMode=False):
        XCommandWidget.__init__(self, parent=parent, designMode=designMode)
        self.__userHost = self.DefaultUserHost
        self.__xtermCommand = self.DefaultXTermCommand
        self.__xtermArguments = self.DefaultXTermArguments
        self.resetUserHost()
        self.resetXTermCommand()

    def _buildArguments(self):
        userHost = str(self.userHost)
        xtermCommand = str(self.xtermCommand)
        arguments = XCommandWidget._buildArguments(self)
        arguments.extend(self.xtermArguments.split())
        if xtermCommand:
            arguments.append('-e')
            if userHost:
                tmpcmd = ['ssh', '-X', '-t', self.userHost]
                arguments.extend(tmpcmd)
            xtermCommand = xtermCommand.split()
            arguments.extend(xtermCommand)
        return arguments

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
        if userHost == self.__userHost:
            return
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
        if cmd == self.__xtermCommand:
            return
        self.__xtermCommand = cmd
        self.commandChanged.emit()

    def resetXTermCommand(self):
        """
        Resets the xterm command to empty string.
        Emits *commandChanged* signal.
        """
        self.setXTermCommand(self.DefaultXTermCommand)

    @Qt.Slot(str)
    def setXTermArguments(self, arguments):
        """
        Sets extra parameters to the command line (they should be space
        separated). Emits *commandChanged* signal.

        :param arguments: extra parameters string
        :type arguments: str
        """
        if arguments == self.__xtermArguments:
            return
        self.__xtermArguments = arguments
        self.commandChanged.emit()

    def getXTermArguments(self):
        """
        Returns the current extra parameters string.

        :return: the current extra parameters string
        :rtype: str
        """
        return str(self.__xtermArguments)

    def resetXTermArguments(self):
        """
        Resets the extra paramters to default. Emits *commandChanged* signal.
        """
        self.setXTermArguments(self.DefaultXTermArguments)

    #:
    #: This property holds the widget command name (ex: xterm)
    #:
    command = Qt.Property(str, XCommandWidget.getCommand,
                          XCommandWidget.setCommand,
                          XCommandWidget.resetCommand,
                          designable=False)

    #:
    #: This property holds the command parameter name which specifies the
    #: window ID (ex: for xterm is *-into*)
    #:
    winIdParam = Qt.Property(str, XCommandWidget.getWinIdParam,
                             XCommandWidget.setWinIdParam,
                             XCommandWidget.resetWinIdParam,
                             designable=False)

    #:
    #: A space separated list of extra parameters
    #:
    arguments = Qt.Property(str, XCommandWidget.getArguments,
                            XCommandWidget.setArguments,
                            XCommandWidget.resetArguments,
                            designable=False)

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

    #:
    #: A space separated list of extra parameters
    #:
    xtermArguments = Qt.Property(str, getXTermArguments, setXTermArguments,
                                 resetXTermArguments)


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
        self.XWidget().resetUserHost()

    def getXTermCommand(self):
        return str(self.XWidget().xtermCommand)

    @Qt.Slot(str)
    def setXTermCommand(self, cmd):
        self.XWidget().xtermCommand = cmd

    def resetXTermCommand(self):
        self.XWidget().resetXTermCommand()

    def getXTermArguments(self):
        return str(self.XWidget().xtermArguments)

    @Qt.Slot()
    def setXTermArguments(self, cmd):
        self.XWidget().xtermArguments = cmd

    def resetXTermArguments(self):
        self.XWidget().resetXTermArguments()

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
    getXTermArguments.__doc__ = Widget.getXTermArguments.__doc__
    setXTermArguments.__doc__ = Widget.setXTermArguments.__doc__
    resetXTermArguments.__doc__ = Widget.resetXTermArguments.__doc__

    #:
    #: This property holds the widget command name (ex: xterm)
    #:
    command = Qt.Property(str, XCommandWindow.getCommand,
                          XCommandWindow.setCommand,
                          XCommandWindow.resetCommand,
                          designable=False)

    #:
    #: This property holds the command parameter name which specifies the
    #: window ID (ex: for xterm is *-into*)
    #:
    winIdParam = Qt.Property(str, XCommandWindow.getWinIdParam,
                             XCommandWindow.setWinIdParam,
                             XCommandWindow.resetWinIdParam,
                             designable=False)

    #:
    #: A space separated list of extra parameters
    #:
    arguments = Qt.Property(str, XCommandWindow.getArguments,
                            XCommandWindow.setArguments,
                            XCommandWindow.resetArguments,
                            designable=False)

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

    #:
    #: A space separated list of extra parameters
    #:
    xtermArguments = Qt.Property(str, getXTermArguments, setXTermArguments,
                                 resetXTermArguments)


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
