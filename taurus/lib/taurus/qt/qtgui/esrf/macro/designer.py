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

import copy

from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.resource import getIcon
from taurus.qt.qtgui.esrf.macro import Argument

from taurus.qt.qtdesigner.taurusplugin import TaurusModelTaskMenu
from taurus.qt.qtdesigner.taurusplugin import setWidgetProperty


@UILoadable(with_ui="ui")
class ArgumentEditorDialog(Qt.QDialog):

    EmptyArgument = Argument()
    UnnamedArgument = Argument(name="unnamed argument")

    def __init__(self, arguments=(), parent=None):
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        self.__setupUi(arguments)

    def __setupUi(self, arguments):
        for arg in arguments:
            self.__addArgument(arg)
        ui = self.ui
        ui.splitter.setCollapsible(0, False)
        ui.splitter.setCollapsible(1, False)
        ui.splitter.setStretchFactor(0, 0)
        ui.splitter.setStretchFactor(1, 1)
        ui.splitter.setStretchFactor(2, 1)

        ui.add_argument_button.setIcon(getIcon("list-add"))
        ui.remove_argument_button.setIcon(getIcon("list-remove"))
        ui.argument_up_button.setIcon(getIcon("go-up"))
        ui.argument_down_button.setIcon(getIcon("go-down"))

        ui.add_enum_button.setIcon(getIcon("list-add"))
        ui.remove_enum_button.setIcon(getIcon("list-remove"))        

        ui.name_lineedit.textEdited.connect(self.__onNameChanged)
        ui.dtype_combobox.currentIndexChanged.connect(self.__onDTypeChanged)
        ui.add_argument_button.clicked.connect(self.__onAddArgument)
        ui.remove_argument_button.clicked.connect(self.__onRemoveArgument)
        ui.argument_up_button.clicked.connect(self.__onArgumentUp)
        ui.argument_down_button.clicked.connect(self.__onArgumentDown)
        ui.argument_list.currentItemChanged.connect(self.__onCurrentArgumentItemChanged)

        ui.add_enum_button.clicked.connect(self.__onAddEnum)
        ui.remove_enum_button.clicked.connect(self.__onRemoveEnum)

        self.accepted.connect(self.__onAccepted)
        
    def __addArgument(self, argument, row=None):
        arg_list = self.ui.argument_list
        item = Qt.QListWidgetItem(argument.name)
        item.setData(Qt.Qt.UserRole, argument)
        item.setData(Qt.Qt.ToolTipRole, str(argument))
        if row is None:
            arg_list.addItem(item)
        else:
            arg_list.insertItem(row, item)

    def __onNameChanged(self, name):
        item = self.ui.argument_list.currentItem()
        if item:
            item.setText(name)

    def __onDTypeChanged(self, index):
        dtype = self.ui.dtype_combobox.itemText(index)
        self.ui.enum_groupbox.setVisible(dtype == 'enum')

    def __onAddArgument(self, checked=False):
        if self.ui.name_lineedit.text():
            arg = Argument()
            self.__updateArgumentFromForm(arg)
        else:
            arg = copy.copy(self.UnnamedArgument)
        self.__addArgument(arg)

    def __onRemoveArgument(self, checked=False):
        arg_list = self.ui.argument_list
        arg_list.takeItem(arg_list.currentRow())

    def __onArgumentUp(self, checked=False):
        arg_list = self.ui.argument_list
        row = arg_list.currentRow()
        item = arg_list.takeItem(row)
        arg_list.insertItem(row-1, item)
        arg_list.setCurrentRow(row-1)

    def __onArgumentDown(self, checked=False):
        arg_list = self.ui.argument_list
        row = arg_list.currentRow()        
        item = arg_list.takeItem(row)
        arg_list.insertItem(row+1, item)
        arg_list.setCurrentRow(row+1)

    def __onAddEnum(self, checked=False):
        enum_list = self.ui.enum_list
        enum_list.insertRow(enum_list.rowCount())

    def __onRemoveEnum(self, checked=False):
        enum_list = self.ui.enum_list
        enum_list.removeRow(enum_list.currentRow())

    def __onCurrentArgumentItemChanged(self, current, previous):
        ui = self.ui
        row = ui.argument_list.row(current)
        ui.remove_argument_button.setEnabled(row >= 0)
        ui.argument_up_button.setEnabled(row >= 1)
        ui.argument_down_button.setEnabled(row < ui.argument_list.count()-1)

        if previous:
            self.__updateArgumentFromForm(previous.data(Qt.Qt.UserRole))

        if current:
            arg = current.data(Qt.Qt.UserRole)
        else:
            arg = self.EmptyArgument
        self.__updateFormFromArgument(arg)
        
    def __getEnumWidgetData(self):
        table = self.ui.enum_list
        result = []
        for row in range(table.rowCount()):
            value = table.item(row, 0).text()
            label = table.item(row, 1).text()
            result.append((value, label))
        return result

    def __updateArgumentFromForm(self, arg):
        ui = self.ui
        dtype = ui.dtype_combobox.currentText()
        arg.name = ui.name_lineedit.text() or None
        if dtype == 'enum':
            arg.dtype = self.__getEnumWidgetData()
        else:
            arg.dtype = dtype
        arg.label = ui.label_lineedit.text() or None
        arg.unit = ui.unit_lineedit.text() or None
        arg.tooltip = ui.tooltip_lineedit.text() or None
        arg.statustip = ui.statustip_lineedit.text() or None        
        arg.icon = ui.icon_lineedit.text() or None
        arg.default_value = ui.default_value_lineedit.text() or None
        arg.min_value = ui.min_value_lineedit.text() or None
        arg.max_value = ui.max_value_lineedit.text() or None        

    def __updateFormFromArgument(self, arg):
        ui = self.ui
        ui.name_lineedit.setText(arg.name)
        dtype = arg.dtype
        ui.dtype_combobox.setCurrentIndex(ui.dtype_combobox.findText(dtype))
        ui.label_lineedit.setText(arg.label or "")
        ui.unit_lineedit.setText(arg.unit or "")
        ui.tooltip_lineedit.setText(arg.tooltip or "")
        ui.statustip_lineedit.setText(arg.statustip or "")
        ui.icon_lineedit.setText(arg.icon or "")
        ui.default_value_lineedit.setText(str(arg.default_value or ""))
        if arg.min_value is None:
            ui.min_value_lineedit.setText("")
        else:
            ui.min_value_lineedit.setText(str(arg.min_value))
        if arg.max_value is None:
            ui.max_value_lineedit.setText("")
        else:
            ui.max_value_lineedit.setText(str(arg.max_value))

        ui.enum_groupbox.setVisible(dtype == 'enum')
        ui.enum_list.setRowCount(0)
        if dtype == 'enum':
            for i, (value, label) in enumerate(arg.enum):
                ui.enum_list.insertRow(i)
                item = Qt.QTableWidgetItem(value)
                ui.enum_list.setItem(i, 0, item)                
                item = Qt.QTableWidgetItem(label)
                ui.enum_list.setItem(i, 1, item)

        item = ui.argument_list.currentItem()
        if item:
            item.setText(arg.name)
            item.setToolTip(str(arg))

    def __onAccepted(self):
        item = self.ui.argument_list.currentItem()
        if item:
            self.__updateArgumentFromForm(item.data(Qt.Qt.UserRole))

    def __items(self):
        arg_list = self.ui.argument_list
        return [arg_list.item(row) for row in range(arg_list.count())]
    
    def getArguments(self):
        return [item.data(Qt.Qt.UserRole) for item in self.__items()]


