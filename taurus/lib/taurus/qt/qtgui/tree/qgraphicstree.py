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

"""A tree widget representing QGraphicsItem hierarchy (for development purposes).

The most common use case of this widget is to debug applications which may have
*zombie* widgets lying around when some widget is removed, reparented in a
dynammic GUI.

Example::

    from taurus.external.qt import Qt, Qt
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.gui.tree.qtreeobject import QGraphicsItemTreeWidget

    app = TaurusApplication()

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

    inspector = QGraphicsItemTreeWidget(graphItem=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()
"""

__all__ = ["QGraphicsItemTreeWidget"]

import weakref

import taurus
from taurus.external.enum import Enum
from taurus.external.qt import Qt
from taurus.qt.qtgui.tree.qtree import QBaseTreeWidget
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from taurus.qt.qtcore.model import TaurusBaseModel, TaurusBaseTreeItem


class Representation(Enum):
    "possible displays of a QGraphicsItem"
    ClassName, ObjectName, FullName, ZValue = range(4)


QR = Representation

__DEFAULT_FILTER_CLASSES = Qt.QPropertyAnimation, Qt.QPanGesture


def _filter(graphItem):
    # Filter
    if isinstance(graphItem, __DEFAULT_FILTER_CLASSES):
        return
    return graphItem


def _buildQGraphicsItemsAsDict(graphItem, container, ffilter=_filter):

    container[graphItem] = childs = {}
    for child in graphItem.childItems():
        # Filter
        if not ffilter(child) is None:
            _buildQGraphicsItemsAsDict(child, childs, ffilter=ffilter)


def getQGraphicsItemTreeAsDict(graphItem=None, ffilter=_filter):

    if graphItem is None:
        app = Qt.QApplication.instance()
        graphItems = [app] + app.topLevelWidgets()
    else:
        graphItems = [graphItem]

    tree = {}
    for graphItem in graphItems:
        if not ffilter(graphItem) is None:
            _buildQGraphicsItemsAsDict(graphItem, tree, ffilter=ffilter)

    return tree


def _buildQGraphicsItemsAsList(graphItem, container, ffilter=_filter):

    children = graphItem.childItems()
    node = graphItem, []
    container.append(node)
    for child in children:
        if not ffilter(child) is None:
            _buildQGraphicsItemsAsList(child, node[1], ffilter=ffilter)


def getQGraphicsItemTreeAsList(graphItem=None, ffilter=_filter):

    if graphItem is None:
        app = Qt.QApplication.instance()
        graphItems = [app] + app.topLevelWidgets()
    else:
        graphItems = [graphItem]

    tree = []
    for graphItem in graphItems:
        if not ffilter(graphItem) is None:
            _buildQGraphicsItemsAsList(graphItem, tree, ffilter=ffilter)

    return tree

getQGraphicsItemTree = getQGraphicsItemTreeAsList


def _getQGraphicsItemStr(graphItem, representation):
    if graphItem is None:
        return 'Null'

    if representation == Representation.ClassName:
        return graphItem.__class__.__name__

    try:
        objectName = str(graphItem) # graphItem.__class__.__name__ # objectName()
    except RuntimeError:
        taurus.error("error accessing object %s", graphItem)
        taurus.debug("details: ", exc_info=1)
        if representation == Representation.ClassName:
            return str(grapItem)
        else:
            return "> ERROR! <"

    if representation == Representation.ObjectName:
        return objectName
    elif representation == Representation.FullName:
        className = graphItem.__class__.__name__ #metaObject().className()
        return '{0}("{1}")'.format(className, objectName)
    elif representation == Representation.ZValue:
        return str(graphItem.zValue())
        
    return str(graphItem)


def _buildQGraphicsItemStr(node, str_tree,
                       representation=Representation.ClassName,
                       ffilter=_filter):

    graphItem, children = node
    str_node = _getQGraphicsItemStr(graphItem, representation)
    str_children = []
    if len(children):
        str_tree.append((str_node, str_children))
        for child in children:
            if ffilter(child):
                _buildQGraphicsItemStr(child, str_children,
                                       representation=representation,
                                       ffilter=ffilter)
    else:
        str_tree.append(str_node)


