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

from taurus.external.qt import Qt
from taurus.qt.qtgui.tree.qtree import ExpansionBar as _ExpansionBar
from taurus.qt.qtgui.resource import getIcon
from taurus.qt.qtgui.esrf.axis import AxisWidget
from taurus.qt.qtgui.util.qtdesigner import QtDesignable
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.action import createStandardAction, StandardAction


class ExpansionBar(_ExpansionBar):

    def onExpandAll(self):
        super(ExpansionBar, self).onExpandAll()
        self.viewWidget().expandAll()

    def onCollapseAll(self):
        super(ExpansionBar, self).onCollapseAll()
        self.viewWidget().collapseAll()

    def onExpandSelection(self):
        super(ExpansionBar, self).onExpandSelection()
        idx = self.viewWidget().currentIndex()
        if idx.isValid():
            self.viewWidget().expand(idx)

    def onCollapseSelection(self):
        super(ExpansionBar, self).onCollapseSelection()
        idx = self.viewWidget().currentIndex()
        if idx.isValid():
            self.viewWidget().collapse(idx)


class AxesWidgetItem(Qt.QTreeWidgetItem):

    def __buildAxisWidget(self, model_name):
        widget = AxisWidget()
        widget.layout().setContentsMargins(3, 0, 3, 0)
        widget.setModel(model_name)
        axis = widget.getModelObj()
        name = ""
        try:
            name = axis.getShortName()
        except:
            name = "?"
        try:
            name = axis.get_property("SpecMotor")["SpecMotor"][0]
        except:
            pass
        widget.setCustomLabel(name)
        widget.setLabelVisible(False)
        widget.setStepMenuVisible(False)
        widget.setReferencePointsMenuVisible(False)
        return widget

    def setModel(self, column, model_name):
        tree = self.treeWidget()
        widget = self.__buildAxisWidget(model_name)
        self.setSizeHint(column, widget.sizeHint())
        tree.setItemWidget(self, column, widget)

    def setModels(self, models):
        if isinstance(models, (list, tuple)):
            m = {}
            for column, model_name in enumerate(models):
                if model_name:
                    m[column] = model_name
            models = m
        for column, model_name in models.items():
            self.setModel(column, model_name)


@UILoadable(with_ui='ui')
@QtDesignable(group="ESRF Widgets", icon=":designer/motor.png")
class AxesTree(Qt.QMainWindow):

    def __init__(self, parent=None, flags=0, designMode=False):
        if parent is not None:
            flags |= Qt.Qt.Widget
        Qt.QMainWindow.__init__(self, parent=None,
                                flags=Qt.Qt.WindowFlags(flags))
        if parent is not None:
            self.setParent(parent)
        self.loadUi()
        ui = self.ui

        ui.print_action = createStandardAction(StandardAction.Print)
        ui.print_action.setToolTip("Print axes positions")
        ui.print_action.setStatusTip("Prints axes positions")
        ui.main_toolbar.addAction(ui.print_action)

        ui.save_action = createStandardAction(StandardAction.SaveAs)
        ui.save_action.setToolTip("Save axes positions to a file")
        ui.save_action.setStatusTip("Saves axes positions to a file")
        ui.main_toolbar.addAction(ui.save_action)

        ui.copy_clipboard_action = createStandardAction(StandardAction.Copy)
        ui.copy_clipboard_action.setToolTip("Copy axes positions to clipboard")
        ui.copy_clipboard_action.setStatusTip("Copies axes positions to clipboard")
        ui.main_toolbar.addAction(ui.copy_clipboard_action)

        expansion_bar = ExpansionBar(view=self.ui.tree)
        self.addToolBar(expansion_bar)

    def sizeHint(self):
        return Qt.QSize(512, 512)


def main():
    import sys
    slits = ["PS{0}".format(i) for i in range(1, 3)]
    slits += ["SS{0}".format(i) for i in range(1, 8)]

    app = Qt.QApplication(sys.argv)
    tree_window = AxesTree()
    tree = tree_window.ui.tree
    tree.setColumnCount(2)
    tree.setHeaderLabels(["Item", "Axis"])
    header = tree.header()
    header.setResizeMode(0, Qt.QHeaderView.ResizeToContents)
    header.setResizeMode(1, Qt.QHeaderView.Stretch)
    U35 = Qt.QTreeWidgetItem(tree, ["U35U", ""])
    for name, axis in (("Energy", "th"), ("Gap", "tth"), ("Harmonic", "chi")):
        item = AxesWidgetItem(U35)
        item.setText(0, name)
        item.setTextAlignment(0, Qt.Qt.AlignVCenter | Qt.Qt.AlignRight)
        item.setModel(1, axis)


    tree_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
