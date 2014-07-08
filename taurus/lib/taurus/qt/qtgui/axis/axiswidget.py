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

import weakref

from taurus import Attribute
from taurus.external.qt import Qt
from taurus.core import TaurusEventType
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.button import TaurusCommandToolButton
from taurus.qt.qtgui.input import TaurusValueSpinBox
from taurus.qt.qtgui.compact import TaurusReadWriteSwitcher
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.resource import getIcon


__height_hint = None
def get_height_hint():
    """Little trick to get a uniform height hint between all widgets"""
    global __height_hint
    if __height_hint is None:
        h1 = Qt.QComboBox().sizeHint().height()
        h2 = Qt.QLineEdit().sizeHint().height()
        h3 = Qt.QDoubleSpinBox().sizeHint().height()
        h4 = Qt.QPushButton().sizeHint().height()
        __height_hint = min(h1, h2, h3, h4)
    return __height_hint


__minimum_height_hint = None
def get_minimum_height_hint():
    """Little trick to get a uniform height hint between all widgets"""
    global __minimum_height_hint
    if __minimum_height_hint is None:
        h1 = Qt.QComboBox().minimumSizeHint().height()
        h2 = Qt.QLineEdit().minimumSizeHint().height()
        h3 = Qt.QDoubleSpinBox().minimumSizeHint().height()
        h4 = Qt.QPushButton().minimumSizeHint().height()
        __minimum_height_hint = min(h1, h2, h3, h4)
    return __minimum_height_hint


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
        self.icon = None
        self.setStep(step)

    def setStep(self, step):
        icon = getIcon(":/step.png")
        if isinstance(step, (list, tuple)):
            lstep = len(step)
            if lstep == 0:
                raise ValueError("Invalid step value")
            step_size = step[0]
            if lstep == 1:
                step_label = self.__toLabel(step_size)
            else:
                step_label = step[1]
                if lstep > 2:
                    icon = step[2]
        elif isinstance(step, dict):
            step_size = step['size']
            step_label = step.get('label', str(step_size))
            icon = step.get('icon', icon)
        else:
            step_size = step
            step_label = str(step)
        if not isinstance(icon, Qt.QIcon):
            if not icon:
                icon = Qt.QIcon()
            else:
                icon = getIcon(icon)
                    
        self.size = step_size
        self.label = step_label
        self.icon = icon

    def __cmp__(self, other):
        return cmp(self.size, other.size)
    

