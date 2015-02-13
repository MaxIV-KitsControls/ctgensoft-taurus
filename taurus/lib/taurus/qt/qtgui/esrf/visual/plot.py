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

import weakref

import numpy


class BaseConfig(dict):

    DefaultConfig = {
        'legend': None,
        'replace': False,
        'replot': True,
        'info': None,
        'z': None,
        'selectable': None,
    }

    def __init__(self, adapter, **kwargs):
        dict.__init__(self, self.DefaultConfig)
        self.__adapter = weakref.ref(adapter)
        self.update(kwargs)

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)
        self.__adapter().replot()


class OneDConfig(BaseConfig):

    DefaultConfig = dict(BaseConfig.DefaultConfig,
        color=None,
        symbol=None,
        linestyle=None,
        xlabel=None,
        ylabel=None,
        yaxis=None,
        xerror=None,
        yerror=None)


class TwoDConfig(BaseConfig):

    DefaultConfig = dict(BaseConfig.DefaultConfig,
#        replace=False,
        xScale=None,
        yScale=None,
        draggable=False,
        colormap=dict(name='gray', autoscale=True,
                      normalization='linear', colors=256),
        pixmap=None,
    )
    

import taurus
from taurus.core import TaurusEventType
from taurus.qt.qtcore.taurusqlistener import QObjectTaurusListener


class BaseAdapter(QObjectTaurusListener):

    ConfigClass = None

    def __init__(self, plot, parent=None, **kwargs):
        QObjectTaurusListener.__init__(self, parent=parent)
        self.__plot = plot
        self.__model = None
        self.config = self.ConfigClass(self, **kwargs)

    @property
    def _plot(self):
        return self.__plot
    
    def update(self):
        raise NotImplementedError
    
    def setModel(self, model_name):
        if self.__model:
            self.__model.removeListener(self)
        self.__model = model = taurus.Attribute(model_name)
        model.addListener(self)


class BaseOneDAdapter(BaseAdapter):

    ConfigClass = OneDConfig

    def __init__(self, *args, **kwargs):
        BaseAdapter.__init__(self, *args, **kwargs)
        self.x = ()
            
    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Config:
            return
        y = ()
        if evt_type == TaurusEventType.Error:
            x, y = (), ()
        else:
            x, y = self.x, evt_value.value
            if y is None:
                y = ()
            if len(x) != len(y):
                x = numpy.arange(len(y))
        self.x = x
        self.plot(x, y)

    def plot(self, x, y):
        raise NotImplementedError

    def getOneD(self):
        raise NotImplementedError        

    def update(self):
        self.plot(*self.getOneD(self))
        

# PyMca specific
class OneDAdapter(BaseOneDAdapter):

    def plot(self, x, y):
        self._plot.addCurve(x, y, **self.config)

    def getOneD(self):
        return self._plot.getCurve(self.config['legend'][:2])


from taurus.qt.qtgui.esrf.video_codec import data_2_raw


class BaseTwoDAdapter(BaseAdapter):

    ConfigClass = TwoDConfig
    
    NullData = numpy.ndarray((5,5), dtype=numpy.uint8,
#        buffer="\1\0\0\0\1\0\1\0\1\0\0\0\1\0\0\0\1\0\1\0\1\0\0\0\1")
         buffer='\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00')
    def __init__(self, *args, **kwargs):
        BaseAdapter.__init__(self, *args, **kwargs)
        self.__model = None

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Config:
            return
        if evt_type == TaurusEventType.Error:
            frame = self.NullData
        else:
            frame = data_2_raw(*evt_value.value)
        self.plot(frame)

    def plot(self, data):
        raise NotImplementedError
    
    def getTwoD(self):
        raise NotImplementedError

    def update(self):
        self.plot(*self.getTwoD(self))


class TwoDAdapter(BaseTwoDAdapter):

    def plot(self, data):
        self._plot.addImage(data, **self.config)

    def getTwoD(self):
        return self._plot.getImage(self.config['legend'][0])
    

