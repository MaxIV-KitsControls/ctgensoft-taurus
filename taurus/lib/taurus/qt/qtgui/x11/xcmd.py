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
A XCommandWidget that may run any command

.. note:: this widget only works on X11 systems.

Example::

    from taurus.external.qt import Qt
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.x11.xcmd import XCommandWidget

    app = TaurusApplication()
    cmdWidget = XCommandWidget()
    cmdWidget.command = 'xterm'
    cmdWidget.winIdParam = '-into'
    cmdWidget.show()
    cmdWidget.start()

    app.exec_()
"""

__all__ = ["XCommandWidget"]

import os
import signal
import weakref

from taurus.core.util import log
from taurus.qt import Qt
from taurus.qt.qtgui.resource import getThemeIcon
from taurus.qt.qtgui.util.taurusactionfactory import ActionFactory


class XCommandWidget(Qt.QWidget):
    """
    A widget displaying an X11 window inside from a command. Example::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.application import TaurusApplication
        from taurus.qt.qtgui.x11.xcmd import XCommandWidget

        app = TaurusApplication()
        cmdWidget = XCommandWidget()
        cmdWidget.command = 'xterm'
        cmdWidget.winIdParam = '-into'
        cmdWidget.show()
        cmdWidget.start()

        app.exec_()
    """

    DefaultAutoRestart = True
    DefaultWinIdParam = '-into'
    DefaultExtraParams = ''
    
    def __init__(self, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self.__command = None
        self.__winIdParam = None
        self.__extraParams = []
        self.__autoRestart = False # Must be False!
        self.__pid = None
        self.__idle = Qt.QTimer(self)
        self.__idle.timeout.connect(self.__start)
        self.__x11Widget = Qt.QX11EmbedContainer(self)
        self.__x11Widget.error.connect(self.__onError)
        Qt.qApp.aboutToQuit.connect(self.__onQuit)
        
        layout = Qt.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.__x11Widget)

        self.resetCommand()
        self.resetWinIdParam()
        self.resetExtraParams()
        self.resetAutoRestart()

    def __del__(self):
        self.terminate()
        
    def __onError(self, error):
        log.error("XEmbedContainer: Error")
        log.debug("XEmbedContainer: Error details: %s", error)

    def __isRunning(self):
        return self.__pid is not None and self.__pid > 0
    
    def __onQuit(self):
        self.autoRestart = False
        self.terminate()
        
    def __start(self):
        self.__idle.stop()
        cmd = [self.command, self.winIdParam, str(self.getX11WinId())] + \
               self._getExtraParams()
        self.__pid = os.fork()
        if not self.__pid:
            # child exec the command
            cmd = ['/usr/bin/env', 'env'] + cmd
            os.execl(*cmd)
            os.exit()
        else:
            log.info("Running: %s", " ".join(cmd))

    def _getExtraParams(self):
        return self.extraParams.split()
            
    def getX11Widget(self):
        return self.__x11Widget

    def getX11WinId(self):
        return self.getX11Widget().winId()
    
    @Qt.Slot()
    def start(self):
        if self.__isRunning():
            os.waitpid(self.__pid, os.WNOHANG)
            self.__pid = None
        self.__idle.start(0)

    @Qt.Slot()        
    def restart(self):
        if self.autoRestart:
            if self.__isRunning():
                self.terminate()
            else:
                self.start()
        else:
            self.terminate()
            self.start()
            
    @Qt.Slot()
    def kill(self):
        if self.__isRunning():
            os.kill(self.__pid, signal.SIGKILL)
            self.__pid = None

    @Qt.Slot()
    def terminate(self):
        if self.__isRunning():
            os.kill(self.__pid, signal.SIGTERM)
            self.__pid = None

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(icon=":/designer/xorg.png",
                    module="taurus.qt.qtgui.x11.xcmd",
                    tooltip="XCommand widget")
            
    # Qt Properties

    def getCommand(self):
        return str(self.__command)

    def setCommand(self, command):
        self.__command = command
        if command is None:
            self.setWindowTitle("<None>")
        else:
            self.setWindowTitle(command)

    def resetCommand(self):
        self.setCommand(None)

    def getWinIdParam(self):
        return str(self.__winIdParam)

    def setWinIdParam(self, winIdParam):
        self.__winIdParam = winIdParam

    def resetWinIdParam(self):
        self.setWinIdParam(self.DefaultWinIdParam)

    def setExtraParams(self, params):
        self.__extraParams = params

    def getExtraParams(self):
        return self.__extraParams

    def resetExtraParams(self):
        self.setExtraParams(self.DefaultExtraParams)

    def setAutoRestart(self, yesno):
        if yesno == self.__autoRestart:
            return
        self.__autoRestart = yesno
        x11Widget = self.getX11Widget()
        if yesno:
            f = x11Widget.clientClosed.connect
        else:
            f = x11Widget.clientClosed.disconnect
        f(self.start)

    def getAutoRestart(self):
        return self.__autoRestart

    def resetAutoRestart(self):
        return self.setAutoRestart(self.DefaultAutoRestart)

    command = Qt.Property(str, getCommand, setCommand, resetCommand)

    winIdParam = Qt.Property(str, getWinIdParam, setWinIdParam,
                                 resetWinIdParam)

    extraParams = Qt.Property(str, getExtraParams, setExtraParams,
                              resetExtraParams)

    autoRestart = Qt.Property(bool, getAutoRestart, setAutoRestart,
                              resetAutoRestart)


class XCommandWindow(Qt.QMainWindow):
    """
    The QMainWindow version of :class:`XCommandWidget`. Example::
    
        from taurus.external.qt import Qt
        from taurus.qt.qtgui.application import TaurusApplication
        from taurus.qt.qtgui.x11 import XCommandWindow

        app = TaurusApplication()
        cmdWindow = XCommandWindow()
        cmdWindow.command = 'xterm'
        cmdWindow.winIdParam = '-into'
        cmdWindow.show()
        cmdWindow.start()

        app.exec_()
    """

    Widget = XCommandWidget

    def __init__(self, **kwargs):
        parent = kwargs.pop('parent', None)
        flags = kwargs.pop('flags', Qt.Qt.WindowFlags())
        super(XCommandWindow, self).__init__(parent=parent, flags=flags)
        x11 = self.Widget(parent=self, **kwargs)
        self.setCentralWidget(x11)
        toolBar = self.addToolBar("Actions")
        self.__actionsToolBar = weakref.ref(toolBar)
        action_factory = ActionFactory()
        self.__restartAction = action_factory.createAction(self,
                                      text="Restart",
                                      icon=getThemeIcon("view-refresh"),
                                      tip="restart the current command",
                                      triggered=self.restart)
        toolBar.addAction(self.__restartAction)

    def XWidget(self):
        return self.centralWidget()

    @Qt.Slot()
    def start(self):
        self.XWidget().start()

    @Qt.Slot()
    def restart(self):
        self.XWidget().restart()

    @Qt.Slot()        
    def terminate(self):
        self.XWidget().terminate()

    @Qt.Slot()        
    def kill(self):
        self.XWidget().kill()

    def getCommand(self):
        return self.XWidget().command

    def setCommand(self, command):
        self.XWidget().command = command

    def resetCommand(self):
        self.XWidget().resetCommand()

    def getWinIdParam(self):
        return self.XWidget().winIdParam

    def setWinIdParam(self, winIdParam):
        self.XWidget().winIdParam = winIdParam

    def resetWinIdParam(self):
        self.XWidget().resetWinIdParam()

    def setExtraParams(self, params):
        self.XWidget().extraParams = params

    def getExtraParams(self):
        return self.XWidget().extraParams

    def resetExtraParams(self):
        self.XWidget().resetExtraParams()

    def setAutoRestart(self, yesno):
        self.XWidget().autoRestart = yesno

    def getAutoRestart(self):
        return self.XWidget().autoRestart

    def resetAutoRestart(self):
        self.XWidget().resetAutoRestart()
            
    command = Qt.Property(str, getCommand, setCommand, resetCommand)

    winIdParam = Qt.Property(str, getWinIdParam, setWinIdParam,
                                 resetWinIdParam)

    extraParams = Qt.Property(str, getExtraParams, setExtraParams,
                              resetExtraParams)

    autoRestart = Qt.Property(bool, getAutoRestart, setAutoRestart,
                              resetAutoRestart)


def main():
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication([])
    w = XCommandWidget()
    w.setFixedSize(800, 600)
    w.command = 'xterm'
    w.winIdParam = '-into'
    w.show()
    w.start()
    app.exec_()

if __name__ == "__main__":
    main()
