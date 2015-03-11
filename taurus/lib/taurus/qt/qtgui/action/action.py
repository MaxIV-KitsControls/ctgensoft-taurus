# -*- coding: utf-8 -*-
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright (c) 2014 European Synchrotron Radiation Facility, Grenoble, France
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

"""A collection of useful taurus standard Qt actions"""

#
# To add a new action simply add a new item in the StandardAction!
#

__all__ = ["StandardAction", "createAction",
           "createStandardAction", "getStandardAction",
           "onRestart", "onFullScreen", "onAssistant", "onAbout"]

import os
from collections import namedtuple

from taurus.external.qt import Qt
from taurus.external.enum import Enum
from taurus.qt.qtgui.resource import getIcon


_AI = namedtuple("StandardActionInfo", ("name", "text", "icon_name",
                                        "shortcut", "checkable",
                                        "toolTip", "statusTip"))

_KS = Qt.QKeySequence

class StandardAction(Enum):
    """Enumeration of standard actions"""

    #: Show application help (hint use with triggered=onAssistant)
    Help = _AI("Help", "&Help", "help-contents", _KS.HelpContents, False,
               "Help", "Shows {app_name} help")

    #: Show application about dialog (hint use with triggered=onAbout)
    About = _AI("About", "&About", "help-about", "", False, "About...",
                "Shows {app_name} about information")

    #: Quits (exits) application
    Quit = _AI("Quit", "&Quit", "application-exit", _KS.Quit, False, "Quit",
               "Quits {app_name}")

    #: Toggles full screen on/off
    FullScreen =_AI("FullScreen", "&Full Screen",
                    ("view-restore", "view-fullscreen"), "", True,
                    "Full screen on/off", "Toggles full screen on/off" )

    #: Restarts application (hint use with triggered=onAssistant)
    Restart = _AI("Restart", "&Restart", "view-refresh", "", False,
                  "Restart", "Restarts {app_name}")

    #: Creates new generic document
    New = _AI("New", "&New", "document-new", _KS.New, False, "New...",
              "Creates new")

    #: Opens new generic document
    Open = _AI("Open", "&Open", "document-open", _KS.Open, False, "Open...",
               "Opens existing")

    #: Closes generic document
    Close = _AI("Close", "&Close", "document-close", _KS.Close, False, "Close",
                "Closes")

    #: Saves generic document
    Save = _AI("Save", "&Save", "document-save", _KS.Save, False, "Save",
               "Saves")

    #: Saves generic document with new name
    SaveAs = _AI("SaveAs", "Save &As", "document-save-as", _KS.SaveAs, False,
                 "Save As...", "Saves as new name")

    #: Saves all documents
    SaveAll = _AI("SaveAll", "Save A&ll", "document-save", "", False,
                  "Save All", "Saves all")

    #: Cuts data
    Cut = _AI("Cut", "Cu&t", "edit-cut", _KS.Cut, False, "Cut", "Cuts")

    #: Copies data
    Copy = _AI("Copy", "&Copy", "edit-copy", _KS.Copy, False, "Copy", "Copies")

    #: Pastes content
    Paste = _AI("Paste", "&Paste", "edit-paste", _KS.Paste, False, "Paste",
                "Pastes")

    #: Generic delete
    Delete = _AI("Delete", "&Delete", "edit-delete", _KS.Delete, False,
                 "Delete", "Deletes")

    #: Undoes action
    Undo = _AI("Undo", "Undo", "edit-undo", _KS.Undo, False, "Undo", "Undoes")

    #: Redoes action
    Redo = _AI("Redo", "Redo", "edit-redo", _KS.Redo, False, "Redo", "Redoes")

    #: Print action
    Print = _AI("Print", "Print", "document-print", _KS.Print, False,
                "Print...", "Prints document")


__standardActions = {}


def __createToggleIcon(off_icon, on_icon=None, size=64):
    if on_icon is None:
        on_icon = off_icon

    QI = Qt.QIcon
    icon = QI()
    modes = QI.Normal, QI.Active, QI.Disabled, QI.Selected
    for state, i in ((QI.Off, off_icon), (QI.On, on_icon)):
        for mode in modes:
            icon.addPixmap(i.pixmap(size, mode=mode, state=state),
                           mode=mode, state=state)
    return icon


