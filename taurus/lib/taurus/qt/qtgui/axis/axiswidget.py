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

import json

from taurus import Attribute
from taurus.external.qt import Qt
from taurus.core import TaurusEventType
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.button import TaurusCommandToolButton
from taurus.qt.qtgui.input import TaurusValueSpinBox
from taurus.qt.qtgui.compact import TaurusReadWriteSwitcher
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.resource import getIcon


class RWWidget(TaurusReadWriteSwitcher):

    exitEditTriggers = list(TaurusReadWriteSwitcher.exitEditTriggers)
    exitEditTriggers.append('editingFinished()')

    _DefaultReadOnly = False

    def __init__(self, *args, **kwargs):
        self.readOnly = self._DefaultReadOnly
        TaurusReadWriteSwitcher.__init__(self, *args, **kwargs)

    def enterEdit(self, *args, **kwargs):
        if self.readOnly:
            return
        return TaurusReadWriteSwitcher.enterEdit(self, *args, **kwargs)


class QStep(Qt.QObject):

    def __init__(self, step, parent=None):
        Qt.QObject.__init__(self, parent)
        self.size = None
        self.label = None
        self.setStep(step)

    def setStep(self, step):
        if isinstance(step, (list, tuple)):
            lstep = len(step)
            if lstep == 0:
                raise ValueError("Invalid step value")
            size = step[0]
            if lstep == 1:
                label = str(size)
            else:
                label = step[1]
        elif isinstance(step, dict):
            size = step['size']
            label = step.get('label', str(size))
        else:
            size = step
            label = str(step)

        self.size = size
        self.label = label

    def __cmp__(self, other):
        return cmp(self.size, other.size)

    def __str__(self):
        obj = dict(label=unicode(self.label), size=self.size)
        return json.dumps(obj)


