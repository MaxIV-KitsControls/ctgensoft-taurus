#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

"""This module provides basic taurus scroll area widget"""

__all__ = ["TaurusScrollArea"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent

from taurusbasecontainer import TaurusBaseContainer


class TaurusScrollArea(Qt.QScrollArea, TaurusBaseContainer):
    """This is a Qt.QScrollArea that additionally accepts a model property.
    This type of taurus container classes are specially useful if you define
    a parent taurus model to them and set all contained taurus widgets to use parent
    model. Example::
    
        from taurus.qt.qtgui.container import *
        from taurus.qt.qtgui.display import *
        
        widget = TaurusScrollArea()
        layout = Qt.QVBoxLayout()
        widget.setLayout(layout)
        widget.model = 'sys/database/2'
        stateWidget = TaurusLabel()
        layout.addWidget(stateWidget)
        stateWidget.useParentModel = True
        stateWidget.model = '/state'"""
        
    __pyqtSignals__ = ("modelChanged(const QString &)",)
        
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QScrollArea, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pending operations related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getPendingOperations(self):
        widget = self.widget()
        if isinstance(widget, TaurusBaseComponent):
            return widget.getPendingOperations()
        return []
    
    def resetPendingOperations(self):
        self.debug("Reset changes")
        widget = self.widget()
        if isinstance(widget, TaurusBaseComponent):
            widget.resetPendingOperations()
    
    def hasPendingOperations(self):
        widget = self.widget()
        if isinstance(widget, TaurusBaseComponent):
            return widget.hasPendingOperations()
        return False
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("applyPendingChanges()")
    def applyPendingChanges(self):
        self.applyPendingOperations()
    
    @Qt.pyqtSignature("resetPendingChanges()")
    def resetPendingChanges(self):
        self.resetPendingOperations()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseContainer.getQtDesignerPluginInfo()
        if cls is TaurusScrollArea:
            ret['module'] = 'taurus.qt.qtgui.container'
            ret['group'] = 'Taurus Containers'
            ret['icon'] = ":/designer/scrollarea.png"
            ret['container'] = True
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    model = Qt.pyqtProperty("QString", TaurusBaseContainer.getModel, 
                                TaurusBaseContainer.setModel, 
                                TaurusBaseContainer.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusBaseContainer.getUseParentModel,
                                         TaurusBaseContainer.setUseParentModel,
                                         TaurusBaseContainer.resetUseParentModel)
    
    showQuality = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowQuality,
                                      TaurusBaseContainer.setShowQuality,
                                      TaurusBaseContainer.resetShowQuality)

def demo():
    "Scroll area"
    w = Qt.QWidget()
    w.setWindowTitle(Qt.QApplication.instance().applicationName())
    layout = Qt.QGridLayout()
    layout.setContentsMargins(0,0,0,0)
    w.setLayout(layout)
    groupbox = TaurusScrollArea()
    groupbox.model = "sys/tg_test/1"
    layout.addWidget(groupbox)
    layout = Qt.QFormLayout()
    groupbox.setLayout(layout)
    import taurus.qt.qtgui.display
    state_led = taurus.qt.qtgui.display.TaurusLed()
    state_led.useParentModel = True
    state_led.model = "/state"
    status_label = taurus.qt.qtgui.display.TaurusLabel()
    status_label.useParentModel = True
    status_label.model = "/status"
    double_scalar_label = taurus.qt.qtgui.display.TaurusLabel()
    double_scalar_label.useParentModel = True
    double_scalar_label.model = "/double_scalar"
    layout.addRow("State:", state_led)
    layout.addRow("Status:", status_label)
    layout.addRow("Double scalar:", double_scalar_label)
    w.show()
    return w

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_device_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Taurus frame demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
        
    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        models = map(str.lower, args)

        w = Qt.QWidget()
        w.setWindowTitle(app.applicationName())
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in models:
            groupbox = TaurusScrollArea()
            groupbox.model = model
            layout.addWidget(groupbox)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()