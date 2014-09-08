# -*- coding: utf-8 -*-
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright (c) 2014 European Synchrotron Radiation Facility, Grenoble, France
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

"""A collection of useful taurus Qt actions"""

__all__ = ["TaurusCommandAction"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseCommandComponent


class TaurusCommandAction(Qt.QAction, TaurusBaseCommandComponent):

    commandFinished = Qt.Signal(object, bool)

    def __init__(self, parent=None):
        Qt.QAction.__init__(self, parent)
        name = self.__class__.__name__
        TaurusBaseCommandComponent.__init__(self, name)
        self.triggered.connect(self.executeCommand)

    # Qt Properties

    asynchronous = Qt.Property(bool, TaurusBaseCommandComponent.getAsynchronous,
                               TaurusBaseCommandComponent.setAsynchronous,
                               TaurusBaseCommandComponent.resetAsynchronous)

    model = Qt.Property(str, TaurusBaseCommandComponent.getModel,
                        TaurusBaseCommandComponent.setModel,
                        TaurusBaseCommandComponent.resetModel)

    useParentModel = Qt.Property(bool, TaurusBaseCommandComponent.getUseParentModel,
                                 TaurusBaseCommandComponent.setUseParentModel,
                                 TaurusBaseCommandComponent.resetUseParentModel)

    command = Qt.Property(str, TaurusBaseCommandComponent.getCommand,
                          TaurusBaseCommandComponent.setCommand,
                          TaurusBaseCommandComponent.resetCommand)

    timeout = Qt.Property(float, TaurusBaseCommandComponent.getTimeout,
                          TaurusBaseCommandComponent.setTimeout,
                          TaurusBaseCommandComponent.resetTimeout)

    dangerMessage = Qt.Property(str, TaurusBaseCommandComponent.getDangerMessage,
                                TaurusBaseCommandComponent.setDangerMessage,
                                TaurusBaseCommandComponent.resetDangerMessage)

#    autoToolTip = Qt.Property(bool, TaurusBaseCommandComponent.getAutoTooltip,
#                              TaurusBaseCommandComponent.setAutoTooltip)

    customText = Qt.Property(str, TaurusBaseCommandComponent.getCustomText,
                             TaurusBaseCommandComponent.setCustomText,
                             TaurusBaseCommandComponent.resetCustomText)
