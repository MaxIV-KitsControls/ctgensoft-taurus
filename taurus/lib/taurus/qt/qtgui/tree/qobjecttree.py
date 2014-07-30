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

"""A tree widget representing QObject hierarchy (for development purposes).

The most common use case of this widget is to debug applications which may have
*zombie* widgets lying around when some widget is removed, reparented in a
dynammic GUI.

Example::

    from taurus.external.qt import Qt
    from taurus.qt.gui.tree.qtreeobject import QObjectTreeWidget

    app = Qt.QApplication([])

    # mw will be the QObject to be "seen" in the Tree (along with all its
    # childs, of course)

    mw = Qt.QMainWindow()
    mw.setObjectName("main window")
    w = Qt.QWidget()
    w.setObjectName("central widget")
    mw.setCentralWidget(w)
    l = Qt.QVBoxLayout()
    w.setLayout(l)
    l1 = Qt.QLabel("H1")
    l1.setObjectName("label 1")
    l.addWidget(l1)
    l2 = Qt.QLabel("H2")
    l2.setObjectName("label 2")
    l.addWidget(l2)
    mw.show()

    inspector = QObjectTreeWidget(qobject=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()
"""

__all__ = ["QObjectTreeWidget"]

import weakref

import taurus
from taurus.external.enum import Enum
from taurus.external.qt import Qt
from taurus.qt.qtgui.tree.qtree import QBaseTreeWidget
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from taurus.qt.qtcore.model import TaurusBaseModel, TaurusBaseTreeItem


class QObjectRepresentation(Enum):
    "possible displays of a QObject"
    ClassName, ObjectName, FullName = range(3)


QR = QObjectRepresentation

__DEFAULT_FILTER_CLASSES = Qt.QPropertyAnimation, Qt.QPanGesture


def _filter(qobject):
    # Filter
    if isinstance(qobject, __DEFAULT_FILTER_CLASSES):
        return
    return qobject


def _buildQObjectsAsDict(qobject, container, ffilter=_filter):

    container[qobject] = childs = {}
    for child in qobject.children():
        # Filter
        if not ffilter(child) is None:
            _buildQObjectsAsDict(child, childs, ffilter=ffilter)


def getQObjectTreeAsDict(qobject=None, ffilter=_filter):

    if qobject is None:
        app = Qt.QApplication.instance()
        qobjects = [app] + app.topLevelWidgets()
    else:
        qobjects = [qobject]

    tree = {}
    for qobject in qobjects:
        if not ffilter(qobject) is None:
            _buildQObjectsAsDict(qobject, tree, ffilter=ffilter)

    return tree


def _buildQObjectsAsList(qobject, container, ffilter=_filter):

    children = qobject.children()
    node = qobject, []
    container.append(node)
    for child in children:
        if not ffilter(child) is None:
            _buildQObjectsAsList(child, node[1], ffilter=ffilter)


def getQObjectTreeAsList(qobject=None, ffilter=_filter):

    if qobject is None:
        app = Qt.QApplication.instance()
        qobjects = [app] + app.topLevelWidgets()
    else:
        qobjects = [qobject]

    tree = []
    for qobject in qobjects:
        if not ffilter(qobject) is None:
            _buildQObjectsAsList(qobject, tree, ffilter=ffilter)

    return tree

getQObjectTree = getQObjectTreeAsList


def _getQObjectStr(qobject, representation):
    if qobject is None:
        return 'Null'

    if representation == QObjectRepresentation.ClassName:
        return qobject.__class__.__name__

    try:
        objectName = qobject.objectName()
    except RuntimeError:
        taurus.error("error accessing object %s", qobject)
        taurus.debug("details: ", exc_info=1)
        if representation == QObjectRepresentation.ClassName:
            return qobject.__class__.__name__
        else:
            return "> ERROR! <"

    if representation == QObjectRepresentation.ObjectName:
        return objectName
    elif representation == QObjectRepresentation.FullName:
        className = qobject.metaObject().className()
        return '{0}("{1}")'.format(className, objectName)
    return str(qobject)


