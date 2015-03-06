# -*- coding: utf-8 -*-
#
# This file is part of ESRF taurus widgets
# (http://gitlab.esrf.fr/taurus/taurus-esrf)
#
# Copyright (c) 2014 European Synchrotron Radiation Facility, Grenoble, France
#
# Distributed under the terms of the GNU Lesser General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#

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
from taurus.qt.qtgui.resource import getIcon, getThemeIcon


class RWWidget(TaurusReadWriteSwitcher):

    exitEditTriggers = list(TaurusReadWriteSwitcher.exitEditTriggers)
    exitEditTriggers.append('editingFinished()')

    _DefaultReadOnly = False

    def __init__(self, *args, **kwargs):
        self.readOnly = self._DefaultReadOnly
        TaurusReadWriteSwitcher.__init__(self, *args, **kwargs)
        layout = self.layout()
        layout.setContentsMargins(0, 0, 0, 0)

    def enterEdit(self, *args, **kwargs):
        if self.readOnly:
            return
        return TaurusReadWriteSwitcher.enterEdit(self, *args, **kwargs)

    def _updateSizePolicy(self):
        pass

class PositionSpinBox(TaurusValueSpinBox):
    pass


class PositionLabel(TaurusLabel):

    def __init__(self, *args, **kwargs):
        TaurusLabel.__init__(self, *args, **kwargs)
        self.setAutoTrim(False)

    def handleEvent(self, evt_src, evt_type, evt_value):
        TaurusLabel.handleEvent(self, evt_src, evt_type, evt_value)
        if evt_type == TaurusEventType.Config:
            units = self.getModelObj().getUnit()
            if units not in (None, "No unit"):
                self.setSuffixText(" " + units)


class ValueLabel(object):
    """
    An object representing a pair value and it's label (display representation).
    Can be used, for example to describe a position value=0.01, label="10 um".
    """
    def __init__(self, value):
        self.value = None
        self.label = None
        self.setValue(value)

    def setValue(self, in_value):
        if isinstance(in_value, (list, tuple)):
            lin_value = len(in_value)
            if lin_value == 0:
                raise ValueError("Invalid value")
            value = in_value[0]
            if lin_value == 1:
                label = str(value)
            else:
                label = in_value[1]
        elif isinstance(in_value, dict):
            value = in_value['value']
            label = in_value.get('label', str(value))
        else:
            value = in_value
            label = str(in_value)

        self.value = value
        self.label = label

    def __cmp__(self, other):
        return cmp(self.value, other.value)

    def __str__(self):
        obj = dict(label=unicode(self.label), value=self.value)
        return json.dumps(obj)


class Step(ValueLabel):

    def setStep(self, step):
        return self.setValue(step)

    @property
    def size(self):
        return self.value


class ReferencePoint(ValueLabel):

    def setReferencePoint(self, refpos):
        return self.setValue(refpos)

    @property
    def position(self):
        return self.value


