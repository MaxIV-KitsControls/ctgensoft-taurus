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
## GNU Lesser Generalgit status Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module provides a taurus QToolButton based widgets"""

__all__ = ["TaurusCommandToolButton"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseCommandWidget
            
    
class TaurusCommandToolButton(Qt.QToolButton, TaurusBaseCommandWidget):
    """
    This class provides a tool button that executes a tango command on its device.
    
    Code examples::
        from taurus.qt.qtgui.button import TaurusCommandToolButton
        from taurus.qt.qtgui.resource import getThemeIcon
    
        # a button that executes the "DevVoid" command for the 'sys/tg_test/1'
        # device in an asynchronous way
        button =  TaurusCommandToolButton()
        button.setModel('sys/tg_test/1')
        button.setCommand("DevVoid")
        button.setIcon(getThemeIcon("folder-open")

        # a button that executes the "DevString" command for the 'sys/tg_test/1'
        # device in an asynchronous way with one parameter.
        # The command returns a string. A slot is created to be called when the
        # command termintes with the result
        # The default text (the command name) is overwritten by a custom string    
        button = TaurusCommandToolButton()
        button.setModel('sys/tg_test/1')
        button.setCommand("DevString")
        button.setArguments(["something"])
        button.setCustomText("Go!")    

        def result(value, error):
            print "DevString command finished with result={0} and error={1}".format(value, error)

        button.commandFinished.connect(result)
    """

    commandFinished = Qt.Signal(object, bool)
    
    def __init__(self, parent=None, designMode=False):
        Qt.QToolButton.__init__(self, parent)
        name = self.__class__.__name__
        TaurusBaseCommandWidget.__init__(self, name,
                                         designMode=designMode)
        self.clicked.connect(self.executeCommand)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        info = TaurusBaseCommandWidget.getQtDesignerPluginInfo()
        info["group"] = "Taurus Buttons"
        info["icon"] = ":/designer/toolbutton.png"
        info["module"] = "taurus.qt.qtgui.button"
        return info
    
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #                      Qt Properties                        #
    ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    asynchronous = Qt.Property(bool, TaurusBaseCommandWidget.getAsynchronous,
                               TaurusBaseCommandWidget.setAsynchronous,
                               TaurusBaseCommandWidget.resetAsynchronous)
    
    model = Qt.Property(str, TaurusBaseCommandWidget.getModel,
                        TaurusBaseCommandWidget.setModel,
                        TaurusBaseCommandWidget.resetModel)
    
    useParentModel = Qt.Property(bool, TaurusBaseCommandWidget.getUseParentModel,
                                 TaurusBaseCommandWidget.setUseParentModel,
                                 TaurusBaseCommandWidget.resetUseParentModel)
    
    command = Qt.Property(str, TaurusBaseCommandWidget.getCommand,
                          TaurusBaseCommandWidget.setCommand,
                          TaurusBaseCommandWidget.resetCommand)

    timeout = Qt.Property(float, TaurusBaseCommandWidget.getTimeout,
                          TaurusBaseCommandWidget.setTimeout,
                          TaurusBaseCommandWidget.resetTimeout)
    
    dangerMessage = Qt.Property(str, TaurusBaseCommandWidget.getDangerMessage,
                                TaurusBaseCommandWidget.setDangerMessage,
                                TaurusBaseCommandWidget.resetDangerMessage)

    autoToolTip = Qt.Property(bool, TaurusBaseCommandWidget.getAutoTooltip,
                              TaurusBaseCommandWidget.setAutoTooltip)

    customText = Qt.Property(str, TaurusBaseCommandWidget.getCustomText,
                             TaurusBaseCommandWidget.setCustomText,
                             TaurusBaseCommandWidget.resetCustomText)


def main():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.resource import getThemeIcon
    
    app = TaurusApplication([])
    window = Qt.QWidget()
    layout = Qt.QVBoxLayout(window)

    tool_button_1 = TaurusCommandToolButton()
    tool_button_1.setCommand("DevString")
    tool_button_1.setCustomText("Go DevString Asynch")
    tool_button_1.setModel("sys/tg_test/1")
    tool_button_1.setArguments(["DevString executed asynchronously"])
    tool_button_1.setIcon(getThemeIcon('network-wired'))
    tool_button_1.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)    
    layout.addWidget(tool_button_1)

    tool_button_2 = TaurusCommandToolButton()
    tool_button_2.setCommand("DevString")
    tool_button_2.setCustomText("Go DevString Synch")
    tool_button_2.setAsynchronous(False)
    tool_button_2.setModel("sys/tg_test/1")
    tool_button_2.setArguments(["DevString executed synchronously"])    
    tool_button_2.setIcon(getThemeIcon('network-wireless'))
    tool_button_2.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
    layout.addWidget(tool_button_2)

    result_widget = Qt.QPlainTextEdit()
    layout.addWidget(result_widget)

    def result_callback(value, error):
        result_widget.appendPlainText("Result: {0}, error={1}".format(value, error))
    tool_button_1.commandFinished.connect(result_callback)
    tool_button_2.commandFinished.connect(result_callback)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