class StepSizeComboBox(Qt.QComboBox, TaurusBaseWidget):

    def __init__(self, parent=None):
        Qt.QComboBox.__init__(self, parent)
        TaurusBaseWidget.__init__(self, self.__class__.__name__)
        self.activated[int].connect(self.__onUserSelection)

    def __onUserSelection(self, index):
        step_size = self.itemData(index)
        self.getModelObj().write(step_size)
        
    def __getUnit(self):
        model = self.getModelObj()
        if model is None:
            return ""
        unit = model.getUnit()
        if "no unit" in unit.lower():
            unit = ""
        return unit

    def __toLabel(self, step):
        unit = self.__getUnit()
        if unit:
            return "{0} {1}".format(step, unit)
        else:
            return "{0}".format(step)
    
    def addStep(self, step):
        icon = getIcon(":/step.png") #getIcon(":/actions/arrange-boxes.svg")
        if isinstance(step, (list, tuple)):
            lstep = len(step)
            if lstep == 0:
                raise ValueError("Invalid step value")
            step_size = step[0]
            if lstep == 1:
                step_label = self.__toLabel(step_size)
            else:
                step_label = step[1]
                if lstep > 2:
                    icon = step[2]
        elif isinstance(step, dict):
            step_size = step['size']
            step_label = step.get('label', str(step_size))
            icon = step.get('icon', icon)
        else:
            step_size = step
            step_label = str(step)
        if not isinstance(icon, Qt.QIcon):
            icon = getIcon(icon)        
        self.addItem(icon, step_label, step_size)

    def addSteps(self, steps):
        for step in steps:
            self.addStep(step)

    def setSteps(self, steps):
        self.clear()
        if steps is None:
            steps = []
        self.addSteps(steps)

    def setCurrentStep(self, step):
        index = self.findData(step, Qt.Qt.UserRole)
        self.setCurrentIndex(index)

    def sizeHint(self):
        size = Qt.QComboBox.sizeHint(self)
        size = Qt.QSize(size.width(), get_height_hint())
        return size

    def minimumSizeHint(self):
        size = Qt.QComboBox.minimumSizeHint(self)
        size = Qt.QSize(size.width(), get_minimum_height_hint())
        return size

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Error:
            self.setCurrentIndex(-1)
        elif evt_type == TaurusEventType.Config:
            return
        else:
            step_size = evt_value.value
            index = self.findData(step_size, Qt.Qt.UserRole)
            if index == -1:
                self.addStep(step_size)
            self.setCurrentIndex(self.findData(step_size, Qt.Qt.UserRole))

    def setModel(self, model):
        if isinstance(model, Qt.QAbstractItemModel):
            Qt.QComboBox.setModel(self, model)
        else:
            TaurusBaseWidget.setModel(self, model)

    
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
        #ui.stepSizeWidget.currentIndexChanged[int].connect(self.__onStepSizeChanged)

        # build steps menu
        ui.stepMenuToolButton.setIcon(getIcon(":/step.png"))
        ui.stepMenu = Qt.QMenu()
        ui.stepMenuToolButton.setMenu(ui.stepMenu)
        ui.stepActionGroup = Qt.QActionGroup(ui.stepMenu)
        ui.stepActionGroup.setExclusive(True)
        ui.stepActionGroup.triggered.connect(self.__onStepSizeChangedByUI)
        
        self.__updateStepButtonPanel()
        
    def __updateStepButtonPanel(self):
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
            ui.stepDownButton.setIconSize(Qt.QSize(8, 8))            
            ui.stepUpButton.setArrowType(Qt.Qt.UpArrow)
            ui.stepUpButton.setIconSize(Qt.QSize(8, 8))            
        layout.setDirection(direction)

    def __getSteps(self):
        return [action.data() for action in self.ui.stepActionGroup.actions()]
        
    def __addStep(self, qstep):
        if not isinstance(qstep, QStep):
            qstep = QStep(qstep, self)
        for action in self.ui.stepActionGroup.actions():
            if action.data().size == qstep.size:
                return action

        action = self.ui.stepActionGroup.addAction(qstep.label)
        action.setData(qstep)
        action.setCheckable(True)
        self.ui.stepMenu.addAction(action)

        # re-order actions
        actions = self.ui.stepActionGroup.actions()
        steps = {}
        for action in actions:
            steps[action.data()] = action
            self.ui.stepActionGroup.removeAction(action)
        for step in sorted(steps):
            action = steps[step]
            self.ui.stepActionGroup.addAction(action)
        
        return action
            
    def __onStepSizeChangedByUI(self, action):
        self.getModelObj().getAttribute("StepSize").write(action.data().size)
        
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
        step = action.data()
        action.setChecked(True)
        ui = self.ui
        ui.positionEdit.setSingleStep(step.size)
        slabel, mlabel = step.label, self.__getModelLabel()
        toolTip = "Move {0} down by {1}".format(mlabel, slabel)
        ui.stepDownButton.setToolTip(toolTip)
        toolTip = "Move {0} up by {1}".format(mlabel, slabel)        
        ui.stepUpButton.setToolTip(toolTip)
        toolTip = "Step size selection (current value: {0})".format(slabel)
        ui.stepMenuToolButton.setToolTip(toolTip)
        
    def __getModelLabel(self):
        model = self.getModelObj()
        if model is None:
            modelLabel = ""
        else:
            modelLabel = model.getSimpleName()
        return modelLabel
        
    def __getCustomLabel(self):        
        customLabel = self.__customLabel
        if customLabel is None:
            model = self.getModelObj()
            if model is None:
                customLabel = self.getNoneValue()
            else:
                customLabel = model.getSimpleName() + ":"
        return customLabel

    def __updateCustomLabel(self):
        self.ui.axisLabel.setText(self.__getCustomLabel())

    def __updateReadOnly(self):
        ui = self.ui
        readOnly = ui.readWriteWidget.readOnly
        ui.stepPanel.setVisible(not readOnly)

    def setModel(self, model_name):
        TaurusWidget.setModel(self, model_name)
        ui = self.ui
        ui.readWriteWidget.setModel(model_name + "/Position")
        ui.stepDownButton.setModel(model_name)
        ui.stepUpButton.setModel(model_name)

        stepSize = Attribute(model_name + "/StepSize")
        stepSize.addListener(self.__onStepSizeChanged)
        
        self.__updateCustomLabel()
        
    def getCustomLabel(self):
        if self.__customLabel is None:
            return ""
        return self.__customLabel

    def setCustomLabel(self, label):
        self.__customLabel = label
        self.__updateCustomLabel()

    def resetCustomLabel(self):
        self.setCustomLabel(None)

    customLabel = Qt.Property(str, getCustomLabel, setCustomLabel,
                              resetCustomLabel)

    def getReadOnly(self):
        return self.ui.readWriteWidget.readOnly

    def setReadOnly(self, readOnly):
        self.ui.readWriteWidget.readOnly = readOnly
        self.__updateReadOnly()

    def resetReadOnly(self):
        self.setReadOnly(self.ui.readWriteWidget._DefaultReadOnly)

    readOnly = Qt.Property(bool, getReadOnly, setReadOnly, resetReadOnly)

    def getSteps(self):
        return [action.data() for action in self.ui.stepActionGroup.actions()]

    def setSteps(self, steps):
        for step in steps:
            self.__addStep(step)
            
    steps = Qt.Property(list, getSteps, setSteps, designable=False)

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

        # vertical step buttons, custom label, motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setModel(motor)
        axis.setStepButtonPanelOrientation(Qt.Qt.Vertical)
        axis.setCustomLabel("= {0} =".format(motor))
        layout.addWidget(axis)

        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setModel(motor)
        axis.setReadOnly(True)        
        layout.addWidget(axis)        

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
