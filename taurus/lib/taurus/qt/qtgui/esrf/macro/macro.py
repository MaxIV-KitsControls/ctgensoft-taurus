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
procedures. They can be used to execute macros from SPEC, macros from the
sardana macro executor, simple python functions, etc.
"""

__docformat__ = 'restructuredtext'

import json

from taurus.external.qt import Qt
from taurus.qt.qtgui.resource import getIcon


class _UI(object):
    pass


_ASCAN_DESC = """\
ascan - one-motor scan

     ascan scans one motor, as specified by motor.  The motor starts at the position given by start and ends at the position
     given by end.  The step size is (start-end)/intervals.  The number of data points collected will be intervals+1.  Count
     time is given by time, which if positive, specifies seconds and if negative, specifies monitor counts.
"""


class AScanWidget(Qt.QWidget):
    """Single axis, absolute scan widget"""
    
    runClicked = Qt.Signal(bool)

    _DefaultOrientation = Qt.Qt.Horizontal

    macroName = 'ascan'

    def __init__(self, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self.__orientation = self._DefaultOrientation
        self.ui = _UI()
        self.ui.axisComboBox = Qt.QComboBox(self)
        self.ui.axisComboBox.setToolTip("motor to scan")
        self.ui.startSpinBox = Qt.QDoubleSpinBox(self)
        self.ui.startSpinBox.setToolTip("start position")
        self.ui.stopSpinBox = Qt.QDoubleSpinBox(self)
        self.ui.stopSpinBox.setToolTip("end position")        
        self.ui.intervalsSpinBox = Qt.QSpinBox(self)
        self.ui.intervalsSpinBox.setToolTip("number of intervals")        
        self.ui.intervalsSpinBox.setMinimum(0)
        self.ui.intervalsSpinBox.setMaximum(2**31-1)
        self.ui.timeSpinBox = Qt.QDoubleSpinBox(self)
        self.ui.timeSpinBox.setToolTip("If positive, count time in seconds\n"
                                       "If negative, monitor counts")
        self.ui.timeSpinBox.setMinimum(float('-inf'))
        self.ui.timeSpinBox.setMaximum(float('+inf'))
        self.ui.timeSpinBox.setSuffix(" s")
        icon = getIcon(":/actions/media_playback_start.svg")
        self.ui.runButton = Qt.QPushButton(icon, "")
        layout = Qt.QBoxLayout(Qt.QBoxLayout.LeftToRight, self)
        layout.setMargin(0)
        layout.addWidget(self.ui.axisComboBox)
        layout.addWidget(self.ui.startSpinBox)
        layout.addWidget(self.ui.stopSpinBox)
        layout.addWidget(self.ui.intervalsSpinBox)
        layout.addWidget(self.ui.timeSpinBox)
        layout.addWidget(self.ui.runButton)        

        self.ui.axisComboBox.currentIndexChanged[int].connect(self.__onAxisChanged)
        self.ui.runButton.clicked.connect(self.runClicked)

        self.setToolTip(_ASCAN_DESC)
        
        self.__updateOrientation()

    def __updateOrientation(self):
        # update the step button panel according to the orientation
        # (horizontal/vertical step down/up buttons)
        ui = self.ui
        layout = self.layout()
        orientation = self.__orientation
        if orientation == Qt.Qt.Horizontal:
            direction = Qt.QBoxLayout.LeftToRight
        else:
            direction = Qt.QBoxLayout.TopToBottom
        layout.setDirection(direction)

    def getOrientation(self):
        return self.__orientation

    def setOrientation(self, orientation):
        self.__orientation = orientation
        self.__updateOrientation()

    def resetOrientation(self):
        self.setOrientation(self._DefaultOrientation)

    orientation = Qt.Property("Qt::Orientation", getOrientation, setOrientation,
                              resetOrientation)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.macro",
                    icon=":designer/macroserver.png",
                    group="ESRF Macro Widgets")

    def __onAxisChanged(self, index):
        enabled = index != -1
        self.ui.startSpinBox.setEnabled(enabled)
        self.ui.stopSpinBox.setEnabled(enabled)
        self.ui.intervalsSpinBox.setEnabled(enabled)
        self.ui.timeSpinBox.setEnabled(enabled)

    def getRunButtonVisible(self):
        return self.ui.runButton.isVisible()

    def setRunButtonVisible(self, visible):
        self.ui.runButton.setVisible(visible)

    def resetRunButtonVisible(self):
        self.setRunButtonVisible(True)

    runButtonVisible = Qt.Property(bool, getRunButtonVisible,
                                   setRunButtonVisible, resetRunButtonVisible)

    def getArgumentValueList(self):
        ui = self.ui
        widgets = ui.axisComboBox, ui.startSpinBox, ui.stopSpinBox, ui.intervalsSpinBox, ui.timeSpinBox
        return [_getWidgetValue(w) for w in widgets]
    
    def getCommandLineList(self):
        return [self.macroName] + self.getArgumentValueList()

    def getCommandLine(self):
        return " ".join(map(str, self.getCommandLineList()))


class ANScanWidget(Qt.QWidget):
    """Multiple axis, absolute scan widget"""
    
    runClicked = Qt.Signal(bool)
    dimensionsChanged = Qt.Signal(int)
    
    _DefaultDimensions = 1
    
    def __init__(self, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self.__old_dimensions = 0
        self.__dimensions = 0
        self.ui = _UI()
        layout = Qt.QGridLayout(self)
        self.ui.intervalsSpinBox = Qt.QSpinBox(self)
        self.ui.intervalsSpinBox.setToolTip("number of intervals")        
        self.ui.intervalsSpinBox.setMinimum(0)
        self.ui.intervalsSpinBox.setMaximum(2**31-1)
        self.ui.timeSpinBox = Qt.QDoubleSpinBox(self)
        self.ui.timeSpinBox.setToolTip("If positive, count time in seconds\n"
                                       "If negative, monitor counts")        
        self.ui.timeSpinBox.setMinimum(float('-inf'))
        self.ui.timeSpinBox.setMaximum(float('+inf'))
        self.ui.timeSpinBox.setSuffix(" s")
        icon = getIcon(":/actions/media_playback_start.svg")
        self.ui.runButton = Qt.QPushButton(icon, "")
        self.ui.runButton.clicked.connect(self.runClicked)
        
        layout.setMargin(0)
        layout.addWidget(self.ui.intervalsSpinBox, 0, 3)
        layout.addWidget(self.ui.timeSpinBox, 0, 4)
        layout.addWidget(self.ui.runButton, 0, 5)

        self.dimensionsChanged.connect(self.__onDimensionsChanged)
        self.setDimensions(self._DefaultDimensions)

    def __onDimensionsChanged(self, n):
        old_n = self.__old_dimensions
        layout = self.layout()
        if old_n == n:
            return
        while old_n > n:
            for col in range(3):
                widget = layout.itemAtPosition(old_n - 1, col).widget()
                index = layout.indexOf(widget)
                layout.takeAt(index)
                widget.setParent(None)
                widget.deleteLater()
            old_n -= 1
        while old_n < n:
            axis_nb = old_n + 1
            axisComboBox = Qt.QComboBox(self)
            axisComboBox.setToolTip("motor%d to scan" % axis_nb)
            startSpinBox = Qt.QDoubleSpinBox(self)
            startSpinBox.setToolTip("start%d position" % axis_nb)
            stopSpinBox = Qt.QDoubleSpinBox(self)
            stopSpinBox.setToolTip("end%d position" % axis_nb)
            layout.addWidget(axisComboBox, old_n, 0)
            layout.addWidget(startSpinBox, old_n, 1)
            layout.addWidget(stopSpinBox, old_n, 2)
            old_n += 1
        if n > 1:
            self.macroName = "a{0}scan".format(n)
        else:
            self.macroName = "ascan"

    def getMotorWidget(self, dim):
        return self.layout().itemAtPosition(dim, 0).widget()

    def getStopWidget(self, dim):
        return self.layout().itemAtPosition(dim, 1).widget()
            
    def getStartWidget(self, dim):
        return self.layout().itemAtPosition(dim, 2).widget()
                
    def getWidgets(self):
        widgets = []
        for dim in range(self.__dimensions):
            widgets.append(self.getMotorWidget(dim))
            widgets.append(self.getStartWidget(dim))
            widgets.append(self.getStopWidget(dim))
        widgets.append(self.ui.intervalsSpinBox)
        widgets.append(self.ui.timeSpinBox)
        return widgets
            
    def getArgumentValueList(self):
        return [_getWidgetValue(w) for w in self.getWidgets()]

    def getCommandLineList(self):
        return [self.macroName] + self.getArgumentValueList()

    def getCommandLine(self):
        return " ".join(map(str, self.getCommandLineList()))
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.macro",
                    icon=":designer/macroserver.png",
                    group="ESRF Macro Widgets")

    def __onAxisChanged(self, index):
        enabled = index != -1
        self.ui.startSpinBox.setEnabled(enabled)
        self.ui.stopSpinBox.setEnabled(enabled)
        self.ui.intervalsSpinBox.setEnabled(enabled)
        self.ui.timeSpinBox.setEnabled(enabled)

    def getDimensions(self):
        return self.__dimensions

    def setDimensions(self, dimensions):
        if dimensions == self.__dimensions:
            return
        self.__old_dimensions = self.__dimensions
        self.__dimensions = dimensions
        self.dimensionsChanged.emit(dimensions)

    def resetDimensions(self):
        self.setDimensions(self._DefaultDimensions)

    dimensions = Qt.Property(int, getDimensions, setDimensions,
                             resetDimensions)

    def getRunButtonVisible(self):
        return self.ui.runButton.isVisible()

    def setRunButtonVisible(self, visible):
        self.ui.runButton.setVisible(visible)

    def resetRunButtonVisible(self):
        self.setRunButtonVisible(True)

    runButtonVisible = Qt.Property(bool, getRunButtonVisible,
                                   setRunButtonVisible, resetRunButtonVisible)

class Argument:
    """Object containing argument information"""
    
    def __init__(self, name=None, dtype=None, label=None, unit=None,
                 tooltip=None, statustip=None, icon=None, min_value=None,
                 max_value=None, default_value=None):
        if name is None:
            name = "<arg>"
        self.name = name
        self.dtype = self.__to_dtype(dtype)
        if label is None:
            label = name.capitalize()
        self.label = label
        self.unit = unit
        self.tooltip = tooltip
        self.statustip = statustip
        self.unit = unit
        self.icon = icon
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value

    def __to_dtype(self, dtype):
        if dtype in (None, str):
            dtype = "str"
        elif dtype == int:
            dtype = 'int'
        elif dtype == float:
            dtype = 'float'
        elif dtype == bool:
            dtype = 'bool'
        return dtype

    def __to_dict(self):
        d = dict(name=self.name, dtype=self.dtype, label=self.label)
        for item_name in ("unit", "tooltip", "statustip", "icon", "min_value",
                          "max_value", "default_value"):
            item = getattr(self, item_name)
            if item is not None:
                d[item_name] = item
        return d
    
    DTYPE_WIDGET_MAP = {
        'str': Qt.QLineEdit,
        'int': Qt.QSpinBox,
        'float': Qt.QDoubleSpinBox,
        'bool': Qt.QCheckBox,
        'enum': Qt.QComboBox,
        'motor': Qt.QComboBox,
    }

    def getFieldWidgetClass(self):
        dtype = self.dtype
        if isinstance(dtype, (list, tuple)):
            dtype = 'enum'
        return self.DTYPE_WIDGET_MAP[dtype]

    def createLabelWidget(self, parent=None):
        widget = Qt.QLabel(parent)
        label = self.label
        if not label.endswith(":"):
            label += ":"
        widget.setText(label)
        if self.tooltip is not None:
            widget.setToolTip(self.tooltip)
        return widget
    
    def createFieldWidget(self, parent=None):
        dtype = self.dtype
        WidgetClass = self.getFieldWidgetClass()
        widget = WidgetClass(parent)
        if dtype == "str":
            if self.default_value is not None:
                widget.setText(self.default_value)
        elif dtype in ("int", "float"):
            if self.min_value is not None:
                widget.setMinimum(self.min_value)
            else:
                widget.setMinimum(-2**31+1)
            if self.max_value is not None:
                widget.setMaximum(self.max_value)
            else:
                widget.setMaximum(2**31-1)
            if self.unit is not None:
                widget.setSuffix(" " + self.unit)
            if self.default_value is not None:
                widget.setValue(self.default_value)
        elif isinstance(dtype, (list, tuple)):
            for item in dtype:
                if isinstance(item, (list, tuple)):
                    value, label = item
                else:
                    value, label = item, item
                if self.unit is not None:
                    label += " " + self.unit
                if self.icon is None:
                    widget.addItem(label, value)
                else:
                    widget.addItem(self.icon, label, value)
            if self.default_value is not None:
                widget.setCurrentIndex(widget.findData(self.default_value))
        if self.tooltip is not None:
            widget.setToolTip(self.tooltip)
        if self.statustip is not None:
            widget.setStatusTip(self.statustip)
        
        return widget

    def __str__(self):
        return json.dumps(self.__to_dict())


def _getWidgetValue(widget):
    if isinstance(widget, Qt.QLineEdit):
        return widget.text()
    elif isinstance(widget, Qt.QAbstractSpinBox):
        return widget.value()
    elif isinstance(widget, Qt.QComboBox):
        return widget.itemData(widget.currentIndex())
    elif isinstance(widget, Qt.QCheckBox):
        return widget.isChecked()


_ARG_DOC = """\
A list of strings. Each string should be a JSON like representation of a dict
with the following elements:
  - name: a string (mandatory)
  - label: a string (optional, if not given name is used as label)
  - dtype: a string (optional, defaults to 'str'. Possible values:
    'float', 'int', 'bool', 'str', 'motor' or a list of strings with possible values
  - min_value: int/float (optional, defaults to -inf) (if dtype is not numeric is ignored)
  - max_value: int/float (optional, defaults to +inf) (if dtype is not numeric is ignored)
  - unit: a string with unit name (optional, default is no unit)
  - tooltip: a string with argument tooltip (optional, default is no tooltip)
  - statustip: a string with argument statustip (optional, default is no statustip)
  - default_value: default value (depends on type) (optional, default is no default value)

Examples:

  1. {"name": "motor", "dtype": "motor"}
  2. {"name": "start_pos", "label": "Start position", "dtype": "float"}
  3. {"unit": "KeV", "name": "energy_start", "dtype": "float", "min_value": 0.0, "tooltip": "starting energy", "label": "Energy start"}
"""


class MacroForm(Qt.QWidget):
    """
    A form widget designed to execute a macro/function with a specified set of
    arguments and name.

    The argument information is given through the meth:`setArguments` method.
    This method can receive a sequence of class:`Argument` or string.
    If string is given, the widget tries to interpret it as a json encoded
    argument information. A valid json encoded object is a dictionary
    containning the same keys as the class:`Argument` object constructor.
    Example::

        from taurus.external.qt import Qt
        from esrf.taurus.qt.qtgui.macro import MacroForm
    
        app = Qt.QApplication([])

        widget = MacroForm()
        args = [
            json.dumps(dict(name="energy_start", label="Energy start",
                            dtype="float", min_value=0.0, unit="KeV",
                            tooltip="starting energy")),
            Argument(name='energy_end', label="Energy end", dtype='float',
                     min_value=0.0, unit="KeV", tooltip="ending energy"),
            Argument(name="nb_points", label="Nb. points", dtype='int',
                     min_value=1, tooltip="number of points"),
            Argument(name="integration_time", label="Int. time", dtype=float,
                     min_value=0.0, unit="s", tooltip="integration time"),
            Argument(name="channel", label="Channel", dtype=[(0, "None"), (1, "Mca"), (2, "XIA")],
                     default_value=1, tooltip="type of channel"),
            Argument(name="channel_start", label="Start chan.", dtype=str),
            Argument(name="channel_end", label="End chan.", dtype=str),
        ]
        widget.setMacroName("zapenergy")
        widget.setArguments(args)
    
        def onRunClicked(self, checked=False):
            args = [w3.macroName] + w3.getArgumentValueList()
            print "run macro: '{0}'".format(" ".join(map(str, args)))
        w3.runClicked.connect(onRunClicked)

    Notice that the widget will not perform any action when the run button is
    clicked. It is up to the programmer to connect the runClicked signal to a
    proper slot which handles the action.
    """
    
    runClicked = Qt.Signal(bool)
    macroNameChanged = Qt.Signal(str)
    
    def __init__(self, parent=None, designMode=False):
        self.__name = ""
        self.__arguments = []
        self.__argumentWidgets = []
        self.ui = _UI()
        Qt.QWidget.__init__(self, parent)
        layout = Qt.QFormLayout(self)
        layout.setMargin(3)
        layout.setSpacing(3)
        
        icon = getIcon(":/actions/media_playback_start.svg")
        self.ui.runButton = Qt.QPushButton(icon, "")
        layout.addRow(self.ui.runButton)
        self.ui.runButton.clicked.connect(self.runClicked)
        
    def getMacroName(self):
        return self.__name

    Qt.Slot(str)
    def setMacroName(self, name):
        self.setWindowTitle(name)
        self.__name = name
        self.macroNameChanged.emit(name)

    def resetMacroName(self):
        self.setMacroName("")

    macroName = Qt.Property(str, getMacroName, setMacroName, resetMacroName)

    def _updateArguments(self):
        layout = self.layout()
        # remove the run button first
        layout.takeAt(layout.indexOf(self.ui.runButton))
        self.ui.runButton.setParent(None)
        # remove all old arguments
        self.__argumentWidgets = argw = []
        while layout.count():
            widget = layout.takeAt(0).widget()
            widget.setParent(None)
            widget.deleteLater()
        # add new arguments
        for argument in self.__arguments:
            label = argument.createLabelWidget()
            field = argument.createFieldWidget()
            layout.addRow(label, field)
            argw.append((argument, label, field))
        # add back the run button
        layout.addRow(self.ui.runButton)

    def getWidgetArguments(self):
        """sequence of (argument, label widget, field widget)"""
        return self.__argumentWidgets
        
    def getArguments(self):
        return self.__arguments

    def getArgumentsStr(self):
        return map(str, self.__arguments)

    def _parseArgument(self, argument):
        if isinstance(argument, Argument):
            pass
        elif isinstance(argument, (str, Qt.QString)):
            argument = str(argument)
            try:
                argument = Argument(**json.loads(argument))
            except:
                argument = Argument(name=argument, tooltip=argument)
        elif isinstance(argument, dict):
            argument = Argument(**argument)
        return argument
    
    Qt.Slot("QStringList")
    def setArguments(self, arguments):
        self.__arguments = args = []
        for argument in arguments:
            argument = self._parseArgument(argument)
            args.append(argument)
        self._updateArguments()

    def resetArguments(self):
        self.setArguments(())

    arguments = Qt.Property("QStringList", getArgumentsStr, setArguments,
                            resetArguments, doc=_ARG_DOC)

    def getRunButtonVisible(self):
        return self.ui.runButton.isVisible()

    def setRunButtonVisible(self, visible):
        self.ui.runButton.setVisible(visible)

    def resetRunButtonVisible(self):
        self.setRunButtonVisible(True)

    runButtonVisible = Qt.Property(bool, getRunButtonVisible,
                                   setRunButtonVisible, resetRunButtonVisible)

    def getArgumentValueList(self):
        result = []
        for argument, _, fieldWidget in self.getWidgetArguments():
            value = _getWidgetValue(fieldWidget)
            result.append(value)
        return result

    def getCommandLineList(self):
        return [self.macroName] + self.getArgumentValueList()

    def getCommandLine(self):
        return " ".join(map(str, self.getCommandLineList()))
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(module="taurus.qt.qtgui.esrf.macro",
                    icon=":designer/macroserver.png",
                    group="ESRF Macro Widgets")


def main():
    import taurus
    from taurus.qt.qtgui.container import QGroupWidget
    from taurus.qt.qtgui.resource import getThemeIcon

    taurus.setLogLevel(taurus.Debug)
    
    app = Qt.QApplication([])

    window = Qt.QWidget()
    windowLayout = Qt.QVBoxLayout(window)

    panel1 = QGroupWidget()
    panel1.setTitle("ascan")
    panel1.setTitleIcon(getThemeIcon("applications-system"))
    layout = panel1.content().layout()
    layout.setMargin(3)
    w1 = AScanWidget()
    layout.addWidget(w1)
    windowLayout.addWidget(panel1)

    panel2 = QGroupWidget()
    panel2.setTitle("anscan")
    panel2.setTitleIcon(getThemeIcon("applications-system"))
    layout = panel2.content().layout()
    layout.setMargin(3)    
    w2 = ANScanWidget()
    layout.addWidget(w2)
    windowLayout.addWidget(panel2)
    
    nspin = Qt.QSpinBox()
    nspin.valueChanged[int].connect(w2.setDimensions)
    def setTitle(n):
        panel2.setTitle("a{0}scan".format(n))
    nspin.valueChanged[int].connect(setTitle)
    nspin.setValue(1)
    nspin.setMinimum(1)
    layout.addWidget(nspin)
    layout.addWidget(w2)

    panel3 = QGroupWidget()
    panel3.setTitle("zapenergy")
    panel3.setTitleIcon(getThemeIcon("applications-system"))
    layout = panel3.content().layout()
    w3 = MacroForm()
    w3.setMacroName("zapenergy")
    args = [
        json.dumps(dict(name="energy_start", label="Energy start", dtype='float', min_value=0.0, unit='KeV', tooltip="starting energy")),
        Argument(name='energy_end', label="Energy end", dtype='float', min_value=0.0, unit="KeV"),
        Argument(name="nb_points", label="Nb. points", dtype='int', min_value=1),
        Argument(name="integration_time", label="Int. time", dtype=float, min_value=0.0, unit="s"),
        Argument(name="channel", label="Channel", dtype=[(0, "None"), (1, "Mca"), (2, "XIA")], default_value=1),
        Argument(name="channel_start", label="Start chan.", dtype=str),
        Argument(name="channel_end", label="End chan.", dtype=str),
    ]
    w3.setArguments(args)
    def onRunClicked(self, checked=False):
        args = [w3.macroName] + w3.getArgumentValueList()
        print "run macro: '{0}'".format(" ".join(map(str, args)))
    w3.runClicked.connect(onRunClicked)
    
    layout.addWidget(w3)
    windowLayout.addWidget(panel3)

    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