class MacroTaskMenu(TaurusModelTaskMenu):

    def __init__(self, widget, parent):
        TaurusModelTaskMenu.__init__(self, widget, parent)
        self.editArgumentsAction = Qt.QAction("Edit arguments...", self,
                                              triggered=self.__onEditArguments)

    def preferredEditAction(self):
        return self.editArgumentsAction

    def taskActions(self):
        actions = TaurusModelTaskMenu.taskActions(self)
        actions.insert(0, self.editArgumentsAction)
        return actions

    def __onEditArguments(self):
        dialog = ArgumentEditorDialog(self.widget.getArguments())
        result = dialog.exec_()
        if result == Qt.QDialog.Accepted:
            arguments = map(str, dialog.getArguments())
            setWidgetProperty(self.widget, "arguments", arguments)
            


def main():
    app = Qt.QApplication([])

    import json
    args = [
        Argument(name='energy_end', label="Energy end",
                 dtype='float', min_value=0.0, unit="KeV"),
        Argument(name="nb_points", label="Nb. points",
                 dtype='int', min_value=1),
        Argument(name="integration_time", label="Int. time",
                 dtype=float, min_value=0.0, unit="s"),
        Argument(name="channel", label="Channel",
                 dtype=[(0, "None"), (1, "Mca"), (2, "XIA")], default_value=1),
        Argument(name="channel_start", label="Start chan.",
                 dtype=str),
        Argument(name="channel_end", label="End chan.",
                 dtype=str),
    ]
    args = []
    w = ArgumentEditorDialog(arguments=args)
    r = w.exec_()
    if r == Qt.QDialog.Accepted:
        for i in w.getArguments():
            print i

if __name__ == "__main__":
    main()