def createAction(text, parent=None, icon=None, iconText=None,
                 toolTip=None, statusTip=None, triggered=None,
                 checkable=None, checked=None, data=None, menuRole=None,
                 shortcut=None, shortcutContext=Qt.Qt.WindowShortcut):
    """
    Create a QAction.

    :param text: action text
    :type text: str
    :param parent: action parent:
    :type parent: QObject
    :param icon: action icon
    :type icon: str or QIcon
    :param iconText: action icon text
    :type iconText: str
    :param toolTip: action tool tip
    :type toolTip: str
    :param statusTip: action status tip
    :type statusTip: str
    :param triggered: register the given callable to the action's
                      triggered signal
    :type triggered: callable
    :param checkable: tell if action is checkable. Can be bool or callable.
                    If True or callable is given, the action becomes
                    checkable. If callable is given, the callable is
                    connect to the action's toggled signal.
    :type checkable: bool or callable
    :param data: action additional data
    :type data: object
    :param menuRole: action menu role (for Mac only)
    :type menuRole: Qt.MenuRole
    :param shortcut: action shortcut
    :type shortcut: any accepted by Qt.QKeySequence
    :param shortcutContext: action shortcut context
    :type shortcutContext: Qt.QShortcutContext
    :return: a QAction customized with given arguments
    :rtype: Qt.QAction
    """
    action = Qt.QAction(text, parent)
    if triggered is not None:
        if callable(triggered):
            action.triggered.connect(triggered)
    if checkable is not None:
        if checkable:
            action.setCheckable(True)
            if checked:
                action.setChecked(True)
        if callable(checkable):
            action.checkable.connect(checkable)
    if icon is not None:
        if not isinstance(icon, Qt.QIcon):
            icon = getIcon(icon)
        action.setIcon(icon)
    if iconText is not None:
        action.setIconText(iconText)
    if shortcut is not None:
        action.setShortcut(Qt.QKeySequence(shortcut))
    if toolTip is not None:
        action.setToolTip(toolTip)
    if statusTip is not None:
        action.setStatusTip(statusTip)
    if data is not None:
        action.setData(Qt.to_qvariant(data))
    if menuRole is not None:
        action.setMenuRole(menuRole)
    action.setShortcutContext(shortcutContext)
    return action


def __toActionInfo(action_id):
    if isinstance(action_id, str):
        action_info = StandardAction[action_id].value
    if isinstance(action_id, StandardAction):
        action_info = action_id.value
    else:
        action_info = action_id
    return action_info


def createStandardAction(action_id, triggered=None, checkable=None):
    """
    Creates a standard action.

    :param action_id:
        action identifier. Can be a string or a member of
        :class:`StandardAction`.
    :type action_id: str or :class:`StandardAction`
    :param triggered: register the given callable to the action's
                      triggered signal
    :type triggered: callable
    :param checkable: register the given callable to the action's
                    toggled signal if the action is checkable. Otherwise has
                    no effect.
    :type checkable: callable
    :return: a standard QAction
    :rtype: Qt.QAction
    """
    action_info = __toActionInfo(action_id)
    if action_info.checkable:
        icon = __createToggleIcon(*map(getIcon, action_info.icon_name))
    else:
        icon = getIcon(action_info.icon_name)
    app = Qt.QApplication.instance()
    app_name = app.applicationName()
    toolTip = action_info.toolTip.format(app_name=app_name)
    statusTip = action_info.statusTip.format(app_name=app_name)
    if checkable is None:
        checkable = action_info.checkable
    return createAction(action_info.text, parent=app,
                        icon=icon, iconText=action_info.name,
                        toolTip=toolTip, statusTip=statusTip,
                        triggered=triggered, checkable=checkable,
                        shortcut=action_info.shortcut,
                        shortcutContext=Qt.Qt.ApplicationShortcut)


def getStandardAction(action_id, triggered=None, checkable=None):
    """
    Returns the standard action given by the action_id.
    Subsequence calls with the same action_id will return the same
    instance of QAction.

    :param action_id:
        action identifier. Can be a string or a member of
        :class:`StandardAction`.
    :type action_id: str or :class:`StandardAction`
    :param triggered: register the given callable to the action's
                      triggered signal
    :type triggered: callable
    :param checkable: register the given callable to the action's
                      toggled signal
    :type checkable: callable
    :return: a standard QAction
    :rtype: Qt.QAction
    """
    action_info = __toActionInfo(action_id)
    global __standardActions
    action =  __standardActions.get(action_info)
    if action is None:
        action = createStandardAction(action_info)
        __standardActions[action_info] = action
    if triggered:
        action.triggered.connect(triggered)
    if checkable:
        action.toggled.connect(checkable)
    return action


__startup_cwd = os.getcwd()
def onRestart():
    """
    Helper function to be used as a slot for the Restart action.
    Example usage::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.action import getStandardAction, StandardAction
        from taurus.qt.qtgui.action import onRestart

        app = Qt.QApplication([])
        w = Qt.QMainWindow()

        toolBar = w.addToolBar("basic")
        menuBar = w.menuBar()
        fileMenu = menuBar.addMenu("&File")

        restartAction = getStandardAction(StandardAction.Restart,
                                          triggered=onRestart)

        toolBar.addAction(restartAction)
        fileMenu.addAction(restartAction)

        w.show()
        app.exec_()
    """
    import sys
    args = sys.argv[:]
    args.insert(0, sys.executable)
    if sys.platform == 'win32':
        args = ['"%s"' % arg for arg in args]

    os.chdir(__startup_cwd)
    os.execv(sys.executable, args)