def _buildQObjectStr(node, str_tree,
                       representation=QObjectRepresentation.ClassName,
                       ffilter=_filter):

    qobject, children = node
    str_node = _getQObjectStr(qobject, representation)
    str_children = []
    if len(children):
        str_tree.append((str_node, str_children))
        for child in children:
            if ffilter(child):
                _buildQObjectStr(child, str_children,
                                   representation=representation,
                                   ffilter=ffilter)
    else:
        str_tree.append(str_node)


def getQObjectTreeStr(qobject=None,
                         representation=QObjectRepresentation.ClassName,
                         ffilter=_filter):

    tree, str_tree = getQObjectTree(qobject=qobject, ffilter=ffilter), []
    for e in tree:
        _buildQObjectStr(e, str_tree, representation=representation,
                           ffilter=ffilter)
    return str_tree


def _getWidgetLayout(widget):
    if not isinstance(widget, Qt.QWidget):
        return
    parent = widget.parent()
    if parent is None or not isinstance(parent, Qt.QWidget):
        return
    layout = parent.layout()
    if layout.indexOf(widget) < 0:
        return
    return layout


def getQObjectIcon(qo):
    if isinstance(qo, Qt.QWidget):
        name = "widget"
        if isinstance(qo, Qt.QLabel):
            name = "label"
        elif isinstance(qo, Qt.QComboBox):
            name = "combobox"
        elif isinstance(qo, Qt.QDoubleSpinBox):
            name = "doublespinbox"
        elif isinstance(qo, Qt.QDateEdit):
            name = "dateedit"
        elif isinstance(qo, Qt.QTimeEdit):
            name = "timeedit"
        elif isinstance(qo, Qt.QDateTimeEdit):
            name = "datetimeedit"
        elif isinstance(qo, Qt.QLineEdit):
            name = "linedit"
        elif isinstance(qo, Qt.QPlainTextEdit):
            name = "plaintextedit"
        elif isinstance(qo, Qt.QTextEdit):
            name = "textedit"
        elif isinstance(qo, Qt.QTabWidget):
            name = "tabwidget"
        elif isinstance(qo, Qt.QRadioButton):
            name = "radiobutton"
        elif isinstance(qo, Qt.QPushButton):
            name = "pushbutton"
        elif isinstance(qo, Qt.QToolButton):
            name = "toolbutton"
        elif isinstance(qo, Qt.QCheckBox):
            name = "checkbox"
        elif isinstance(qo, Qt.QToolBox):
            name = "toolbox"
        elif isinstance(qo, Qt.QTreeView):
            name = "tree"
        elif isinstance(qo, Qt.QTableView):
            name = "table"
        elif isinstance(qo, Qt.QListView):
            name = "listbox"
        elif isinstance(qo, Qt.QStackedWidget):
            name = "widgetstack"
        elif isinstance(qo, Qt.QDockWidget):
            name = "dockwidget"
        elif isinstance(qo, Qt.QDockWidget):
            name = "dockwidget"
        elif isinstance(qo, Qt.QCalendarWidget):
            name = "calendarwidget"
        elif isinstance(qo, Qt.QDialogButtonBox):
            name = "dialogbuttonbox"
        elif isinstance(qo, Qt.QFrame):
            name = "frame"
        elif isinstance(qo, Qt.QAbstractSpinBox):
            name = "spinbox"
        elif isinstance(qo, Qt.QAbstractButton):
            name = "pushbutton"
        elif isinstance(qo, Qt.QAbstractSlider):
            name = "hslider"
        return getIcon(":/designer/" + name + ".png")
    elif isinstance(qo, Qt.QLayout):
        name = "editform"
        if isinstance(qo, Qt.QVBoxLayout):
            name = "editvlayout"
        elif isinstance(qo, Qt.QHBoxLayout):
            name = "edithlayout"
        elif isinstance(qo, Qt.QGridLayout):
            name = "editgrid"
        elif isinstance(qo, Qt.QFormLayout):
            name = "editform"
    elif isinstance(qo, Qt.QCoreApplication):
        return getThemeIcon("applications-development")
    return getThemeIcon("emblem-system")