@UILoadable(with_ui='ui')
class AxisWidget(TaurusWidget):

    _DefaultStepButtonOrientation = Qt.Qt.Horizontal

    stepSizeChanged = Qt.Signal(float, str)
    
    def __init__(self, parent=None, designMode=False):
        self.__customLabel = None
        self.__stepButtonOrientation = self._DefaultStepButtonOrientation
        TaurusWidget.__init__(self, parent)
        self.loadUi()
        ui = self.ui

        # initialize read/write position widgets
        ui.positionLabel = TaurusLabel(designMode=designMode)
        ui.positionLabel.setAutoTooltip(False)

        ui.positionEdit = TaurusValueSpinBox(designMode=designMode)
        ui.positionEdit.setAutoTooltip(False)
        
        exitEditTriggers = list(TaurusReadWriteSwitcher.exitEditTriggers)
        exitEditTriggers.append('editingFinished()')
        ui.readWriteWidget = RWWidget(designMode=designMode)
        ui.readWriteWidget.setReadWidget(ui.positionLabel)
        ui.readWriteWidget.setWriteWidget(ui.positionEdit)
        ui.readWritePanel.layout().addWidget(ui.readWriteWidget)

        # initialize step buttton panel with step up and step down buttons
        stepButtonPanelLayout = Qt.QBoxLayout(Qt.QBoxLayout.LeftToRight,
                                              ui.stepButtonPanel)
        stepButtonPanelLayout.setContentsMargins(0, 0, 0, 0)
        stepButtonPanelLayout.setSpacing(0)
        ui.stepDownButton = TaurusCommandToolButton()
        ui.stepDownButton.setAutoTooltip(False)
        ui.stepDownButton.setAutoRaise(True)
        ui.stepDownButton.setObjectName("StepDownButton")
        ui.stepDownButton.setCommand("StepDown")
        policy = ui.stepDownButton.sizePolicy()
        policy.setVerticalPolicy(Qt.QSizePolicy.Minimum)
        ui.stepDownButton.setSizePolicy(policy)
        ui.stepUpButton = TaurusCommandToolButton()
        ui.stepUpButton.setAutoTooltip(False)        
        ui.stepUpButton.setAutoRaise(True)
        ui.stepUpButton.setObjectName("StepUpButton")        
        ui.stepUpButton.setCommand("StepUp")
        policy = ui.stepUpButton.sizePolicy()
        policy.setVerticalPolicy(Qt.QSizePolicy.Minimum)
        ui.stepUpButton.setSizePolicy(policy)        
        stepButtonPanelLayout.addWidget(ui.stepDownButton)
        stepButtonPanelLayout.addWidget(ui.stepUpButton)        
        self.setAutoTooltip(False)

        self.stepSizeChanged.connect(self.__handleStepSizeChanged)

        # build steps menu
        ui.stepMenuToolButton.setIcon(getIcon(":/step.png"))
        ui.stepMenu = Qt.QMenu()
        ui.stepMenuToolButton.setMenu(ui.stepMenu)
        ui.stepActionGroup = Qt.QActionGroup(ui.stepMenu)
        ui.stepActionGroup.setExclusive(True)
        ui.stepActionGroup.triggered.connect(self.__onStepSizeChangedByUI)
        
        self.__updateStepButtonPanel()
        
    def __updateStepButtonPanel(self):
        # update the step button panel according to the orientation
        # (horizontal/vertical step down/up buttons)
        ui = self.ui
        layout = ui.stepButtonPanel.layout()
        orientation = self.__stepButtonOrientation
        if orientation == Qt.Qt.Horizontal:
            direction = Qt.QBoxLayout.LeftToRight
            ui.stepDownButton.setArrowType(Qt.Qt.LeftArrow)
            ui.stepDownButton.setIconSize(Qt.QSize(16, 16))
            ui.stepUpButton.setArrowType(Qt.Qt.RightArrow)
            ui.stepUpButton.setIconSize(Qt.QSize(16, 16))
        else:
            direction = Qt.QBoxLayout.BottomToTop
            ui.stepDownButton.setArrowType(Qt.Qt.DownArrow)
            ui.stepDownButton.setIconSize(Qt.QSize(8, 6))            
            ui.stepUpButton.setArrowType(Qt.Qt.UpArrow)
            ui.stepUpButton.setIconSize(Qt.QSize(8, 6))            
        layout.setDirection(direction)

    def __addStep(self, qstep):
        if not isinstance(qstep, QStep):
            qstep = QStep(qstep, self)

        # if step exists return the corresponding action
        for action in self.ui.stepActionGroup.actions():
            step = Qt.from_qvariant(action.data())
            if step.size == qstep.size:
                return action

        # create a new action for the step and add it to the menu
        action = self.ui.stepActionGroup.addAction(qstep.label)
        action.setData(qstep)
        action.setCheckable(True)
        self.ui.stepMenu.addAction(action)

        # re-order actions is the step group
        actions = self.ui.stepActionGroup.actions()
        steps = {}
        for action in actions:
            step = Qt.from_qvariant(action.data())
            steps[step] = action
            self.ui.stepActionGroup.removeAction(action)
        for step in sorted(steps):
            action = steps[step]
            self.ui.stepActionGroup.addAction(action)
        
        return action
            
    def __onStepSizeChangedByUI(self, action):
        qstep = Qt.from_qvariant(action.data())
        self.getModelObj().getAttribute("StepSize").write(qstep.size)
        
    def __onStepSizeChanged(self, evt_src, evt_type, evt_value):
        if evt_type in (TaurusEventType.Error, TaurusEventType.Config):
            return
        unit = evt_src.getUnit()
        step_size = evt_value.value
        if "no unit" in unit.lower():
            step_label = "{0}".format(step_size)
        else:
            step_label = "{0} {1}".format(step_size, unit)
        self.stepSizeChanged.emit(step_size, step_label)

    def __handleStepSizeChanged(self, step_size, step_label):
        action = self.__addStep((step_size, step_label))
        step = Qt.from_qvariant(action.data())
        action.setChecked(True)
        ui = self.ui
        ui.positionEdit.setSingleStep(step.size)
        self.__updateToolTips()
        
    def __getModelLabel(self):
        model = self.getModelObj()
        if model is None:
            modelLabel = ""
        else:
            modelLabel = model.getSimpleName()
        return modelLabel
        
    def __getAxisLabel(self):        
        customLabel = self.__customLabel
        if customLabel is None:
            model = self.getModelObj()
            if model is None:
                customLabel = self.getNoneValue()
            else:
                customLabel = model.getSimpleName() + ":"
        return customLabel

    def __updateToolTips(self):
        ui = self.ui
        label = self.__getModelLabel()
        readOnly = self.getReadOnly()
        action = self.ui.stepActionGroup.checkedAction()
        stepLabel = Qt.from_qvariant(action.data()).label
        toolTip = "Move {0} down by {1}".format(label, stepLabel)
        ui.stepDownButton.setToolTip(toolTip)
        toolTip = "Move {0} up by {1}".format(label, stepLabel)
        ui.stepUpButton.setToolTip(toolTip)
        toolTip = "Step size selection (current value: {0})".format(stepLabel)
        ui.stepMenuToolButton.setToolTip(toolTip)
        toolTip = "{0} current position".format(label)
        if not readOnly:
            toolTip += " (double click to set new position)"
        ui.readWritePanel.setToolTip(toolTip)

    def setModel(self, model_name):
        TaurusWidget.setModel(self, model_name)
        self.ui.readWriteWidget.setModel(model_name + "/Position")
        self.ui.stepDownButton.setModel(model_name)
        self.ui.stepUpButton.setModel(model_name)

        stepSize = Attribute(model_name + "/StepSize")
        stepSize.addListener(self.__onStepSizeChanged)

        self.ui.axisLabel.setText(self.__getAxisLabel())
        self.__updateToolTips()
        
    def getCustomLabel(self):
        if self.__customLabel is None:
            return ""
        return self.__customLabel

    def setCustomLabel(self, label):
        self.__customLabel = label
        self.ui.axisLabel.setText(self.__getAxisLabel())
        self.__updateToolTips()
        
    def resetCustomLabel(self):
        self.setCustomLabel(None)

    customLabel = Qt.Property(str, getCustomLabel, setCustomLabel,
                              resetCustomLabel)

    def getReadOnly(self):
        return self.ui.readWriteWidget.readOnly

    def setReadOnly(self, readOnly):
        self.ui.readWriteWidget.readOnly = readOnly
        self.ui.stepPanel.setVisible(not readOnly)
        self.__updateToolTips()

    def resetReadOnly(self):
        self.setReadOnly(self.ui.readWriteWidget._DefaultReadOnly)

    readOnly = Qt.Property(bool, getReadOnly, setReadOnly, resetReadOnly)

    def getSteps(self):
        result = []
        for action in self.ui.stepActionGroup.actions():
            qstep = Qt.from_qvariant(action.data())
            result.append(str(qstep))
        return result

    def setSteps(self, steps):
        for step in steps:
            if isinstance(step, Qt.QString): # happens in the QtDesigner
                step = unicode(step)
            try:
                step = json.loads(step)
            except TypeError:
                pass
            self.__addStep(step)
            
    steps = Qt.Property("QStringList", getSteps, setSteps)

    def getStepButtonPanelOrientation(self):
        return self.__stepButtonOrientation

    def setStepButtonPanelOrientation(self, orientation):
        self.__stepButtonOrientation = orientation
        self.__updateStepButtonPanel()

    def resetStepButtonPanelOrientation(self):
        self.setStepButtonPanelOrientation(self._DefaultStepButtonOrientation)

    stepButtonPanelOrientation = Qt.Property("Qt::Orientation",
                                             getStepButtonPanelOrientation,
                                             setStepButtonPanelOrientation,
                                             resetStepButtonPanelOrientation)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.axis",
                    icon=":designer/extra_motor.png",
                    group="Taurus Axis")


def main():
    import sys
    from taurus.core.util.argparse import get_taurus_parser
    from taurus.qt.qtgui.application import TaurusApplication
    
    parser = get_taurus_parser()
    parser.usage = "%prog [options] <axis_name(s)>"
    app = TaurusApplication(sys.argv, cmd_line_parser=parser, 
                            app_name="Axis", app_version="1.0",
                            org_domain="Taurus",
                            org_name="Taurus community")
        
    args = app.get_command_line_args()

    window = Qt.QWidget()
    layout = Qt.QVBoxLayout(window)
    layout.setContentsMargins(3, 3, 3, 3)
    layout.setSpacing(2)
    defaultSteps = [(0.01, "10 um"), (0.1, "100 um"), (1.0, "1 mm"),
                    (10.0, "10 mm"), (100.0, "100 mm")]
    for motor in args:
        # "default" motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setModel(motor)
        layout.addWidget(axis)

        # vertical step buttons, motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setModel(motor)
        axis.setStepButtonPanelOrientation(Qt.Qt.Vertical)
        layout.addWidget(axis)

        # read-only, custom label, motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setModel(motor)
        axis.setReadOnly(True)        
        axis.setCustomLabel("= {0} =".format(motor))
        layout.addWidget(axis)        

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
