#############################################################################
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
#############################################################################

"""A widget dedicated view/edit the properties of any QObject.

Example::

    from taurus.external.qt import Qt
    from taurus.qt.gui.panel.qpropertyeditor import QPropertyEditor

    app = QApplication([])
    inspector = QPropertyEditor(qobject=None)

    # watch myself... weard
    inspector.setQObject(inspector)
    inspector.show()
    app.exec_()
"""

__all__ = ["QPropertyEditor"]

import weakref

import taurus
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable


def getPropertyValueDisplay(qMetaProperty, value):
    if qMetaProperty.isEnumType():
        metaEnum = qMetaProperty.enumerator()
        return metaEnum.key(value)
    return str(value)


def getPropertyValueToolTip(qMetaProperty, value):
    if qMetaProperty.isEnumType():
        enu = qMetaProperty.enumerator()
        tooltip = "<html>A {0}<br/>".format(enu.name())
        for i in range(enu.keyCount()):
            k, v = enu.key(i), enu.value(i)
            text = "{0}: {1}<br/>".format(k, v)
            if v == value:
                text = "<b>" + text + "</b>"
            tooltip += text
        return tooltip
    return str(value)


@UILoadable(with_ui="ui")
class QPropertyEditor(Qt.QWidget):
    """
    A widget dedicated view/edit the properties of any QObject. Example::

    from taurus.external.qt import Qt
    from taurus.qt.gui.panel.qpropertyeditor import QPropertyEditor

    app = Qt.QApplication([])
    inspector = QPropertyEditor(qobject=None)

    # watch myself... weard
    inspector.setQObject(inspector)
    inspector.show()
    app.exec_()
    """

    def __init__(self, parent=None, qobject=None):
        super(QPropertyEditor, self).__init__(parent)
        self.loadUi()

        self.ui.focusButton.clicked.connect(self.__onFocus)

        self.setQObject(qobject)

    @property
    def qobject(self):
        """returns the current QObject being edited or None if no QObject is
        associated with the editor.

        :return: the current QObject being edited or None if no QObject is
                 associated with the editor
        """
        if self.__qobject is None:
            return
        return self.__qobject()

    def setQObject(self, qobject):
        """Sets the current QObject whose properties are to been seen by the
        editor.

        :param qobject: the new QObject (can be None)
        """
        ui = self.ui
        superClassName = ""
        _class = ""
        className = ""
        isWidget = False
        propCount = 0
        if qobject is None:
            self.__qobject = None
        else:
            _class = qobject.__class__.__name__
            self.__qobject = weakref.ref(qobject)
            metaObject = qobject.metaObject()
            if metaObject is not None:
                className = metaObject.className()
                superClass = metaObject.superClass()
                if superClass is not None:
                    superClassName = superClass.className()
                isWidget = qobject.isWidgetType()
                propCount = metaObject.propertyCount()

        ui.classLineEdit.setText(_class)
        ui.classNameLineEdit.setText(className)
        ui.superClassNameLineEdit.setText(superClassName)
        ui.isWidgetLineEdit.setText(str(isWidget))
        ui.focusButton.setEnabled(isWidget)

        propTree = ui.propertiesTreeWidget

        Qt.QObject.disconnect(propTree,
                        Qt.SIGNAL("itemChanged (QTreeWidgetItem*, int)"),
                        self.__onPropertyTreeChanged)
        propTree.clear()
        if propCount == 0:
            return

        metaO, props = metaObject, []
        while True:
            first, last = metaO.propertyOffset(), metaO.propertyCount()
            if first < last:
                class_props = {}
                for p_index in range(first, last):
                    metaProp = metaObject.property(p_index)
                    class_props[metaProp.name()] = metaProp
                props.insert(0, (metaO, class_props))
            metaO = metaO.superClass()
            if metaO is None:
                break

        # build tree
        for metaO, props in props:
            topItem = Qt.QTreeWidgetItem(propTree)
            topItem.setText(0, metaO.className())
            for prop_name in sorted(props.keys()):
                metaProp = props[prop_name]
                prop_type = metaProp.typeName()
                value = qobject.property(prop_name)
                prop_value = getPropertyValueDisplay(metaProp, value)
                columns = [prop_name, prop_type, prop_value]
                propItem = Qt.QTreeWidgetItem(topItem, columns)
                propItem.setFlags(propItem.flags() | Qt.Qt.ItemIsEditable)
                propItem.setData(2, Qt.Qt.UserRole, prop_name)
                propItem.setData(2, Qt.Qt.DisplayRole, value)
                propItem.setToolTip(2, getPropertyValueToolTip(metaProp,
                                                               value))

        propTree.expandToDepth(1)
        propTree.headerItem()
        Qt.QObject.connect(propTree,
                    Qt.SIGNAL("itemChanged (QTreeWidgetItem*, int)"),
                    self.__onPropertyTreeChanged)

    def __onPropertyTreeChanged(self, item, column):
        if column != 2:
            return
        qobject = self.qobject
        if qobject is None:
            taurus.warning("qobject disappeared while trying to set a property " \
                           "on it")
            return
        prop_name = item.data(column, Qt.Qt.UserRole)
        prop_value = item.data(column, Qt.Qt.DisplayRole)
        qobject.setProperty(prop_name, prop_value)

    def __onFocus(self):
        qwidget = self.qobject
        if qwidget is None:
            taurus.warning("widget disappeared while trying to set a property " \
                           "on it")
            return
        #TODO: animate somehow


def main():
    app = Qt.QApplication([])
    inspector = QPropertyEditor(qobject=None)
    # watch myself... weard
    inspector.setQObject(inspector)
    inspector.show()
    app.exec_()


if __name__ == "__main__":
    main()