class PlotConfig(dict):

    DefaultPlotConfig = {
        'title': "",
        'xLabel': 'X',
        'yLabel': 'Y',
        'keepAspectRatio': False,
        'enableActiveCurveHandling': False,
        'flipXaxis': False,
        'flipYaxis': False,
        'logXaxis': False,
        'logYaxis': False,
        'grid': 1,
        'plotPoints': False,
        'plotLines': True,
    }

    def __init__(self, plot, **kwargs):
        dict.__init__(self, self.DefaultPlotConfig)
        self.__plot = weakref.ref(plot)
        self.update(kwargs)

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)
        
        self.__plot().replot()


from taurus.external.qt import Qt
from taurus.qt.qtgui.util.qtdesigner import QtDesignable
from PyMca5.PyMcaGraph.Plot import Plot

OpenGLBackend = "opengl"


class QPlotWidget(Qt.QMainWindow, Plot):

    #: Default backend
    DefaultBackend = OpenGLBackend
    
    def __init__(self, parent=None, backend=DefaultBackend, **kwargs):
        Qt.QMainWindow.__init__(self, parent)
        Plot.__init__(self, parent, backend=backend)
        if parent:
            self.setWindowFlags(Qt.Qt.Widget)
        plot_widget = self.getWidgetHandle()
        if backend == OpenGLBackend:
            plot_widget.format().setAlpha(True)
        self.setCentralWidget(plot_widget)
#        self.config = PlotConfig(self, **kwargs)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return dict(label="Plot Widget",
                    module="taurus.qt.qtgui.esrf.visual",
                    icon=":designer/macroserver.png",
                    group="ESRF Widgets")

    Qt.Slot("QStringList")
    def setTools(self, tools):
        pass

    def getTools(self):
        return self.__tools


    yAxisInvert = Qt.Property(bool, Plot.isYAxisInverted, Plot.invertYAxis)

    xAxisLabel = Qt.Property(str, Plot.getGraphXLabel, Plot.setGraphXLabel)
    yAxisLabel = Qt.Property(str, Plot.getGraphYLabel, Plot.setGraphYLabel)    

    xAxisAutoScale = Qt.Property(bool, Plot.isXAxisAutoScale, Plot.setXAxisAutoScale)
    yAxisAutoScale = Qt.Property(bool, Plot.isYAxisAutoScale, Plot.setYAxisAutoScale)
    
    xAxisLogarithmic = Qt.Property(bool, Plot.isXAxisLogarithmic, Plot.setXAxisLogarithmic)
    yAxisLogarithmic = Qt.Property(bool, Plot.isYAxisLogarithmic, Plot.setYAxisLogarithmic)
    
#    markerMode = Qt.Property(bool, Plot.isMarkerModeEnabled, Plot.enableMarkerMode)

    title = Qt.Property(str, Plot.getGraphTitle, Plot.setGraphTitle)

    drawMode = Qt.Property(bool, Plot.isDrawModeEnabled, Plot.setDrawModeEnabled)

#    keepAspectRatio = Qt.Property(bool, Plot.isKeepDataAspectRatio, Plot.keepDataAspectRatio)
#    grid = Qt.QProperty(bool, Plot.isGridShown, Plot.showGrid)
    

def main():
    app = Qt.QApplication([])
    panel = Qt.QWidget()
    palette = Qt.QPalette(panel.palette())
    palette.setColor(Qt.QPalette.Window, Qt.QColor(0,255,0))
    panel.setAutoFillBackground(True)
    panel.setPalette(palette)
    layout = Qt.QVBoxLayout(panel)
    w = QPlotWidget()
    layout.addWidget(w)
    y = numpy.random.random(1000)
    x = numpy.arange(len(y))
    w.addCurve(x, y, replace=False, replot=False, linestyle="", symbol="s", z=3,
               xlabel="Curve 1 X", ylabel="Curve 1 Y") #, fill=True)

    panel.show()
    app.exec_()

if __name__ == "__main__":
    main()
