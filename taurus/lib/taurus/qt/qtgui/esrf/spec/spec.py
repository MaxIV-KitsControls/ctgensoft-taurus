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
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.dialog import TaurusMessageBox
from taurus.qt.qtgui.util import UILoadable, QtDesignable

from taurus.qt.qtgui.esrf.macro import MacroForm
from taurus.qt.qtgui.esrf.macro import AScanWidget, ANScanWidget

TWENTY_DAYS = 60*60*24*20


def Specable(klass=None):
    if klass is None:
        return functools.partial(Specable)

    def _onCommandFinished(widget, result, error=False):
        widget.__last_command_id = None
        widget.ui.runButton.setEnabled(True)
        widget.ui.stopButton.setEnabled(False)

    def _runCommand(widget):
        model = widget.getModelObj()
        if model is None:
            raise ValueError("No executor has been connected")

        command = "ExecuteCmdA"
        args = [widget.getCommandLine()]
        result = model.command(command, args=args, asynch=True,
                               callback=widget._onWaitRunReply,
                               timeout=TWENTY_DAYS)
        widget.ui.runButton.setEnabled(False)
        widget.ui.stopButton.setEnabled(True)
        return result

    def _stopCommand(widget):
        model = widget.getModelObj()
        if model is None:
            raise ValueError("No executor has been connected")

        command = "AbortCmd"
        args = [widget.__last_command_id]
        result = model.command(command, args=args, asynch=True,
                               callback=widget._onWaitStopReply,
                               timeout=TWENTY_DAYS)
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
            widget._runCommand()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.setWindowTitle("Unhandled exception running macro")
            msgbox.exec_()

    def _onStopClicked(widget, checked=False):
        try:
            widget._stopCommand()
        except:
            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.setWindowTitle("Unhandled exception stopping macro")
            msgbox.exec_()

    def _onWaitRunReply(widget, result, error=False):
        widget.__last_command_id = result
        if error:
            widget.setStatusTip("Error executing macro '{0}'".format(widget.macroName))
        else:
            model = widget.getModelObj()
            while not model.command("IsReplyArrived", args=[result], asynch=False):
                time.sleep(0.1)
            result = model.command("GetReply", args=[result], asynch=False)
        if hasattr(widget, 'commandFinished'):
            widget.commandFinished.emit(result, error)

    def _onWaitStopReply(widget, result, error=False):
        pass

    def _motorListChanged(widget, evt_src, evt_type, evt_value):
        if not hasattr(widget, 'motorListChanged'):
            return
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            if evt_value.value is None:
                evt_value.value = []
            motors = [value.split() for value in evt_value.value]
            widget.motorListChanged.emit(motors)

    def getMotors(widget):
        model = widget.getModelObj()
        mot_list = widget.getModelObj().getAttribute("MotorList").read().value
        if mot_list is None:
            mot_list = []
        motors = {}
        for motor in mot_list:
            alias, name = motor.split()
            motors[alias] = name
        return motors

    def _counterListChanged(widget, evt_src, evt_type, evt_value):
        if not hasattr(widget, 'counterListChanged'):
            return
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            if evt_value.value is None:
                evt_value.value = []
            counters = [value.split() for value in evt_value.value]
            widget.counterListChanged.emit(counters)

    def getCounters(widget):
        model = widget.getModelObj()
        mot_list = widget.getModelObj().getAttribute("CounterList").read().value
        if ct_list is None:
            ct_list = []
        counters = {}
        for counter in ct_list:
            alias, name = counter.split()
            counters[alias] = name
        return counters

    def _onModelChanged(widget, model_name):
        model = widget.getModelObj()
        if model:
            motor_list_attr = model.getAttribute("MotorList")
            motor_list_attr.addListener(widget._motorListChanged)
            counter_list_attr = model.getAttribute("CounterList")
            counter_list_attr.addListener(widget._counterListChanged)


    init_original = klass.__init__
    def _init(widget, *args, **kwargs):
        widget.__last_command_id = None
        init_original(widget, *args, **kwargs)
        Qt.QObject.connect(widget,
                           Qt.SIGNAL(TaurusBaseWidget.ModelChangedSignal),
                           widget._onModelChanged)
        if hasattr(widget, 'runClicked'):
            widget.runClicked.connect(widget._onRunClicked)
        if hasattr(widget, 'stopClicked'):
            widget.stopClicked.connect(widget._onStopClicked)
        if hasattr(widget, 'commandFinished'):
            widget.commandFinished.connect(widget._onCommandFinished)

    klass._onCommandFinished = _onCommandFinished
    klass._runCommand = _runCommand
    klass._onRunClicked = _onRunClicked
    klass._onWaitRunReply = _onWaitRunReply

    klass._stopCommand = _stopCommand
    klass._onStopClicked = _onStopClicked
    klass._onWaitStopReply = _onWaitStopReply

    klass.__init__ = _init

    klass._motorListChanged = _motorListChanged
    klass._counterListChanged = _counterListChanged
    klass._onModelChanged = _onModelChanged
    klass.getMotors = getMotors
    klass.getCounters = getCounters

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
        d = MacroForm.getQtDesignerPluginInfo()
        d.update(module="taurus.qt.qtgui.esrf.spec",
                 icon=":designer/macroserver.png",
                 group="ESRF Spec Widgets")
        return d