class QObjectTreeInfoItem(TaurusBaseTreeItem):
    """
    Tree object item (to be used by a Tree Model
    """
    def __init__(self, model, data, parent=None):
        TaurusBaseTreeItem.__init__(self, model, data, parent=parent)
        if data is not None:
            self.qobject = weakref.ref(data)
            dat = (_getQObjectStr(data, QR.ClassName),
                   _getQObjectStr(data, QR.ObjectName))
            self.setData(0, dat)
        self.__toolTip = _getQObjectStr(data, QR.FullName)
        self.__icon = getQObjectIcon(data)

    def toolTip(self, index):
        return self.__toolTip

    def icon(self, index):
        if index.column() == 0:
            return self.__icon


class QObjectTreeInfoModel(TaurusBaseModel):
    """
    Model representation of a tree of QObjects
    """
    ColumnNames = "Class", "Object name"
    ColumnRoles = (QR.ClassName,), QR.ObjectName

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)

    def role(self, column, depth=0):
        if column == 0:
            return self.ColumnRoles[column][0]
        return self.ColumnRoles[column]

    def roleIcon(self, taurus_role):
        return Qt.QIcon()

    def roleSize(self, taurus_role):
        return Qt.QSize(300, 70)

    def roleToolTip(self, role):
        return "widget information"

    @staticmethod
    def _build_qobject_item(model, parent, node):
        qobject, children = node
        item = QObjectTreeInfoItem(model, qobject, parent)
        parent.appendChild(item)
        for child in children:
            QObjectTreeInfoModel._build_qobject_item(model, item, child)

    def setupModelData(self, qobject):
        if qobject is None:
            return
        data = getQObjectTree(qobject=qobject)
        rootItem = self._rootItem
        for node in data:
            QObjectTreeInfoModel._build_qobject_item(self, rootItem, node)


class QObjectTreeWidget(QBaseTreeWidget):
    """
    A tree representation of the selected QObject childs.

    The use case of this widget is to debug applications which may have *zombie*
    widgets lying around when some widget is removed, reparented in a dynammic
    GUI. Example::

    from taurus.external.qt import Qt
    from taurus.qt.gui.tree.qtreeobject import QObjectTreeWidget

    app = Qt.QApplication([])

    # mw will be the QObject to be "seen" in the Tree (along with all its
    # childs, of course)

    mw = Qt.QMainWindow()
    mw.setObjectName("main window")
    w = Qt.QWidget()
    w.setObjectName("central widget")
    mw.setCentralWidget(w)
    l = Qt.QVBoxLayout()
    w.setLayout(l)
    l1 = Qt.QLabel("H1")
    l1.setObjectName("label 1")
    l.addWidget(l1)
    l2 = Qt.QLabel("H2")
    l2.setObjectName("label 2")
    l.addWidget(l2)
    mw.show()

    inspector = QObjectTreeWidget(qobject=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()
    """

    KnownPerspectives = {
        "Default": {
            "label":   "Default perspecive",
            "tooltip": "QObject tree view",
            "icon":    "",
            "model":   [QObjectTreeInfoModel],
        },
    }

    DftPerspective = "Default"

    def __init__(self, parent=None, with_navigation_bar=True,
                 with_filter_widget=True, perspective=None, proxy=None,
                 qobject=None):
        QBaseTreeWidget.__init__(self, parent,
                                 with_navigation_bar=with_navigation_bar,
                                 with_filter_widget=with_filter_widget,
                                 perspective=perspective, proxy=proxy)
        qmodel = self.getQModel()
        qmodel.setDataSource(qobject)


def __buildGUI():
    mw = Qt.QMainWindow()
    mw.setObjectName("mainWindow")
    w = Qt.QWidget()
    w.setObjectName("centralWidget")
    mw.setCentralWidget(w)
    l = Qt.QVBoxLayout()
    l.setObjectName("verticalLayout")
    w.setLayout(l)
    l1 = Qt.QLabel("H1")
    l1.setObjectName("label1")
    l.addWidget(l1)
    l2 = Qt.QLabel("H2")
    l2.setObjectName("label2")
    l.addWidget(l2)
    mw.show()
    return mw


def main():
    app = Qt.QApplication([])

    w = __buildGUI()
    w.show()
    inspector = QObjectTreeWidget(qobject=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()


if __name__ == "__main__":
    main()
