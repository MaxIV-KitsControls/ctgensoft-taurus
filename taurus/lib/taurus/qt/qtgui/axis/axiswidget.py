# -*- coding: utf-8 -*-

##############################################################################
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
##############################################################################

"""
This package contains a collection of Qt based widgets designed to control
axis based elements (motors)
"""

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.input import TaurusValueSpinBox
from taurus.qt.qtgui.compact import TaurusReadWriteSwitcher
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.resource import getIcon


@UILoadable(with_ui='ui')
class AxisWidget(TaurusWidget):
    
    def __init__(self, parent=None):
        self.__customLabel = None
        TaurusWidget.__init__(self, parent)
        self.loadUi()
        ui = self.ui
        ui.positionLabel = TaurusLabel()
        ui.positionSpinBox = TaurusValueSpinBox()
        exitEditTriggers = list(TaurusReadWriteSwitcher.exitEditTriggers)
        exitEditTriggers.append('editingFinished()')
        ui.readWriteWidget = TaurusReadWriteSwitcher(exitEditTriggers=exitEditTriggers)
        ui.readWriteWidget.setReadWidget(ui.positionLabel)
        ui.readWriteWidget.setWriteWidget(ui.positionSpinBox)
        ui.readWritePanel.layout().addWidget(ui.readWriteWidget)
        downIcon = getIcon(":/actions/media_playback_backward.svg")
        if not downIcon.isNull():
            ui.stepDownButton.setIcon(downIcon)
        else:
            ui.stepDownButton.setArrowType(Qt.Qt.LeftArrow)
        upIcon = getIcon(":/actions/media_playback_start.svg")        
        if not upIcon.isNull():
            ui.stepUpButton.setIcon(upIcon)
        else:
            ui.stepUpButton.setArrowType(Qt.Qt.RightArrow)
                                
    def setModel(self, model_name):
        TaurusWidget.setModel(self, model_name)
        ui = self.ui
        ui.readWriteWidget.setModel(model_name + "/Position")
        ui.stepDownButton.setModel(model_name)
        ui.stepUpButton.setModel(model_name)
        self.__updateCustomLabel()

    def __updateCustomLabel(self):
        customLabel = self.__customLabel
        if customLabel is None:
            model = self.getModelObj()
            if model is None:
                customLabel = "-----"
            else:
                customLabel = model.getSimpleName() + ":"
        self.ui.axisLabel.setText(customLabel)
        
    def setCustomLabel(self, label):
        self.__customLabel = label
        self.__updateCustomLabel()

    def getCustomLabel(self):
        return self.__customLabel

    def resetCustomLabel(self):
        self.setCustomLabel(None)
    
    customLabel = Qt.Property(str, getCustomLabel, setCustomLabel,
                              resetCustomLabel)


def main():
    import sys
    from taurus.core.util.argparse import get_taurus_parser
    from taurus.qt.qtgui.application import TaurusApplication
    
    parser = get_taurus_parser()
    parser.usage = "%prog [options] <axis_name(s)>"
    app = TaurusApplication(sys.argv, cmd_line_parser=parser, 
                            app_name="Axis", app_version="1.0",
                            org_domain="Taurus", org_name="Tango community")
        
    args = app.get_command_line_args()

    window = Qt.QMainWindow()
    panel = Qt.QWidget()
    layout = Qt.QVBoxLayout(panel)
    for motor in args:
        axis = AxisWidget()
        axis.setModel(motor)
        layout.addWidget(axis)

    window.setCentralWidget(panel)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