class SpecCounterMonitorWidget(Qt.QWidget, TaurusBaseWidget):

    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        Qt.QWidget.__init__(self, parent=parent)
        TaurusBaseWidget.__init__(self, name, designMode=designMode)
        layout = Qt.QHBoxLayout(self)

    def __update(self):
        counter_list = self.getModelObj().read().value or []
        layout = self.layout()
        while layout.count():
            layout.takeAt(0)

        for i, counter in enumerate(counter_list):
            mne, dev_name = counter.split()
            label = TaurusLabel()
            label.setAutoTrim(False)
            label.setPrefixText(mne + ": ")
            label.setModel(dev_name + "/value")
            layout.addWidget(label)

    def handleEvent(self, evt_src, evt_type, evt_value):
        # We should call __update() directly. This is an ugly hack to work
        # around a tango < 9 bug that prevents subscribing to an event inside
        # an event handler
        Qt.QTimer.singleShot(10, self.__update)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.spec",
                    icon=":designer/macroserver.png",
                    group="ESRF Spec Widgets")


class SpecUIMixin(TaurusBaseWidget):

    _QtDesignerIcon = None

    def __init__(self):
        name = self.__class__.__name__
        TaurusBaseWidget.__init__(self, name=name)
        self.setAutoTooltip(False)
        self.setWindowTitle(name)
        self.loadUi()
        for w in self.findChildren(Qt.QWidget):
            if hasattr(w, "setAutoTooltip"):
                w.setAutoTooltip(False)
        self.connect(self, Qt.SIGNAL("modelChanged(const QString &)"),
                     self.onModelChanged)

    def onModelChanged(self, model_name):
        pass


class SpecBasePanel(Qt.QWidget, SpecUIMixin):

    def __init__(self,  parent=None):
        Qt.QWidget.__init__(self, parent)
        SpecUIMixin.__init__(self)

    model = Qt.Property(str, SpecUIMixin.getModel,
                        SpecUIMixin.setModel, SpecUIMixin.resetModel)


class SpecOutputWidget(Qt.QPlainTextEdit, TaurusBaseWidget):

    def __init__(self, parent=None, designMode=False):
        Qt.QPlainTextEdit.__init__(self, parent)
        TaurusBaseWidget.__init__(self, name=self.__class__.__name__,
                                  designMode=designMode)
        self.setAutoTooltip(False)
        self.__connected = False
        self.__remove_line = False
        self.setFont(Qt.QFont("Monospace"))
        self.setReadOnly(True)
        self.textChanged.connect(self.__onTextChanged)

    def __onTextChanged(self):
        self.ensureCursorVisible()

    def __removeCurrentLine(self):
        cursor = self.textCursor()
        cursor.movePosition(Qt.QTextCursor.StartOfLine,
                            Qt.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

    def __strip_cr(self, text):
        endswith_cr = text.endswith("\r")
        cr_nb = text.count("\r")
        if endswith_cr:
            cr_nb -= 1
        if cr_nb:
            pass

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Config:
            return
        if evt_type == TaurusEventType.Error:
            self.__remove_line = False
            self.__connected = False
            text = "\n--- disconnected from SPEC ---\n"
        else:
            text = evt_value.value
            if not self.__connected:
                self.__connected = True
                if not text:
                    text = "-1.SPEC> "

            if self.__remove_line:
                if "\n" not in text:
                    self.__removeCurrentLine()
                self.__remove_line = False
            if text.endswith("\r"):
                self.__remove_line = True
                text = text[:-1]

        self.moveCursor(Qt.QTextCursor.End)
        self.insertPlainText(text)

    model = Qt.Property(str, TaurusBaseWidget.getModel,
                        TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)

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
    windowLayout = Qt.QGridLayout(window)

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
    windowLayout.addWidget(panel1, 0, 0)

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
    windowLayout.addWidget(panel2, 1, 0)

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
    windowLayout.addWidget(panel3, 2, 0)

    panel4 = QGroupWidget()
    panel4.setTitle("ascan")
    layout = panel4.content().layout()
    layout.setMargin(3)
    w4 = SpecAScanWidget()
    w4.setModel(spec)
    layout.addWidget(w4)
    windowLayout.addWidget(panel4, 3, 0)

    panel5 = QGroupWidget()
    panel5.setTitle("a3scan")
    layout = panel5.content().layout()
    layout.setMargin(3)
    w5 = SpecANScanWidget()
    w5.setDimensions(3)
    w5.setModel(spec)
    layout.addWidget(w5)
    windowLayout.addWidget(panel5, 4, 0)

    panel6 = QGroupWidget()
    panel6.setTitle("counter monitor")
    layout = panel6.content().layout()
    layout.setMargin(3)
    w6 = SpecCounterMonitorWidget()
    w6.setModel(spec)
    layout.addWidget(w6)
    windowLayout.addWidget(panel6, 5, 0)

    output = SpecOutputWidget()
    output.setModel(spec + "/output")
    windowLayout.addWidget(output, 0, 1, 6, 1)
    window.show()
    app.exec_()



if __name__ == "__main__":
    main()
