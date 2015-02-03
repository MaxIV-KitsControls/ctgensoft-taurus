#!/usr/bin/env python

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

""" Every TaurusWidget should have the following Qt Designer extended capabilities:

  - Task menu:
    it means when you right click on the widget in the designer, it will have
    the following additional items:
    - 'Edit model...' - opens a customized dialog for editing the widget model
    
  - Property Sheet:
    it means that in the Qt Designer property sheet it will have the following
    properties customized:
    - 'model' - will have a '...' button that will open a customized dialog for
      editing the widget model (same has 'Edit model...' task menu item
"""

import sys
import inspect

from taurus.external.qt import Qt
from taurus.external.qt import QtDesigner

from taurus.core.util.log import Logger


Q_TYPEID_MAP = {'QPyDesignerContainerExtension':     'com.trolltech.Qt.Designer.Container',
                'QPyDesignerPropertySheetExtension': 'com.trolltech.Qt.Designer.PropertySheet',
                'QPyDesignerTaskMenuExtension':      'com.trolltech.Qt.Designer.TaskMenu',
                'QPyDesignerMemberSheetExtension':   'com.trolltech.Qt.Designer.MemberSheet'}

def Q_TYPEID(class_type):
    return Q_TYPEID_MAP[class_type]


designer_logger = Logger("PyQtDesigner")


def _importPackage(name):
    __import__(name)
    return sys.modules[name]


def setWidgetProperty(widget, name, value):
    form = QtDesigner.QDesignerFormWindowInterface.findFormWindow(widget)
    form.cursor().setWidgetProperty(widget, name, value)


class BaseTaurusTaskMenu(QtDesigner.QPyDesignerTaskMenuExtension):
    """
    Base taurus task menu. Stores the widget in the widget member.
    Subclass it to get a proper task menu.
    """

    def __init__(self, widget, parent):
        QtDesigner.QPyDesignerTaskMenuExtension.__init__(self, parent)
        self.widget = widget


class TaurusModelTaskMenu(BaseTaurusTaskMenu):
    """
    Taurus task menu with a *Choose model...* menu item which pops up a
    taurus model chooser.
    """

    def __init__(self, widget, parent):
        BaseTaurusTaskMenu.__init__(self, widget, parent)

        self.chooseModelAction = Qt.QAction("Choose model...", self,
                                            triggered=self.__onEditModel)

    def preferredEditAction(self):
        return self.chooseModelAction

    def taskActions(self):
        return [self.chooseModelAction]

    def __onEditModel(self):
        from taurus.qt.qtgui.panel import TaurusModelChooser
        dialog = TaurusModelChooser.modelChooserDlg

        model, ok = dialog(singleModel=True, windowTitle="Choose widget model")

        if ok and model:
            model = model[0]
            # need to take the scheme out to prevent designer from creating
            # a real tango model instead of simulation
            model = model.rpartition("://")[-1]
            setWidgetProperty(self.widget, "model", model)


class TaurusWidgetExtensionFactory(QtDesigner.QExtensionFactory):
    """Extension factory for taurus widgets"""

    def __init__(self, parent = None):
        QtDesigner.QExtensionFactory.__init__(self, parent)

    @staticmethod
    def _getClass(widget, name):
        if isinstance(name, (str, unicode, Qt.QString)):
            mod_name, _, class_name = name.rpartition(".")
            if not mod_name:
                mod_name = info['module']
            try:
                mod = _importPackage(mod_name)
            except ImportError:
                designer_logger.warning("Could not find extension %s", name)
            klass = getattr(mod, class_name)
        else:
            klass = name
        return klass

    def createExtension(self, widget, iid, parent):
        if not hasattr(widget, "getQtDesignerPluginInfo"):
            return

        info = widget.getQtDesignerPluginInfo()
        is_menu = iid == Q_TYPEID("QPyDesignerTaskMenuExtension")
        if is_menu:
            try:
                menu_class = info['task_menu']
            except KeyError:
                if hasattr(widget, 'setModel'):
                    menu_class = TaurusModelTaskMenu
            menu_class = self._getClass(widget, menu_class)
            return menu_class(widget, parent)


class TaurusWidgetPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    """TaurusWidgetPlugin"""

    Factory = None
    
    def __init__(self, parent = None):
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        self._log = Logger(self._getWidgetClassName(), designer_logger)
        self.initialized = False
    
    def initialize(self, formEditor):
        """ Overwrite if necessary. Don't forget to call this method in case you
            want the generic taurus extensions in your widget.""" 
        if self.isInitialized():
            return

        if self.Factory is None:
            manager = formEditor.extensionManager()
            if manager:
                self.Factory = TaurusWidgetExtensionFactory(manager)
                for extension in Q_TYPEID_MAP:
                    manager.registerExtensions(self.Factory, Q_TYPEID(extension))
        self.initialized = True
        
    def isInitialized(self):
        return self.initialized

    def getWidgetClass(self):
        return self.WidgetClass

    def _getWidgetClassName(self):
        return self.getWidgetClass().__name__

    def __getWidgetArgs(self, klass=None, designMode=True, parent=None):
        if klass is None:
            klass = self.getWidgetClass()
        ctor = klass.__init__
        aspec = inspect.getargspec(ctor)
        if aspec.defaults is None:
            kwspec = {}
        else:
            kwspec = dict(zip(aspec.args[-len(aspec.defaults):],
                              aspec.defaults))
        args, kwargs = [], {}
        if 'designMode' in kwspec:
            kwargs['designMode'] = designMode
        if 'parent' in kwspec:
            kwargs['parent'] = parent
        else:
            args.append(parent)
        return args, kwargs

    def createWidget(self, parent):
        try:
            klass = self.getWidgetClass()
            args, kwargs = self.__getWidgetArgs(klass=klass,
                                                designMode=True,
                                                parent=parent)
            w = klass(*args, **kwargs)
        except Exception, e:
            name = self._getWidgetClassName()
            print 100*"="
            print "taurus designer plugin error creating %s: %s" % (name, str(e))
            print 100*"-"
            import traceback
            traceback.print_exc()
            w = None
        return w
    
    def getWidgetInfo(self, key, dft=None):
        if not hasattr(self, '_widgetInfo'):
            self._widgetInfo = self.getWidgetClass().getQtDesignerPluginInfo()
        return self._widgetInfo.get(key, dft)

    def getLabel(self):
        return self.getWidgetInfo('label', self.name())
    
    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return self._getWidgetClassName()
        
    def group(self):
        """ Returns the name of the group in Qt Designer's widget box that this 
            widget belongs to.
            It returns 'Taurus Widgets'. Overwrite if want another group."""
        return self.getWidgetInfo('group', 'Taurus Widgets')

    def getIconName(self):
        return self.getWidgetInfo('icon')
        
    def icon(self):
        icon = self.getWidgetInfo('icon')
        if icon is None:
            return Qt.QIcon()
        elif isinstance(icon, Qt.QIcon):
            return icon
        else:
            if not icon.startswith(":"):
                icon = ':/designer/%s' % icon
            import taurus.qt.qtgui.resource
            return taurus.qt.qtgui.resource.getIcon(icon)
    
    def domXml(self):
        name = str(self.name())
        label = self.getLabel()
        lowerName = name[0].lower() + name[1:]
        r = "<ui displayname=\"{0}\"> " \
            "<widget class=\"{1}\" name=\"{2}\" /></ui>".format(label, name,
                                                                lowerName)
        return r

    def includeFile(self):
        """Returns the module containing the custom widget class. It may include
           a module path."""
        return self.getWidgetInfo('module')

    def toolTip(self):
        tooltip = self.getWidgetInfo('tooltip')
        if tooltip is None:
            tooltip = "A %s" % self._getWidgetClassName()
        return tooltip
        
    def whatsThis(self):
        whatsthis = self.getWidgetInfo('whatsthis')
        if whatsthis is None:
            whatsthis = "This is a %s widget" % self._getWidgetClassName()
        return whatsthis
    
    def isContainer(self):
        return self.getWidgetInfo('container', False)
