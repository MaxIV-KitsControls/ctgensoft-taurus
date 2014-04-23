# -*- coding: utf-8 -*-
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

""""""

import time

try:
    import ordereddict
    OrderedDict = ordereddict.OrderedDict
except ImportError:
    OrderedDict = dict

from taurus.qt import Qt

from pyqtgraph import ImageItem, ViewBox, GridItem
from pyqtgraph import GraphicsView, GraphicsLayoutWidget

from taurus.core import TaurusEventType
from taurus.core.util.codecs import CodecFactory
from taurus.qt.qtgui.base import TaurusBaseComponent

try:
    Slot = Qt.Slot
    Signal = Qt.Signal
    Property = Qt.Property
except AttributeError:
    Slot = Qt.pyqtSlot
    Signal = Qt.pyqtSignal
    Property = Qt.pyqtProperty

    
class QFreqCounter(Qt.QObject):

    freqChanged = Signal(float)
    
    def __init__(self, parent=None, freq_window=0.25):
        Qt.QObject.__init__(self, parent)
        self.__counter = 0
        self.__freq = 0.0
        self.__last_update_time = time.time()
        self.__timer_id = self.startTimer(int(freq_window*1000))

    def timerEvent(self, evt):
        now = time.time()
        dt = now - self.__last_update_time
        counter = self.__counter
        self.__counter = 0
        self.__last_update_time = now
        self.__freq = counter / dt
        self.freqChanged.emit(self.__freq)

    def __iadd__(self, n):
        self.__counter += n
        return self


class TaurusImageItem(ImageItem, TaurusBaseComponent):

    frameChanged = Qt.Signal(object)
    
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        ImageItem.__init__(self, *args, **kwargs)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self.frameChanged.connect(self.onFrameChanged)
        if model is not None:
            self.setModel(model)

    def toFrame(self, value):
        # Ugly hack: import PyTango
        #@todo: replace this (Tango-centric).
        try:
            from PyTango import DevEncoded  
        except ImportError:
            DevEncoded = 28

        dtype = value.type
        if dtype == DevEncoded:
            return CodecFactory().decode(value.value)
        raise TypeError("Unsupported video from data type '%s'" % str(dtype))
        
    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Error:
            self.error("error event on " + str(evt_src))
            return
        if evt_type == TaurusEventType.Config:
            self.debug("config event: ignored")
            return
        
        data = evt_value.value
        if data is None:
            self.debug('Ignoring event. Reason: no data')
            return
        
        try:
            frame = self.toFrame(evt_value)
        except Exception as e:
            self.info('Ignoring event. Reason: exception decoding data!')
            self.info('Details:', exc_info=1)
            return

        if frame is None or not len(frame):
            self.info('Ignoring event. Reason: empty data')
            return
               
        self.frameChanged.emit(frame)
        return frame
        
    def onFrameChanged(self, frame):
        #pyqtgraph transposes the image to we give it transposed
        view = frame.swapaxes(0, 1)[:, ::-1]
        self.setImage(view)


class TaurusGraphicsView(GraphicsView):

    def __init__(self, *args, **kwargs):
        GraphicsView.__init__(self, *args, **kwargs)
        self.__view_box = ViewBox(border='r', lockAspect=True)
        self.__grid = GridItem()
        self.__view_box.addItem(self.__grid)
        self.setCentralItem(self.__view_box)
        self.__model_items = OrderedDict()

    def getViewBox(self):
        """
        Returns the active view box
        """
        return self.__view_box

    def getGrid(self):
        """
        Returns the grid for the active view box
        """
        return self.__grid

    def getModelItems(self):
        return self.__model_items
    
    def getModelItem(self, model_name):
        return self.__model_items[model_name]

    def addModelItem(self, model_name, image_item):
        item = self._addModelItem(image_item)
        self.__model_items[model_name] = item

    def _addModelItem(self, image_item):
        """
        Add an image item to the scene. Default implementation just adds it
        to the active view box.
        Returns the actual root node that was added. In default implementation
        it is the same image item that was given as parameter.
        """
        self.getViewBox().addItem(image_item)
        return image_item

    def removeModelItems(self, names):
        viewBox = self.getViewBox()
        for name in names:
            item = self.__model_items[name]
            viewBox.removeItem(item)

    @Slot(list)
    def setModel(self, model_names):
        if model_names is None:
            model_names = []
        if isinstance(model_names, (basestring,)):
            model_names = [model_names]
        old_items, new_items = set(self.__model_items), set(model_names)
        del_items = old_items.difference(new_items)
        new_items.difference_update(old_items)
        self.removeModelItems(del_items)
        for model_name in new_items:
            item = TaurusImageItem(model=model_name)
            self.addModelItem(model_name, item)

    def getModel(self):
        return self.__model_items.keys()

    def resetModel(self):
        self.setModel(None)

    model = Property(list, getModel, setModel, resetModel)


class TaurusGraphicsWindow(GraphicsLayoutWidget):

    def __init__(self, *args, **kwargs):
        GraphicsLayoutWidget.__init__(self, *args, **kwargs)
        
        
    
def main():
    import sys

    app = Qt.QApplication([])
    models = sys.argv[1:]

    window = Qt.QWidget()
    layout = Qt.QVBoxLayout(window)
    view = TaurusGraphicsView()
    layout.addWidget(view, 1)

    view.model = models
        
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
