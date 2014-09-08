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

"""\
This module provides a command base class that can be used
in conjunction with any QObject (namely QWidget)
"""

__all__ = ["CommandMixin"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt


class CommandMixin(object):
    """
    Helper class for QObjects that execute commands
    (ex: QButtons, QActions).

    The QObject should implement the signal:
    ``commandExecuted(result<object>, error<bool>)``.
    This signal is emitted when the command finishes. The first
    parameter is the command result and the second is a boolean flag
    indicating if an error occured. If an error occurred, the result
    is the exception.
    """

    _DefaultAsynchronous = True

    def __init__(self):
        self.__asynchronous = self._DefaultAsynchronous
        self.__command = None
        self.__customText = None
        self.__timeout = None
        self.__args = ()
        self.__kwargs = {}

    def executeCommand(self):
        """
        Executes the active command on the registered model. If widget
        is in asynchronous mode, the method returns None. If in
        synchronous mode the method will execute the command, block
        until it finishes and return the result of the command
        execution. 
        """
        if self.__command is None:
            raise ValueError("No command has been specified")
        model = self.getModelObj()
        if model is None:
            raise ValueError("No model has been connected")
        result = model.command(self.__command, args=self.__args,
                               kwargs=self.__kwargs,
                               asynch=self.__asynchronous,
                               callback=self.__onCommandFinished,
                               timeout=self.__timeout)
        return result

    def __onCommandFinished(self, result, error=False):
        if hasattr(self, "commandFinished"):
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
        if self.__command is None:
            return ""
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
        if self.__customText is None:
            return ""
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
        if self.__timeout is None:
            return 0.0
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
