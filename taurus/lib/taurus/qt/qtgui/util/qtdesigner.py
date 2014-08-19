# -*- coding: utf-8 -*-
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2014 European Synchrotron Radiation Facility, Grenoble, France
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

"""utilities to make widgets designable"""

import inspect
import functools


def QtDesignable(klass=None, **kwargs):
    """
    A class decorator intended to be used in a Qt.QWidget to make it
    qt designable (i.e. to appear in QtDesigner widget catalog).

    It accepts the same arguments as the dictionary keys returned by
    TaurusBaseWidget.getQtDesignerPluginInfo.

    Example::
        from taurus.external.qt import Qt
        from taurus.qt.qtgui.util import QtDesignable

        @QtDesignable
        class MyFirstWidget(Qt.QWidget):
            '''
            A widget that will appear in the taurusdesigner
            '''

            def __init__(self, parent=None):
                Qt.QWidget.__init__(self, parent)
                # my stuff here


        @QtDesignable(icon=':/folder.png', group='My Widgets',
                      subclassable=False, tooltip='My second widget',
                      whatsthis='my special second widget')
        class MySecondWidget(Qt.QWidget):
            '''
            A widget that will appear in the taurusdesigner with
            a fancy icon, in my personal group box. Also the
            subclasses of this widget will not appear in the
            taurusdesigner (unless they have their own QtDesignable
            decorator)
            '''

            def __init__(self, parent=None):
                Qt.QWidget.__init__(self, parent)
                # my stuff here

    .. warning::
        This decorator will overload your existing
        ``getQtDesignerPluginInfo`` class method.

    :param module:
        full python module name
        [default: inspect.getmodule(klass).__name__]
    :type module: str
    :param icon:
        icon name or a Qt.QIcon [default: ':/designer/taurus.png']
    :type icon: str or Qt.QICon
    :param group:
        the name of the group box where the widget will appear in the
        QtDesigner [default: 'Taurus [Unclassified]']
    :type group: str
    :param container:
        tell if the widget is a container widget [default: False]
    :type container: bool
    :param tooltip:
        *tool tip* that will appear in the QtDesigner
        [default is 'A <class name>']
    :type tooltip: str
    :param whatsthis:
        *whats this* that will appear in the QtDesigner
        [default is 'This is a <class name> widget']
    :type whatsthis: str
    :param subclassable:
        tells if subclasses of the widget should also appear in the
        QtDesigner [default: True]
    """
    if klass is None:
        return functools.partial(QtDesignable, **kwargs)

    def getQtDesignerPluginInfo(cls):
        """
        Returns pertinent information in order to be able to build a
        valid QtDesigner widget plugin.

        :return: (dict) a map with pertinent designer information
        """

        kw = dict(kwargs)
        if not kw.pop("subclassable", True) and cls != klass:
            return
        dft_module = inspect.getmodule(klass).__name__
        kw["module"] = kw.get("module", dft_module)
        kw["icon"] = kw.get("icon", ":/designer/taurus.png")
        kw["group"] = kw.get("group", "Taurus [Unclassified]")
        kw["container"] = kw.get("container", False)
        return kw

    klass.getQtDesignerPluginInfo = classmethod(getQtDesignerPluginInfo)

    return klass