@UILoadable(with_ui='ui')
class AxisWidget(TaurusWidget):
    """

    """

    _DefaultStepButtonOrientation = Qt.Qt.Horizontal
    _DefaultButtonSize = Qt.QSize(16, 16)

    stepSizeChanged = Qt.Signal(float, str)

    def __init__(self, parent=None, designMode=False):
        self.__customLabel = None
        self.__iconSize = self._DefaultButtonSize
        self.__stepButtonOrientation = self._DefaultStepButtonOrientation
        TaurusWidget.__init__(self, parent)
        self.loadUi()
        ui = self.ui

        self.setAutoTooltip(False)

        # initialize read/write position widgets
        ui.positionLabel = PositionLabel(designMode=designMode)
        ui.positionLabel.setAutoTooltip(False)

        ui.positionEdit = PositionSpinBox(designMode=designMode)
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
        ui.stepDownButton.setObjectName("StepDownButton")
        ui.stepDownButton.setCommand("StepDown")

        ui.stepUpButton = TaurusCommandToolButton()
        ui.stepUpButton.setAutoTooltip(False)
        ui.stepUpButton.setObjectName("StepUpButton")
        ui.stepUpButton.setCommand("StepUp")

        stepButtonPanelLayout.addWidget(ui.stepDownButton)
        stepButtonPanelLayout.addWidget(ui.stepUpButton)
        self.__updateStepButtonPanel()

        self.stepSizeChanged.connect(self.__handleStepSizeChanged)

        # build steps menu
        ui.stepMenu = Qt.QMenu()
        ui.stepMenuToolButton.setIcon(getIcon(":/step.png"))
        ui.stepMenuToolButton.setMenu(ui.stepMenu)
        ui.stepActionGroup = Qt.QActionGroup(self)
        ui.stepActionGroup.setExclusive(True)
        ui.stepActionGroup.triggered.connect(self.__onStepSizeChangedByUI)

        # build reference position menu
        ui.refPointsMenu = Qt.QMenu()
        ui.refPointsMenuToolButton.setIcon(getIcon(":/status/flag-green.svg"))
        ui.refPointsMenuToolButton.setMenu(ui.refPointsMenu)
        ui.refPointsActionGroup = Qt.QActionGroup(self)
        ui.refPointsActionGroup.setExclusive(True)
        ui.refPointsActionGroup.triggered.connect(self.__onRefPosChangedByUI)

        # build menu
        ui.menu = Qt.QMenu()
        ui.menuToolButton.setIcon(getIcon("preferences-system"))
        ui.menuToolButton.setMenu(ui.menu)

        ui.stepSubMenu = Qt.QMenu("Change step size")
        ui.stepSubMenu.setIcon(getIcon(":/step.png"))
        ui.menu.addMenu(ui.stepSubMenu)

        ui.refPointsSubMenu = Qt.QMenu("Go to")
        ui.refPointsSubMenu.setIcon(getIcon(":/status/flag-green.svg"))
        ui.menu.addMenu(ui.refPointsSubMenu)

        ui.menu.addSeparator()
        ui.expertPanelAction = Qt.QAction("Expert panel...", self)
        ui.expertPanelAction.setToolTip("Open an expert axis dialog")
        ui.expertPanelAction.setStatusTip("Open an expert axis dialog")
        ui.menu.addAction(ui.expertPanelAction)
        ui.expertPanelAction.triggered.connect(self.__onExpertPanelTriggered)

        # Stop button
        ui.stopToolButton.setIcon(getThemeIcon("media-playback-stop"))

        # need to resize button icon size because of some styles (windows, kde)
        self.__updateIconSize()

    def __onExpertPanelTriggered(self, checked=False):
        dialog = Qt.QDialog(self)
        name = self.getModelName()
        dialog.setWindowTitle(name)
        layout = Qt.QVBoxLayout(dialog)

        from taurus.qt.qtgui.panel import TaurusDevicePanel
        panel = TaurusDevicePanel()
        panel.setModel(name)
        layout.addWidget(panel)

        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def __updateIconSize(self):
        ui, iconSize = self.ui, self.__iconSize
        ui.stepDownButton.setIconSize(iconSize)
        ui.stepUpButton.setIconSize(iconSize)
        ui.stepMenuToolButton.setIconSize(iconSize)
        ui.refPointsMenuToolButton.setIconSize(iconSize)
        ui.menuToolButton.setIconSize(iconSize)
        ui.stopToolButton.setIconSize(iconSize)
        stepSize = iconSize
        if self.__stepButtonOrientation == Qt.Qt.Vertical:
            stepSize = Qt.QSize(8, 8)
        ui.stepDownButton.setIconSize(stepSize)
        ui.stepUpButton.setIconSize(stepSize)
        ui.readWriteWidget.setMinimumHeight(iconSize.height())

    def __updateStepButtonPanel(self):
        # update the step button panel according to the orientation
        # (horizontal/vertical step down/up buttons)
        ui = self.ui
        layout = ui.stepButtonPanel.layout()
        orientation = self.__stepButtonOrientation
        iconSize = self.__iconSize
        if orientation == Qt.Qt.Horizontal:
            direction = Qt.QBoxLayout.LeftToRight
            ui.stepDownButton.setArrowType(Qt.Qt.LeftArrow)
            ui.stepUpButton.setArrowType(Qt.Qt.RightArrow)
        else:
            iconSize = Qt.QSize(8, 8)
            direction = Qt.QBoxLayout.BottomToTop
            ui.stepDownButton.setArrowType(Qt.Qt.DownArrow)
            ui.stepUpButton.setArrowType(Qt.Qt.UpArrow)
        ui.stepDownButton.setIconSize(iconSize)
        ui.stepUpButton.setIconSize(iconSize)
        layout.setDirection(direction)

    def __addStep(self, qstep):
        if not isinstance(qstep, Step):
            qstep = Step(qstep)

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
        self.ui.stepSubMenu.addAction(action)

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

    def __addReferencePoint(self, point):
        if not isinstance(point, ReferencePoint):
            point = ReferencePoint(point)

        # if reference position exists return the corresponding action
        for action in self.ui.refPointsActionGroup.actions():
            pt = Qt.from_qvariant(action.data())
            if pt.position == point.position:
                return action

        # create a new action for the reference position and add it to the menu
        action = self.ui.refPointsActionGroup.addAction(point.label)
        action.setData(point)
        #action.setCheckable(True)
        self.ui.refPointsMenu.addAction(action)
        self.ui.refPointsSubMenu.addAction(action)

        # re-order actions is the step group
        actions = self.ui.refPointsActionGroup.actions()
        points = {}
        for action in actions:
            point = Qt.from_qvariant(action.data())
            points[point] = action
            self.ui.refPointsActionGroup.removeAction(action)
        for point in sorted(points):
            action = points[point]
            self.ui.refPointsActionGroup.addAction(action)

        return action

    def __onRefPosChangedByUI(self, action):
        point = Qt.from_qvariant(action.data())
        self.getModelObj().getAttribute("Position").write(point.position)

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
        self.ui.stepMenuToolButton.setText(step.label)
        self.ui.positionEdit.setSingleStep(step.size)
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
        readOnly = self.isReadOnly()
        action = self.ui.stepActionGroup.checkedAction()
        if action is None:
            stepLabel = "?"
        else:
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

    # -~-~-~-~-~-~-~
    # Qt Properties
    # -~-~-~-~-~-~-~

    @Qt.Slot(str)
    def setModel(self, model_name):
        TaurusWidget.setModel(self, model_name)
        self.ui.readWriteWidget.setModel(model_name + "/Position")
        self.ui.stepDownButton.setModel(model_name)
        self.ui.stepUpButton.setModel(model_name)
        self.ui.stopToolButton.setModel(model_name)
        stepSize = Attribute(model_name + "/StepSize")
        stepSize.addListener(self.__onStepSizeChanged)

        self.ui.axisLabel.setText(self.__getAxisLabel())
        self.__updateToolTips()

    def getCustomLabel(self):
        if self.__customLabel is None:
            return ""
        return self.__customLabel

    @Qt.Slot(str)
    def setCustomLabel(self, label):
        self.__customLabel = label
        self.ui.axisLabel.setText(self.__getAxisLabel())
        self.__updateToolTips()

    def resetCustomLabel(self):
        self.setCustomLabel(None)

    customLabel = Qt.Property(str, getCustomLabel, setCustomLabel,
                              resetCustomLabel)

    def isReadOnly(self):
        return self.ui.readWriteWidget.readOnly

    @Qt.Slot(bool)
    def setReadOnly(self, readOnly):
        self.ui.readWriteWidget.readOnly = readOnly
        self.ui.stepButtonPanel.setEnabled(not readOnly)
        self.__updateToolTips()

    def resetReadOnly(self):
        self.setReadOnly(self.ui.readWriteWidget._DefaultReadOnly)

    readOnly = Qt.Property(bool, isReadOnly, setReadOnly, resetReadOnly)

    def getSteps(self):
        result = []
        for action in self.ui.stepActionGroup.actions():
            qstep = Qt.from_qvariant(action.data())
            result.append(str(qstep))
        return result

    @Qt.Slot("QStringList")
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

    def getReferencePoints(self):
        result = []
        for action in self.ui.refPointsActionGroup.actions():

            qstep = Qt.from_qvariant(action.data())
            result.append(str(qstep))
        return result

    @Qt.Slot("QStringList")
    def setReferencePoints(self, ref_points):
        for ref_point in ref_points:
            if isinstance(ref_point, Qt.QString): # happens in the QtDesigner
                ref_point = unicode(ref_point)
            try:
                ref_point = json.loads(ref_point)
            except TypeError:
                pass
            self.__addReferencePoint(ref_point)

    referencePoints = Qt.Property("QStringList", getReferencePoints,
                                  setReferencePoints)

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

    def isLabelVisible(self):
        return self.ui.labelPanel.isVisible()

    @Qt.Slot(bool)
    def setLabelVisible(self, visible):
        self.ui.labelPanel.setVisible(visible)

    def resetLabelVisible(self):
        self.setLabelVisible(True)

    labelVisible = Qt.Property(bool, isLabelVisible, setLabelVisible,
                               resetLabelVisible)

    def isStepButtonsVisible(self):
        return self.ui.stepButtonPanel.isVisible()

    @Qt.Slot(bool)
    def setStepButtonsVisible(self, visible):
        self.ui.stepButtonPanel.setVisible(visible)

    def resetStepButtonsVisible(self):
        self.setStepButtonsVisible(True)

    stepButtonsVisible = Qt.Property(bool, isStepButtonsVisible,
                                     setStepButtonsVisible,
                                     resetStepButtonsVisible)

    def isStepMenuVisible(self):
        return self.ui.stepMenuToolButton.isVisible()

    @Qt.Slot(bool)
    def setStepMenuVisible(self, visible):
        self.ui.stepMenuToolButton.setVisible(visible)

    def resetStepMenuVisible(self):
        self.setStepMenuVisible(True)

    stepMenuVisible = Qt.Property(bool, isStepMenuVisible,
                                  setStepMenuVisible,
                                  resetStepMenuVisible)

    def isReferencePointsMenuVisible(self):
        return self.ui.refPointsMenuToolButton.isVisible()

    @Qt.Slot(bool)
    def setReferencePointsMenuVisible(self, visible):
        self.ui.refPointsMenuToolButton.setVisible(visible)

    def resetReferencePointsMenuVisible(self):
        self.setReferencePointsMenuVisible(True)

    referencePointsMenuVisible = Qt.Property(bool, isReferencePointsMenuVisible,
                                             setReferencePointsMenuVisible,
                                             resetReferencePointsMenuVisible)

    def isOperationMenuVisible(self):
        return self.ui.menuToolButton.isVisible()

    @Qt.Slot(bool)
    def setOperationMenuVisible(self, visible):
        self.ui.menuToolButton.setVisible(visible)

    def resetOperationMenuVisible(self):
        self.setOperationMenuVisible(True)

    operationMenuVisible = Qt.Property(bool, isOperationMenuVisible,
                                       setOperationMenuVisible,
                                       resetOperationMenuVisible)

    def isStopButtonVisible(self):
        return self.ui.stopToolButton.isVisible()

    @Qt.Slot(bool)
    def setStopButtonVisible(self, visible):
        self.ui.stopToolButton.setVisible(visible)

    def resetStopButtonVisible(self):
        self.setStopButtonVisible(True)

    stopButtonVisible = Qt.Property(bool, isStopButtonVisible,
                                    setStopButtonVisible,
                                    resetStopButtonVisible)

    def getIconSize(self):
        return self.__iconSize

    @Qt.Slot("QSize")
    def setIconSize(self, iconSize):
        self.__iconSize = iconSize
        self.__updateIconSize()

    def resetIconSize(self):
        self.setIconSize(self._DefaultIconSize)

    iconSize = Qt.Property("QSize", getIconSize, setIconSize, resetIconSize)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.axis",
                    icon=":designer/motor.png",
                    group="ESRF Widgets")


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

    if not len(args):
        parser.error("Must give at least one axis")

    window = Qt.QWidget()
    layout = Qt.QVBoxLayout(window)
    layout.setContentsMargins(3, 3, 3, 3)
    layout.setSpacing(2)
    defaultSteps = [(0.01, "10 um"), (0.1, "100 um"), (1.0, "1 mm"),
                    (10.0, "10 mm"), (100.0, "100 mm")]
    defaultSteps = 0.01, 0.1, 1.0, 10.0, 100.0
    defaultReferencePoints = [(i, "{0} mm".format(i)) for i in (1,2,4,5,10,25)]

    inOutReferencePoints = [
        (10.45, "Out (10.45 mm)"),
        (2.55, "In (2.55 mm)"),
        (20, "Maintenance (20.00 mm)")
    ]

    for motor in args:
        axisPanel = Qt.QGroupBox(motor)
        layout.addWidget(axisPanel)

        axisLayout = Qt.QVBoxLayout(axisPanel)
        axisLayout.setSpacing(2)
        axisLayout.setContentsMargins(2, 2, 2, 2)

        # "default" motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setReferencePoints(defaultReferencePoints)
        axis.setModel(motor)
        axis.ui.stepDownButton.setIcon(getThemeIcon("edit-undo"))
        axis.ui.stepDownButton.setArrowType(Qt.Qt.NoArrow)
        axis.ui.stepUpButton.setIcon(getThemeIcon("edit-redo"))
        axis.ui.stepUpButton.setArrowType(Qt.Qt.NoArrow)
        axisLayout.addWidget(axis)

        # vertical step buttons, motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setReferencePoints(inOutReferencePoints)
        axis.setModel(motor)
        axis.setStepButtonPanelOrientation(Qt.Qt.Vertical)
        axisLayout.addWidget(axis)

        # read-only, custom label, motor widget
        axis = AxisWidget()
        axis.setSteps(defaultSteps)
        axis.setReferencePoints(defaultReferencePoints)
        axis.setModel(motor)
        axis.setReadOnly(True)
        axis.setStepMenuVisible(False)
        axis.setStepButtonsVisible(False)
        axis.setStopButtonVisible(False)
        axis.setOperationMenuVisible(False)
        axis.setReferencePointsMenuVisible(False)
        axis.setCustomLabel("= {0} =".format(motor))
        axisLayout.addWidget(axis)

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