def getQGraphicsItemTreeStr(graphItem=None,
                         representation=Representation.ClassName,
                         ffilter=_filter):

    tree, str_tree = getQGraphicsItemTree(graphItem=graphItem, ffilter=ffilter), []
    for e in tree:
        _buildQGraphicsItemStr(e, str_tree, representation=representation,
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


def getQGraphicsItemIcon(qo):
    if isinstance(qo, Qt.QGraphicsItem):
        name = "widget"
        if isinstance(qo, Qt.QGraphicsEllipseItem):
            name = "ledred"
        elif isinstance(qo, Qt.QGraphicsPathItem):
            name = "listbox"
        elif isinstance(qo, Qt.QGraphicsPolygonItem):
            name = "doublespinbox"
        elif isinstance(qo, Qt.QGraphicsRectItem):
            name = "frame"
        elif isinstance(qo, Qt.QGraphicsSimpleTextItem):
            name = "label"
        elif isinstance(qo, Qt.QGraphicsItemGroup):
            name = "widgetstack"
        elif isinstance(qo, Qt.QGraphicsLineItem):
            name = "line"
        elif isinstance(qo, Qt.QGraphicsTextItem):
            name = "textedit"
        elif isinstance(qo, Qt.QGraphicsWidget):
            name = "widget"
        elif isinstance(qo, Qt.QGraphicsProxyWidget):
            name = "frame"
        elif isinstance(qo, Qt.QGraphicsPixmapItem):
            name = "graphicsview"
        elif isinstance(qo, Qt.QGraphicsObject):
            name = "mdiarea"
        return getIcon(":/designer/" + name + ".png")
    return getThemeIcon("emblem-system")


class QGraphicsItemTreeInfoItem(TaurusBaseTreeItem):
    """
    Tree object item (to be used by a Tree Model
    """
    def __init__(self, model, data, parent=None):
        TaurusBaseTreeItem.__init__(self, model, data, parent=parent)
        if data is not None:
            self.graphItem = weakref.ref(data)
            dat = (_getQGraphicsItemStr(data, QR.ClassName),
                   _getQGraphicsItemStr(data, QR.ZValue))
            self.setData(0, dat)
        self.__toolTip = _getQGraphicsItemStr(data, QR.FullName)
        self.__icon = getQGraphicsItemIcon(data)

    def toolTip(self, index):
        return self.__toolTip

    def icon(self, index):
        if index.column() == 0:
            return self.__icon


class QGraphicsItemTreeInfoModel(TaurusBaseModel):
    """
    Model representation of a tree of QGraphicsItems
    """
    ColumnNames = "Item", "ZValue"
    ColumnRoles = (QR.ClassName,), QR.ZValue

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
    def _build_graphItem_item(model, parent, node):
        graphItem, children = node
        item = QGraphicsItemTreeInfoItem(model, graphItem, parent)
        parent.appendChild(item)
        for child in children:
            QGraphicsItemTreeInfoModel._build_graphItem_item(model, item, child)

    def setupModelData(self, qobject):
        if qobject is None:
            return
        if isinstance(qobject, Qt.QGraphicsScene):
            items = [item for item in qobject.items() if item.parentItem() is None]
        elif isinstance(qobject, Qt.QGraphicsView):
            items = [item for item in qobject.scene().items() if item.parentItem() is None]
        elif isinstance(qobject, Qt.QGraphicsItem):
            items = [qobject]

        rootItem = self._rootItem
        for item in items:
            for node in getQGraphicsItemTree(graphItem=item):
                QGraphicsItemTreeInfoModel._build_graphItem_item(self, rootItem, node)


class QGraphicsItemTreeWidget(QBaseTreeWidget):
    """
    A tree representation of the selected QGraphicsItem childs.

    The use case of this widget is to debug applications which may have *zombie*
    widgets lying around when some widget is removed, reparented in a dynammic
    GUI. Example::

    from taurus.external.qt import Qt, Qt
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.gui.tree.qtreeobject import QGraphicsItemTreeWidget

    app = TaurusApplication()

    # mw will be the QGraphicsItem to be "seen" in the Tree (along with all its
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

    inspector = QGraphicsItemTreeWidget(graphItem=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()
    """

    KnownPerspectives = {
        "Default": {
            "label":   "Default perspecive",
            "tooltip": "Graphics item tree view",
            "icon":    "",
            "model":   [QGraphicsItemTreeInfoModel],
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
    scene = Qt.QGraphicsScene()
    scene.setObjectName("mainScene")
    view = Qt.QGraphicsView(scene)
    view.setObjectName("view1")
    rect1 = scene.addRect(10, 10, 200, 100)
    rect1.setPen(Qt.QPen(Qt.Qt.green))
    rect1.setBrush(Qt.QBrush(Qt.Qt.red))

    ellipse1 = scene.addEllipse(300, 50, 180, 90)
    ellipse1.setPen(Qt.QPen(Qt.Qt.yellow))
    ellipse1.setBrush(Qt.QBrush(Qt.Qt.blue))

    group1 = Qt.QGraphicsItemGroup()
    scene.addItem(group1)
    
    rect2 = Qt.QGraphicsRectItem(10, 10, 200, 100)
    rect2.setPen(Qt.QPen(Qt.Qt.red))
    rect2.setBrush(Qt.QBrush(Qt.Qt.green))
    group1.addToGroup(rect2)
    
    ellipse2 = Qt.QGraphicsEllipseItem(300, 50, 180, 90)
    ellipse2.setPen(Qt.QPen(Qt.Qt.blue))
    ellipse2.setBrush(Qt.QBrush(Qt.Qt.yellow))
    group1.addToGroup(ellipse2)
    group1.moveBy(400, 0)
    return view, scene


def main():
    app = Qt.QApplication([])

    view, scene = __buildGUI()
    view.show()
    inspector = QGraphicsItemTreeWidget(qobject=view)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()


if __name__ == "__main__":
    main()