def onFullScreen(window, checked):
    """
    Helper function to be used as a slot for the FullScreen action.
    Example usage::

        from functools import partial

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.action import getStandardAction, StandardAction
        from taurus.qt.qtgui.action import onFullScreen

        app = Qt.QApplication([])
        w = Qt.QMainWindow()

        toolBar = w.addToolBar("basic")
        menuBar = w.menuBar()
        viewMenu = menuBar.addMenu("&View")

        fsAction = getStandardAction(StandardAction.FullScreen,
                                     checkable=partial(onFullScreen, w))

        toolBar.addAction(fsAction)
        viewMenu.addAction(fsAction)

        w.show()
        app.exec_()
    """
    if checked:
        window.showFullScreen()
    else:
        window.showNormal()


def onAssistant(collection_file_name):
    """
    Helper function to be used as a slot for the Help action.
    Example usage::

        from functools import partial

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.action import getStandardAction, StandardAction
        from taurus.qt.qtgui.action import onAssistant

        app = Qt.QApplication([])
        w = Qt.QMainWindow()

        toolBar = w.addToolBar("basic")
        menuBar = w.menuBar()
        helpMenu = menuBar.addMenu("&Help")

        onAssist = partial(onAssistant, "my_help.qhc")

        helpAction = getStandardAction(StandardAction.Help,
                                       triggered=onAssist)

        toolBar.addAction(helpAction)
        helpMenu.addAction(helpAction)

        w.show()
        app.exec_()
    """

    from taurus.qt.qtgui.help import Assistant
    assistant = Assistant(collection_file_name)
    assistant.start()


def onAbout(pixmap=None, html=None, text=None, modal=True, parent=None):
    """
    Helper function to be used as a slot for the About action.
    Example usage::

        from taurus.external.qt import Qt
        from taurus.qt.qtgui.action import getStandardAction, StandardAction
        from taurus.qt.qtgui.action import onAbout

        app = Qt.QApplication([])
        w = Qt.QMainWindow()

        toolBar = w.addToolBar("basic")
        menuBar = w.menuBar()
        helpMenu = menuBar.addMenu("&Help")

        aboutAction = getStandardAction(StandardAction.About,
                                        triggered=onAbout)

        toolBar.addAction(aboutAction)
        aboutMenu.addAction(aboutAction)

        w.show()
        app.exec_()
    """
    from taurus.qt.qtgui.help import AboutDialog
    about_dialog = AboutDialog(parent)
    if pixmap:
        about_dialog.setPixmap(pixmap)
    if text:
        about_dialog.setText(text)
    if html:
        about_dialog.setHtml(html)
    if modal:
        about_dialog.exec_()
    else:
        about_dialog.setModel(True)
        about_dialog.show()


def main():
    from functools import partial

    app = Qt.QApplication([])
    app.setApplicationName("TaurusActionDemo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Taurus community")
    app.setOrganizationDomain("http://www.taurus-scada.org/")
    w = Qt.QMainWindow()

    quitAction = getStandardAction(StandardAction.Quit)
    restartAction = getStandardAction(StandardAction.Restart)
    fullScreenAction = getStandardAction(StandardAction.FullScreen)
    aboutAction = getStandardAction(StandardAction.About)
    helpAction = getStandardAction(StandardAction.Help)

    quitAction.triggered.connect(w.close)
    restartAction.triggered.connect(onRestart)
    fullScreenAction.toggled.connect(partial(onFullScreen, w))
    aboutAction.triggered.connect(onAbout)

    statusBar = w.statusBar()
    menuBar = w.menuBar()
    standardToolBar = w.addToolBar("Standard")

    fileMenu = menuBar.addMenu("&File")
    fileMenu.addSeparator()
    fileMenu.addAction(restartAction)
    fileMenu.addSeparator()
    fileMenu.addAction(quitAction)

    viewMenu = menuBar.addMenu("&View")
    viewMenu.addSeparator()
    viewMenu.addAction(fullScreenAction)

    helpMenu = menuBar.addMenu("&Help")
    helpMenu.addAction(helpAction)
    helpMenu.addSeparator()
    helpMenu.addAction(aboutAction)

    standardToolBar.addAction(fullScreenAction)
    standardToolBar.addSeparator()
    standardToolBar.addAction(aboutAction)
    standardToolBar.addAction(helpAction)
    standardToolBar.addSeparator()
    standardToolBar.addAction(restartAction)
    standardToolBar.addAction(quitAction)

    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
