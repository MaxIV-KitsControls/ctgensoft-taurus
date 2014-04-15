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

from taurus.qt import Qt

from pyqtgraph import ImageItem, ViewBox, GridItem, ROI
from pyqtgraph import GraphicsView, GraphicsLayoutWidget

from taurus.core import TaurusEventType
from taurus.core.util.codecs import CodecFactory
from taurus.qt.qtgui.base import TaurusBaseComponent

Signal = Qt.pyqtSignal


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


class VideoItemMixin(TaurusBaseComponent):

    def __init__(self):
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        self.data_fps = QFreqCounter()
        self.paint_fps = QFreqCounter()
        
        
class VideoItem(ImageItem, VideoItemMixin):

    frameChanged = Qt.Signal(object)
    
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        ImageItem.__init__(self, *args, **kwargs)
        VideoItemMixin.__init__(self)
        self.frameChanged.connect(self.onFrameChanged)
        if model is not None:
            self.setModel(model)

    def toFrame(self, value):
        # Ugly hack: import PyTango
        try:
            from PyTango import DevEncoded  #@todo: replace this (Tango-centric).
        except:
            DevEncoded = 28 #@todo: hardcoded fallback to be replaced when the data types are handled in Taurus

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
               
        self.data_fps += 1
        self.frameChanged.emit(frame)
        return frame
        
    def onFrameChanged(self, frame):
        self.setImage(frame)


class VideoGraphicsView(GraphicsView):

    def __init__(self, *args, **kwargs):
        GraphicsView.__init__(self, *args, **kwargs)
        self.__view_box = ViewBox(border='r', lockAspect=True)
        self.__grid = GridItem()
        self.__view_box.addItem(self.__grid)
        self.setCentralItem(self.__view_box)

    def addModel(self, *args, **kwargs):
        roi = ROI((0,0), removable=True)
        self.__view_box.addItem(roi)
        video_item = VideoItem(*args, **kwargs)
        video_item.setParentItem(roi)

        def onFrameChanged(data):
            rw, rh = roi.size()
            dh, dw = data.shape
            if rw != dw or rh != dh:
                print "resize_roi"
                roi.setSize(dw, dh)

        def onRemoveVideo():
            roi.sigRemoveRequested.disconnect(onRemoveVideo)
            video_item.frameChanged.disconnect(onFrameChanged)
            video_item.setModel(None)
            self.__view_box.removeItem(roi)
            
        roi.sigRemoveRequested.connect(onRemoveVideo)
        video_item.frameChanged.connect(onFrameChanged)
        return video_item


class VideoGraphicsWindow(GraphicsLayoutWidget):

    def __init__(self, *args, **kwargs):
        GraphicsLayoutWidget.__init__(self, *args, **kwargs)
        
        
    
def main():
    import sys

    app = Qt.QApplication([])
    models = sys.argv[1:]

    window = Qt.QWidget()
    layout = Qt.QVBoxLayout(window)
    view = VideoGraphicsView()
    layout.addWidget(view, 1)

    for model in models:
#        dataFreqLabel = limavideo.ValueLabel(fmt="%s data freq {value:.1f} data/s" % model)
#        paintFreqLabel = limavideo.ValueLabel(fmt="%s paint freq {value:.1f} paint/s" % model)
#        layout.addWidget(dataFreqLabel, 0)
#        layout.addWidget(paintFreqLabel, 0)

        video_item = view.addModel(model=model)
#        video_item.data_fps.freqChanged.connect(dataFreqLabel.setValue)
#        video_item.paint_fps.freqChanged.connect(paintFreqLabel.setValue)
        
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
