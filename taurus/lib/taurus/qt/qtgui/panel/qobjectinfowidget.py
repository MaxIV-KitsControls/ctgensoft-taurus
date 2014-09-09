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

"""A widget which displays/edits information about a QObject.

Example::

    from taurus.external.qt import Qt
    from qarbon.qt.gui.qobjectinfowidget import QObjectInfoWidget

    app = QApplication([])

    # mw will be the QObject to be "seen"
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

    inspector = QObjectInfoWidget(qobject=mw)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()"""

__all__ = ["QObjectInfoWidget"]

from taurus.external.qt import Qt
from taurus.qt.qtgui.resource import getThemeIcon
from taurus.qt.qtgui.panel.qpropertyeditor import QPropertyEditor
from taurus.qt.qtgui.tree.qobjecttree import QObjectTreeWidget


class QObjectInfoWidget(Qt.QWidget):
    """
    A widget which displays/edits information about a QObject. Example::

    from taurus.external.qt import Qt
    from qarbon.qt.gui.qobjectinfowidget import QObjectInfoWidget

    app = QApplication([])

    # mw will be the QObject to be "seen"
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

    inspector = QObjectInfoWidget(qobject=mw)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()
    """

    def __init__(self, parent=None, qobject=None):
        super(QObjectInfoWidget, self).__init__(parent)
        self.setWindowIcon(getThemeIcon("applications-development"))
        self.setWindowTitle("QObject Inspector")
        layout = Qt.QHBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setMargin(0)
        self.__splitter = splitter = Qt.QSplitter(Qt.Qt.Horizontal, self)
        layout.addWidget(splitter)

        self.__form = form = QPropertyEditor(parent=splitter, qobject=qobject)
        self.__tree = tree = QObjectTreeWidget(parent=splitter, qobject=qobject)
        splitter.addWidget(tree)
        splitter.addWidget(form)

        treeSelectionModel = tree.viewWidget().selectionModel()
        Qt.QObject.connect(treeSelectionModel,
            Qt.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
            self.__onSelectionChanged)

    def __onSelectionChanged(self, selected, deselected):
        indexes = selected.indexes()
        if len(indexes):
            index = indexes[0]
            qobject = index.internalPointer().qobject()
        else:
            qobject = None
        self.__form.setQObject(qobject)

    def setQObject(self, qobject):
        self.__tree.getBaseQModel().setDataSource(qobject)
        self.__form.setQObject(qobject)


def __buildGUI():
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
    return mw


def main():
    app = Qt.QApplication([])
    w = __buildGUI()
    w.show()
    inspector = QObjectInfoWidget(qobject=w)
    inspector.setAttribute(Qt.Qt.WA_QuitOnClose, False)
    inspector.show()
    app.exec_()

if __name__ == "__main__":
    main()
