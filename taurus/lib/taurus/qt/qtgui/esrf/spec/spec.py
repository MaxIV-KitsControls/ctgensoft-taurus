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
This package contains a collection of Qt based widgets designed to execute
Spec macros.
"""

__docformat__ = 'restructuredtext'

import sys
import time
import functools

from taurus.core import TaurusEventType
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.dialog import TaurusMessageBox

from taurus.qt.qtgui.esrf.macro import MacroForm
from taurus.qt.qtgui.esrf.macro import AScanWidget, ANScanWidget

TWENTY_DAYS = 60*60*24*20


def Specable(klass=None):
    if klass is None:
        return functools.partial(Specable)

    def _onCommandFinished(widget, result, error=False):
        widget.ui.runButton.setEnabled(True)

    def _executeCommand(widget):
        model = widget.getModelObj()
        if model is None:
            raise ValueError("No executor has been connected")

        command = "ExecuteCmdA"
        args = [widget.getCommandLine()]
        result = model.command(command, args=args, asynch=True,
                               callback=widget._onWaitReply,
                               timeout=TWENTY_DAYS)
        widget.ui.runButton.setEnabled(False)
        return result

    def _onRunClicked(widget, checked=False):
        if widget.isDangerous() and not widget.getForceDangerousOperations():
            result = Qt.QMessageBox.question(widget,
                "Potentially dangerous action",
                "{0}\nProceed?".format(widget.getDangerMessage()),
                Qt.QMessageBox.Ok|Qt.QMessageBox.Cancel, Qt.QMessageBox.Ok)
            if result != Qt.QMessageBox.Ok:
                return
        try:
            widget._executeCommand()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.setWindowTitle("Unhandled exception running macro")
            msgbox.exec_()

    def _onWaitReply(widget, result, error=False):
        if error:
            widget.setStatusTip("Error executing macro '{0}'".format(widget.macroName))
        else:
            model = widget.getModelObj()
            while not model.command("IsReplyArrived", args=[result], asynch=False):
                time.sleep(0.1)
            result = model.command("GetReply", args=[result], asynch=False)
        widget.commandFinished.emit(result, error)

    def _motorListChanged(widget, evt_src, evt_type, evt_value):
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            motors = [value.split() for value in evt_value.value]
            widget.motorListChanged.emit(motors)

    def _onModelChanged(widget, model_name):
        model = widget.getModelObj()
        if model:        
            motor_list_attr = model.getAttribute("MotorList")
            motor_list_attr.addListener(widget._motorListChanged)

    def getMotors(widget):
        model = widget.getModelObj()
        motors = {}
        for motor in widget.getModelObj().getAttribute("MotorList").read().value:
            alias, name = motor.split()
            motors[alias] = name
        return motors
            
    init_original = klass.__init__
    def _init(widget, *args, **kwargs):
        init_original(widget, *args, **kwargs)
        Qt.QObject.connect(widget,
                           Qt.SIGNAL(TaurusBaseWidget.ModelChangedSignal),
                           widget._onModelChanged)
        widget.runClicked.connect(widget._onRunClicked)
        widget.commandFinished.connect(widget._onCommandFinished)
        
    klass._onCommandFinished = _onCommandFinished
    klass._executeCommand = _executeCommand
    klass._onRunClicked = _onRunClicked
    klass._onWaitReply = _onWaitReply
    klass.__init__ = _init

    klass._motorListChanged = _motorListChanged
    klass._onModelChanged = _onModelChanged
    klass.getMotors = getMotors
    
    return klass


@Specable
class SpecAScanWidget(AScanWidget, TaurusBaseWidget):

    commandFinished = Qt.Signal(object, bool)
    motorListChanged = Qt.Signal(object)
    
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        AScanWidget.__init__(self, parent=parent, designMode=designMode)
        TaurusBaseWidget.__init__(self, name, designMode=designMode)
        self.motorListChanged.connect(self.__onMotorListChanged)
        self.ui.axisComboBox.currentIndexChanged.connect(self.__onMotorSelectionChanged)

    def __onMotorSelectionChanged(self, index):
        minv, maxv = float('-inf'), float('+inf')
        units = ''
        motors = self.getMotors()
        if index >= 0:
            motor_name = motors[self.ui.axisComboBox.itemData(index)]
            db = self.getModelObj().getParentObj()
            props = db.get_device_attribute_property(motor_name, 'position')['position']
            minv = float(props.get('min_value', (minv,))[0])
            maxv = float(props.get('max_value', (maxv,))[0])
            if 'unit' in props:
                units = " " + props['unit'][0]
        self.ui.startSpinBox.setMinimum(minv)
        self.ui.startSpinBox.setMaximum(maxv)        
        self.ui.startSpinBox.setSuffix(units)
        self.ui.stopSpinBox.setMinimum(minv)
        self.ui.stopSpinBox.setMaximum(maxv)        
        self.ui.stopSpinBox.setSuffix(units)            
        
    def __onMotorListChanged(self, motors):
        axisComboBox = self.ui.axisComboBox
        current_motor = axisComboBox.currentText()
        axisComboBox.clear()
        for motor_alias, _ in motors:
            axisComboBox.addItem(motor_alias, motor_alias)
        if current_motor:
            axisComboBox.setCurrentIndex(axisComboBox.findText(current_motor))
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.spec",
                    icon=":designer/macroserver.png",
                    group="ESRF Spec Widgets")

    model = Qt.Property(str, TaurusBaseWidget.getModel,
                        TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)
    

@Specable
class SpecANScanWidget(ANScanWidget, TaurusBaseWidget):

    commandFinished = Qt.Signal(object, bool)
    motorListChanged = Qt.Signal(object)
    
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        ANScanWidget.__init__(self, parent=parent, designMode=designMode)
        TaurusBaseWidget.__init__(self, name, designMode=designMode)
        self.motorListChanged.connect(self.__onMotorListChanged)
        self.dimensionsChanged.connect(self.__onDimensionsChanged)

    def __onDimensionsChanged(self, n):
        layout = self.layout()
        for dim in range(n):
            motorWidget = self.getMotorWidget(dim)
            motorWidget.currentIndexChanged.connect(self.__onMotorSelectionChanged)
        
    def __onMotorSelectionChanged(self, index):
        self.__updateMotorWidgets()

    def __updateMotorWidgets(self):
        motors = self.getMotors()
        db = self.getModelObj().getParentObj()
        for dim in range(self.dimensions):
            minv, maxv = float('-inf'), float('+inf')
            units = ''
            motorWidget = self.getMotorWidget(dim)
            startWidget = self.getStartWidget(dim)
            stopWidget = self.getStopWidget(dim)
            index = motorWidget.currentIndex()
            if index >= 0:
                motor_name = motors[motorWidget.itemData(index)]
                props = db.get_device_attribute_property(motor_name, 'position')['position']
                minv = float(props.get('min_value', (minv,))[0])
                maxv = float(props.get('max_value', (maxv,))[0])
                if 'unit' in props:
                    units = " " + props['unit'][0]
            startWidget.setMinimum(minv)
            startWidget.setMaximum(maxv)            
            startWidget.setSuffix(units)
            stopWidget.setMinimum(minv)
            stopWidget.setMaximum(maxv)            
            stopWidget.setSuffix(units)            
        
    def __onMotorListChanged(self, motors):
        layout = self.layout()
        for dim in range(self.dimensions):
            axisComboBox = layout.itemAtPosition(dim, 0).widget()
            current_motor = axisComboBox.currentText()
            axisComboBox.clear()
            for motor_alias, motor_name in motors:
                axisComboBox.addItem(motor_alias, motor_alias)
            if current_motor:
                axisComboBox.setCurrentIndex(axisComboBox.findText(current_motor))
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.spec",
                    icon=":designer/macroserver.png",
                    group="ESRF Spec Widgets")
    
    model = Qt.Property(str, TaurusBaseWidget.getModel,
                        TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)


@Specable
class SpecMacroForm(MacroForm, TaurusBaseWidget):

    commandFinished = Qt.Signal(object, bool)
    motorListChanged = Qt.Signal(object)
    
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        MacroForm.__init__(self, parent=parent, designMode=designMode)
        TaurusBaseWidget.__init__(self, name, designMode=designMode)
        self.motorListChanged.connect(self.__onMotorListChanged)

    def __onMotorListChanged(self, motors):
        self.__fillMotorArgumentWidgets(motors)

    def __fillMotorArgumentWidgets(self, motors):
        argw = self.getWidgetArguments()
        for argument, _, field in argw:
            if argument.dtype == 'motor':
                field.clear()
                for motor_alias, _ in motors:
                    field.addItem(motor_alias, motor_alias)
                if argument.default_value is not None:
                    field.setCurrentIndex(field.findData(argument.default_value))

    def _updateArguments(self):
        MacroForm._updateArguments(self)
        model = self.getModelObj()
        if model:
            evt_value = model.getAttribute("MotorList").read()
            motors = [value.split() for value in evt_value.value]
            self.__fillMotorArgumentWidgets(motors)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.spec",
                    icon=":designer/macroserver.png",
                    group="ESRF Spec Widgets")

    

def main():
    import sys
    from taurus.core.util.argparse import get_taurus_parser
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.container import QGroupWidget
    from taurus.qt.qtgui.resource import getThemeIcon
    from taurus.qt.qtgui.esrf.macro import Argument
    
    parser = get_taurus_parser()
    parser.usage = "%prog [options] <spec device name>"
    app = TaurusApplication(sys.argv, cmd_line_parser=parser, 
                            app_name="Axis", app_version="1.0",
                            org_domain="Taurus",
                            org_name="Taurus community")
        
    args = app.get_command_line_args()

    if not len(args):
        parser.error("Must give a spec device name")

    spec = args[0]
    window = Qt.QWidget()
    windowLayout = Qt.QVBoxLayout(window)

    panel1 = QGroupWidget()
    panel1.setTitle("ct")
    layout = panel1.content().layout()
    w1 = SpecMacroForm()
    w1.setMacroName("ct")
    w1.setModel(spec)
    args = [
        Argument(name="integration_time", label="Int. time", dtype=float,
                 min_value=0.0, unit="s", default_value=1.0,
                 tooltip="integration time (in seconds)"),
    ]
    w1.setArguments(args)
    layout.addWidget(w1)
    windowLayout.addWidget(panel1)

    panel2 = QGroupWidget()
    panel2.setTitle("wm")
    layout = panel2.content().layout()
    w2 = SpecMacroForm()
    w2.setMacroName("wm")
    args = [
        Argument(name="motor", label="Motor", dtype='motor',
                 tooltip="motor name"),
    ]
    w2.setModel(spec)
    w2.setArguments(args)
    layout.addWidget(w2)
    windowLayout.addWidget(panel2)

    panel3 = QGroupWidget()
    panel3.setTitle("ascan")
    layout = panel3.content().layout()
    w3 = SpecMacroForm()
    w3.setMacroName("ascan")
    args = [
        Argument(name="motor", label="Motor", dtype='motor',
                 tooltip="motor name"),
        Argument(name="start", label="Start", dtype=float,
                 tooltip="scan motor start position"),
        Argument(name="end", label="End", dtype=float,
                 tooltip="scan motor end position"),
        Argument(name="nb_interv", label="Nb. interv", dtype=int,
                 tooltip="number of intervals"),
        Argument(name="int_time", label="Integ. time", dtype=float, unit="s",
                 tooltip="integration time"),                 
    ]
    w3.setModel(spec)
    w3.setArguments(args)
    layout.addWidget(w3)
    windowLayout.addWidget(panel3)

    panel4 = QGroupWidget()
    panel4.setTitle("ascan")
    layout = panel4.content().layout()
    layout.setMargin(3)
    w4 = SpecAScanWidget()
    w4.setModel(spec)
    layout.addWidget(w4)
    windowLayout.addWidget(panel4)

    panel5 = QGroupWidget()
    panel5.setTitle("a3scan")
    layout = panel5.content().layout()
    layout.setMargin(3)
    w5 = SpecANScanWidget()
    w5.setDimensions(3)
    w5.setModel(spec)
    layout.addWidget(w5)
    windowLayout.addWidget(panel5)    
    
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
