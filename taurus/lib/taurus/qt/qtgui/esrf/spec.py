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

import time

from taurus.core import TaurusEventType
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.dialog import TaurusMessageBox

from taurus_esrf.qt.qtgui.macro import MacroForm


class SpecMacroForm(MacroForm, TaurusBaseWidget):

    TWENTY_DAYS = 60*60*24*20

    commandFinished = Qt.Signal(object, bool)

    motorListChanged = Qt.Signal(object)
    
    
    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        MacroForm.__init__(self, parent=parent, designMode=designMode)
        TaurusBaseWidget.__init__(self, name, designMode=designMode)
        self.runClicked.connect(self.__onRunClicked)
        self.commandFinished.connect(self.__onCommandFinished)
        self.motorListChanged.connect(self.__onMotorListChanged)

    def __onCommandFinished(self, result, error=False):
        self.runButton.setEnabled(True)
        
    def _executeCommand(self):
        """
        Executes the active command on the registered model. If widget is in
        asynchronous mode, the method returns None.
        If in synchronous mode the method will execute the command and block
        until it finishes. It returns the result in 
        """
        macroName = self.macroName
        if not macroName:
            raise ValueError("No macro has been specified")
        model = self.getModelObj()
        if model is None:
            raise ValueError("No executor has been connected")

        command = "ExecuteCmdA"
        args = [macroName] + self.getArgumentValueList()
        args = [" ".join(map(str, args))]
        result = model.command(command, args=args, asynch=True,
                               callback=self.__onWaitReply,
                               timeout=self.TWENTY_DAYS)
        self.runButton.setEnabled(False)
        return result

    def __onRunClicked(self, checked=False):
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
            msgbox.setWindowTitle("Unhandled exception running macro")
            msgbox.exec_()

    def __onWaitReply(self, cmd_id, error=False):
        model = self.getModelObj()
        while not model.command("IsReplyArrived", args=[cmd_id], asynch=False):
            time.sleep(0.1)
        result = model.command("GetReply", args=[cmd_id], asynch=False)
        self.commandFinished.emit(result, False)

    def __motorListChanged(self, evt_src, evt_type, evt_value):
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            motors = [value.split() for value in evt_value.value]
            self.motorListChanged.emit(motors)

    def __onMotorListChanged(self, motors):
        self.__fillMotorArgumentWidgets(motors)

    def __fillMotorArgumentWidgets(self, motors):
        argw = self.getWidgetArguments()
        for argument, label, field in argw:
            if argument.dtype == 'motor':
                field.clear()
                for motor_alias, motor_name in motors:
                    field.addItem(motor_alias, motor_alias)
                if argument.default_value is not None:
                    field.setCurrentIndex(field.findData(self.default_value))

    def _updateArguments(self):
        MacroForm._updateArguments(self)
        model = self.getModelObj()
        if model:
            evt_value = model.getAttribute("MotorList").read()
            motors = [value.split() for value in evt_value.value]
            self.__fillMotorArgumentWidgets(motors)
        
    def setModel(self, model_name):
        model = self.getModelObj()
        if model:
            motor_list_attr = model.getAttribute("MotorList")
            motor_list_attr.removeListener(self.__motorListChanged)

        TaurusBaseWidget.setModel(self, model_name)
        
        model = self.getModelObj()
        if model:        
            motor_list_attr = model.getAttribute("MotorList")
            motor_list_attr.addListener(self.__motorListChanged)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus_esrf.qt.qtgui.spec",
                    icon=":designer/macroserver.png",
                    group="ESRF Spec Widgets")


def main():
    import sys
    from taurus.core.util.argparse import get_taurus_parser
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.container import QGroupWidget
    from taurus.qt.qtgui.resource import getThemeIcon
    from taurus_esrf.qt.qtgui.macro import Argument
    
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

    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
