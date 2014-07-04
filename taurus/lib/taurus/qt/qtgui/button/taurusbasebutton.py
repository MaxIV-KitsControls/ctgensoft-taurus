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

"""This module provides a taurus command base class to be used in qt buttons"""

__all__ = ["TaurusBaseCommandWidget"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.dialog import TaurusMessageBox
from taurus.qt.qtgui.base import TaurusBaseWidget
            

class TaurusBaseCommandWidget(TaurusBaseWidget):
    """
    Base class for taurus widgets command based widget buttons
    """
    
    _DefaultAsynchronous = True
    
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self.__asynchronous = self._DefaultAsynchronous
        self.__command = None
        self.__customText = None
        self.__timeout = None
        self.__args = ()
        self.__kwargs = {}
        TaurusBaseWidget.__init__(self, name, parent=parent, designMode=designMode)

    def _executeCommand(self):
        """
        Executes the active command on the registered model. If widget is in
        asynchronous mode, the method returns None.
        If in synchronous mode the method will execute the command and block
        until it finishes. It returns the result in 
        """
        if self.__command is None:
            raise ValueError("No command has been specified")
        model = self.getModelObj()
        if model is None:
            raise ValueError("No model has been connected")
        result = model.command(self.__command, args=self.__args,
                               kwargs=self.__kwargs, asynch=self.__asynchronous,
                               callback=self.__onCommandFinished,
                               timeout=self.__timeout)
        return result

    def executeCommand(self):
        if self.isDangerous() and not self.getForceDangerousOperations():
            result = Qt.QMessageBox.question(self,
                "Potentially dangerous action",
                "{0}\nProceed?".format(self.getDangerMessage()),
                Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel, Qt.QMessageBox.Ok)
            if result != Qt.QMessageBox.Ok:
                return
        try:
            self._executeCommand()
        except:
            import sys
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.setWindowTitle("Unhandled exception running command")
            msgbox.exec_()
        
    def __onCommandFinished(self, result, error=False):
        self.commandFinished.emit(result, error)
    
    def setAsynchronous(self, asynchronous):
        self.__asynchronous = asynchronous

    def getAsynchronous(self):
        return self.__asynchronous

    def resetAsynchronous(self):
        self.setAsynchronous(self._DefaultAsynchronous)

    def __updateText(self):
        self.setText(self.getDisplayValue())

    def getDisplayValue(self, cache=True):
        text = self.__customText
        if text is None:
            text = self.__command
        if text is None:
            text = ""
        return text
                
    def setCommand(self, command):
        """
        Sets the command to be executed when the button is clicked
        
        :param command: (str or None) the command name
        """
        self.__command = command
        self.__updateText()
    
    def getCommand(self):
        """
        Returns the command name to be executed when the button is clicked
        
        :return: (str or None) the command name
        """
        return self.__command
    
    def resetCommand(self):
        '''equivalent to self.setCommand(None)'''
        self.setCommand(None)

    def setCustomText(self, customText):
        """
        Sets the widget customText. If set to None, the widget will use the
        command name as text
        
        :param customText: (str or None) the custom text
        """
        self.__customText = customText
        self.__updateText()        
    
    def getCustomText(self):
        """
        Returns the customText name to be executed when the button is clicked
        
        :return: (str or None) the customText name
        """
        return self.__customText
    
    def resetCustomText(self):
        '''equivalent to self.setCustomText(None)'''
        self.setCustomText(None)
        
    def setTimeout(self, timeout):
        """
        Sets the timeout to be used when the command is executed
        
        :param timeout: (float or None) the timeout name
        """
        self.__timeout = timeout
    
    def getTimeout(self):
        """
        Returns the timeout name to be used when the command is executed
        
        :return: (str or None) the timeout name
        """
        return self.__timeout
    
    def resetTimeout(self):
        '''equivalent to self.setTimeout(None)'''
        self.setTimeout(None)
        
    def setArguments(self, arguments):
        """
        Sets the arguments to be passed to the command when it is executed
        
        :param arguments: sequence of arguments
        """
        self.__args = arguments
    
    def getArguments(self):
        """
        Returns the arguments to be passed to the command when it is executed
        
        :return: (sequence) a sequence of arguments
        """
        return self.__args
    
    def resetArguments(self):
        """
        Resets the command arguments to an empty sequence
        """
        self.setArguments(())

    def setKeywordArguments(self, arguments):
        """
        Sets the keyword arguments to be passed to the command when it
        is executed
        
        :param arguments: dictionary of arguments
        """
        self.__kwargs = arguments
    
    def getKeywordArguments(self):
        """
        Returns the keywordarguments to be passed to the command when
        it is executed
        
        :return: (dict) a dictionary of keyword arguments
        """
        return self.__kwargs
    
    def resetKeywordArguments(self):
        """
        Resets the command keyword arguments to an empty dictionary
        """
        self.setKeywordArguments({})

    @classmethod
    def getQtDesignerPluginInfo(cls):
        info = TaurusBaseWidget.getQtDesignerPluginInfo()
        info["group"] = "Taurus Buttons"
        info["icon"] = ":/designer/pushbutton.png"
        info["module"] = "taurus.qt.qtgui.button"
        return info
