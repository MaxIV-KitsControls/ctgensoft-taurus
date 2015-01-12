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
###########################################################################

"""A panel that displays rectangle coordinates."""

__all__ = ["QSizeWidget", "QPointWidget", "QRectWidget",
           "QRectXYWHWidget", "QRectX1Y1X2Y2Widget",
           "QVector2DWidget", "QVector3DWidget", "QVector4DWidget",
           "QFlipHVWidget"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.external.ordereddict import OrderedDict
from taurus.external.enum import Enum
from taurus.qt.qtcore.base import Rectangle, Size, Point
from taurus.qt.qtcore.base import Vector2D, Vector3D, Vector4D
from taurus.qt.qtcore.base import FlipHV

class LabelLocation(Enum):
    Outside, Inside = range(2)


class UnitsLocation(Enum):
    Outside, Label, Inside = range(3)


class _SpinBox(Qt.QSpinBox):

    def __init__(self, parent=None):
        Qt.QSpinBox.__init__(self, parent)
        self.setMinimum(-2**31)
        self.setMaximum(2**31-1)


class _FSpinBox(Qt.QDoubleSpinBox):

    def __init__(self, parent=None):
        Qt.QDoubleSpinBox.__init__(self, parent)
        self.setMinimum(float('-inf'))
        self.setMaximum(float('+inf'))


class ValueMixin:

    DefaultValue = None
    DefaultPrefix = DefaultSuffix = ""

    def __init__(self, *args, **kwargs):
        self.__value = self.DefaultValue
        self.__prefix = self.DefaultPrefix
        self.__suffix = self.DefaultSuffix

    def getPrefix(self):
        return self.__prefix

    def setPrefix(self, prefix):
        if prefix is None:
            prefix = self.DefaultPrefix
        self.__prefix = prefix
        self._update()

    def resetPrefix(self):
        self.setPrefix(self.DefaultPrefix)

    prefix = Qt.Property(str, getPrefix, setPrefix, resetPrefix)

    def getSuffix(self):
        return self.__suffix

    def setSuffix(self, suffix):
        if suffix is None:
            suffix = self.DefaultSuffix
        self.__suffix = suffix
        self._update()

    def resetSuffix(self):
        self.setSuffix(self.DefaultSuffix)

    suffix = Qt.Property(str, getSuffix, setSuffix, resetSuffix)

    def getValue(self):
        return self.__value

    def setValue(self, value):
        if value is None:
            value = self.DefaultValue
        self.__value = value
        self._update()

    def resetValue(self):
        self.setValue("")

    value = Qt.Property(str, getValue, setValue, resetValue)


class _CheckBox(Qt.QCheckBox, ValueMixin):

    DefaultValue = False

    valueChanged = Qt.Signal(bool)

    def __init__(self, *args, **kwargs):
        Qt.QCheckBox.__init__(self, *args, **kwargs)
        ValueMixin.__init__(self)
        self.toggled.connect(self.valueChanged)

    def _update(self):
        self.setChecked(self.getValue())
        text = "{0}{1}".format(self.prefix, self.suffix)
        self.setText(text)


class _ValueLabel(Qt.QLabel, ValueMixin):

    DefaultValue = ""

    def __init__(self, *args, **kwargs):
        Qt.QLabel.__init__(self, *args, **kwargs)
        ValueMixin.__init__(self)

    def _update(self):
        text = "{0}{1}{2}".format(self.prefix, self.value,
                                  self.suffix)
        self.setText(text)


class BaseWidgetMixin:

    Fields = {}

    DefaultLabelLocation = LabelLocation.Outside
    DefaultUnitsLocation = UnitsLocation.Outside

    def __init__(self, obj):
        self.__obj = obj
        self.__field_widgets = {}
        self.__read_only = False
        self.__label_location = self.DefaultLabelLocation
        self.__units_location = self.DefaultUnitsLocation
        self.__button_panel = Qt.QWidget()
        self.__button_panel.setVisible(False)
        layout = Qt.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(3)
        self.__rebuildUI()
        obj.changed.connect(self.__onChanged)
        obj.unitsChanged.connect(self.__onUnitsChanged)

    def __onUnitsChanged(self):
        for _, (_, _, uw) in self.__field_widgets.items():
            uw.setText(self.__obj.units)

    def __onChanged(self, o):
        obj = self.__obj
        funcs = self.Fields
        for name in self.__field_widgets:
            fget_name = funcs[name]['fget']
            value = getattr(obj, fget_name)()
            self.setFieldValue(name, value)

    def __getValueWidgetClass(self):
        if self.readOnly:
            return _ValueLabel
        if self.__obj.getDataType() == float:
            return _FSpinBox
        elif self.__obj.getDataType() == bool:
            return _CheckBox
        return _SpinBox

    def getObject(self):
        return self.__obj

    def getUnits(self):
        return self.__obj.getUnits()

    def __rebuildUI(self):
        layout = self.layout()
        while not layout.isEmpty():
            w = layout.takeAt(0).widget()
            w.setParent(None)
        for col in range(layout.columnCount()):
            layout.setColumnStretch(col, 0)
        obj = self.__obj
        field_widgets = self.__field_widgets
        field_widgets.clear()
        units = self.getUnits()
        ValueWidget = self.__getValueWidgetClass()
        for row, (field_name, field) in enumerate(self.Fields.items()):
            field_widgets[field_name] = widgets = dict()
            label = field.get('label', field_name)
            fget = getattr(obj, field['fget'])
            fset = getattr(obj, field['fset'])
            value_widget = ValueWidget()
            widgets["value"] = value_widget
            value_widget.setValue(fget())
            try:
                value_widget.valueChanged.connect(fset)
            except AttributeError:
                pass
            col = 0

            # add label
            if self.__label_location == LabelLocation.Outside:
                label_widget = _ValueLabel()
                label_widget.setSuffix(":")
                label_widget.setValue(label)
                label_widget.setAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
                widgets["label"] = label_widget
                layout.addWidget(label_widget, row, col)
                col += 1
            elif self.__label_location == LabelLocation.Inside:
                value_widget.setPrefix(label + ": ")

            # add editor
            layout.addWidget(value_widget, row, col)
            layout.setColumnStretch(col, 1)
            col += 1

            # add units
            if self.__units_location == UnitsLocation.Outside:
                units_widget = Qt.QLabel(units)
                widgets["units"] = units_widget
                layout.addWidget(units_widget, row, col)
                col += 1
            elif self.__units_location == UnitsLocation.Inside:
                value_widget.setSuffix(" " + units)
            elif self.__units_location == UnitsLocation.Label:
                label_widget = widgets.get("label")
                if label_widget is not None:
                    label_widget.setSuffix(" ({0}):".format(units))
        layout.addWidget(self.__button_panel, row, 0)

    def getFieldsWidgets(self):
        return self.__field_widgets

    def getFieldWidgets(self, field_name):
        return self.getFieldsWidgets()[field_name]

    def getFieldEditorWidget(self, field_name):
        return self.getFieldWidgets(field_name)['value']

    def getFieldValue(self, field_name):
        return self.getFieldEditorWidget(field_name).value()

    def getFieldValues(self):
        return [self.getFieldValue(field)
                for field in self.getFieldWidgets()]

    def setFieldValue(self, field_name, value):
        field_widget = self.getFieldEditorWidget(field_name)
        field_widget.setValue(value)
        bs = field_widget.blockSignals(True)
        try:
            field_widget.setValue(value)
        finally:
            field_widget.blockSignals(bs)

    # read-only

    def isReadOnly(self):
        return self.__read_only

    @Qt.Slot(bool)
    def setReadOnly(self, yesno):
        self.__read_only = yesno
        self.__rebuildUI()

    def resetReadOnly(self):
        self.setReadOnly(False)

    # label location

    def getLabelLocation(self):
        return self.__label_location

    def getLabelLocationStr(self):
        return self.__label_location.name

    def setLabelLocation(self, location):
        if not isinstance(location, LabelLocation):
            location = LabelLocation[location]
        self.__label_location = location
        self.__rebuildUI()

    def resetLabelLocation(self):
        self.setLabelLocation(self.DefaultLabelLocation)

    # unit location

    def getUnitsLocation(self):
        return self.__units_location

    def getUnitsLocationStr(self):
        return self.__units_location.name

    def setUnitsLocation(self, location):
        if not isinstance(location, UnitsLocation):
            location = UnitsLocation[location]
        self.__units_location = location
        self.__rebuildUI()

    def resetUnitsLocation(self):
        self.setUnitsLocation(self.DefaultUnitLocation)

    def getButtonPanel(self):
        return self.__button_panel

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'module'    : 'taurus.qt.qtgui.input',
            'group'     : 'Taurus Input',
            'icon'      : ':/designer/form.png',
            'container' : False }


class QBaseWidget(Qt.QWidget, BaseWidgetMixin):

    ObjClass = None

    def __init__(self, parent=None, obj=None, units=None):
        Qt.QWidget.__init__(self, parent)
        if obj is None:
            obj = self.ObjClass(parent=self, units=units)
        BaseWidgetMixin.__init__(self, obj)

    readOnly = Qt.Property(bool, BaseWidgetMixin.isReadOnly,
                           BaseWidgetMixin.setReadOnly,
                           BaseWidgetMixin.resetReadOnly)

    labelLocation = Qt.Property(str,
                                BaseWidgetMixin.getLabelLocationStr,
                                BaseWidgetMixin.setLabelLocation,
                                BaseWidgetMixin.resetLabelLocation)

    unitsLocation = Qt.Property(str,
                                BaseWidgetMixin.getUnitsLocationStr,
                                BaseWidgetMixin.setUnitsLocation,
                                BaseWidgetMixin.resetUnitsLocation)


class _QBaseRectWidget(QBaseWidget):

    ObjClass = Rectangle

    def getRectangle(self):
        return self.getObject()


class QRectXYWHWidget(_QBaseRectWidget):

    Fields = OrderedDict((
        ('x', dict(fget='left', fset="moveLeft", label='X')),
        ('y', dict(fget='top', fset="moveTop", label='Y')),
        ('w', dict(fget='width', fset="setWidth", label='Width')),
        ('h', dict(fget='height', fset="setHeight", label='Height'))))


class QRectX1Y1X2Y2Widget(_QBaseRectWidget):

    Fields = OrderedDict((
        ('x1', dict(fget='left', fset="setLeft", label='X1')),
        ('y1', dict(fget='top', fset="setTop", label='Y1')),
        ('x2', dict(fget='right', fset="setRight", label='X2')),
        ('y2', dict(fget='bottom', fset="setBottom", label='Y2'))))


class QRectWidget(Qt.QWidget):

    viewChanged = Qt.Signal(int)

    def __init__(self, parent=None, obj=None, units=None):
        Qt.QWidget.__init__(self, parent)
        if obj is None:
            obj = Rectangle(parent=self, units=units)
        layout = Qt.QStackedLayout(self)
        self.__xywh = QRectXYWHWidget(obj=obj)
        layout.addWidget(self.__xywh)
        self.__x1y1x2y2 = QRectX1Y1X2Y2Widget(obj=obj)
        layout.addWidget(self.__x1y1x2y2)

    def getView(self):
        return self.layout().currentIndex()

    @Qt.Slot(int)
    def setView(self, n):
        layout = self.layout()
        count = layout.count()
        if n >= count or n < 0:
            raise ValueError("View number out of range (0 < i < {0})".format(count))
        layout.setCurrentIndex(n)
        self.viewChanged.emit(n)

    def resetView(self):
        self.setView(0)

    view = Qt.Property(int, getView, setView, resetView)

    @Qt.Slot(bool)
    def setReadOnly(self, yesno):
        self.__xywh.setReadOnly(yesno)
        self.__x1y1x2y2.setReadOnly(yesno)

    def isReadOnly(self):
        return self.__xywh.isReadOnly()

    def resetReadOnly(self):
        self.__xywh.resetReadOnly()
        self.__x1y1x2y2.resetReadOnly()

    readOnly = Qt.Property(bool, isReadOnly, setReadOnly, resetReadOnly)

    def getObject(self):
        return self.__xywh.getObject()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'module'    : 'taurus.qt.qtgui.input',
            'group'     : 'Taurus Input',
            'icon'      : ':/designer/form.png',
            'container' : False }


class QSizeWidget(QBaseWidget):

    ObjClass = Size

    Fields = OrderedDict((
        ('w', dict(fget='width', fset="setWidth", label='W')),
        ('h', dict(fget='height', fset="setHeight", label='H'))))

    def __init__(self, parent=None, obj=None, units=None):
        QBaseWidget.__init__(self, obj=obj, units=units, parent=parent)
        #for field_widget in self.getFieldsWidgets().values():
        #    field_widget['value'].setMinimum(0)


class QPointWidget(QBaseWidget):

    ObjClass = Point

    Fields = OrderedDict((
        ('x', dict(fget='x', fset="setX", label='X')),
        ('y', dict(fget='y', fset="setY", label='Y'))))


class _QBaseVectorWidget(QBaseWidget):

    ObjClass = None

    Fields = OrderedDict((
        ('x', dict(fget='x', fset="setX", label='X')),
        ('y', dict(fget='y', fset="setY", label='Y'))))


class QVector2DWidget(_QBaseVectorWidget):

    ObjClass = Vector2D


class QVector3DWidget(_QBaseVectorWidget):

    ObjClass = Vector3D

    Fields = OrderedDict(_QBaseVectorWidget.Fields)
    Fields['z'] = dict(fget='z', fset="setZ", label='Z')


class QVector4DWidget(_QBaseVectorWidget):

    ObjClass = Vector4D

    Fields = OrderedDict(_QBaseVectorWidget.Fields)
    Fields['z'] = dict(fget='z', fset="setZ", label='Z')
    Fields['w'] = dict(fget='w', fset="setW", label='W')


class QFlipHVWidget(QBaseWidget):

    ObjClass = FlipHV

    Fields = OrderedDict((
        ('h', dict(fget='flipH', fset="setFlipH", label='Horizontal')),
        ('v', dict(fget='flipV', fset="setFlipV", label='Vertical'))))


def main():

    def __HBox(title='', childs=(), parent=None):
        box = Qt.QGroupBox(title, parent)
        layout = Qt.QHBoxLayout(box)
        layout.setMargin(3); layout.setSpacing(3)
        for child in childs:
            layout.addWidget(child)
        return box


    def __VBox(title='', childs=(), parent=None):
        box = Qt.QGroupBox(title, parent)
        layout = Qt.QVBoxLayout(box)
        layout.setMargin(3); layout.setSpacing(3)
        for child in childs:
            layout.addWidget(child)
        return box

    # model objects

    point = Point(55.4, -11.8, units="mm")
    size = Size(23, 678, units="km")
    rectangle = Rectangle(10, 20, 30, 40, units='px')
    rectangle2 = Rectangle(1.1, 2.2, 3.3, 4.4, units='eV')
    vector2 = Vector2D(187.55, 74.71)
    vector3 = Vector3D(-10, 4, 9)
    flip = FlipHV(True, False)

    app = Qt.QApplication([])
    w = Qt.QWidget()
    layout = Qt.QVBoxLayout(w)

    # Point widgets

    pw1 = QPointWidget(obj=point)
    pw2 = QPointWidget(obj=point)
    pw2.setLabelLocation(LabelLocation.Inside)
    pw2.setUnitsLocation(UnitsLocation.Inside)
    pw3 = QPointWidget(obj=point)
    pw3.setReadOnly(True)

    pb1 = __HBox("RW 1", (pw1,))
    pb2 = __HBox("RW 2", (pw2,))
    pb3 = __HBox("RO", (pw3,))

    pointBox = __HBox("Point", (pb1, pb2, pb3))
    layout.addWidget(pointBox)

    # Size

    sw1 = QSizeWidget(obj=size)
    sw2 = QSizeWidget(obj=size)
    sw2.setLabelLocation(LabelLocation.Inside)
    sw2.setUnitsLocation(UnitsLocation.Inside)
    sw3 = QSizeWidget(obj=size)
    sw3.setReadOnly(True)

    sb1 = __HBox("RW 1", (sw1,))
    sb2 = __HBox("RW 2", (sw2,))
    sb3 = __HBox("RO", (sw3,))

    sizeBox = __HBox("Size", (sb1, sb2, sb3))
    layout.addWidget(sizeBox)


    # Rect
    ## Rect XYWH

    rw1 = QRectXYWHWidget(obj=rectangle)
    rw2 = QRectXYWHWidget(obj=rectangle)
    rw2.setLabelLocation(LabelLocation.Inside)
    rw2.setUnitsLocation(UnitsLocation.Inside)
    rw3 = QRectXYWHWidget(obj=rectangle)
    rw3.setReadOnly(True)

    rb1 = __HBox("RW 1", (rw1,))
    rb2 = __HBox("RW 2", (rw2,))
    rb3 = __HBox("RO", (rw3,))

    rectXYWHBox = __HBox("Rect XYWH", (rb1, rb2, rb3))

    ## Rect X1Y1X2Y2

    rw1 = QRectX1Y1X2Y2Widget(obj=rectangle)
    rw2 = QRectX1Y1X2Y2Widget(obj=rectangle)
    rw2.setLabelLocation(LabelLocation.Inside)
    rw2.setUnitsLocation(UnitsLocation.Inside)
    rw3 = QRectX1Y1X2Y2Widget(obj=rectangle)
    rw3.setReadOnly(True)

    rb1 = __HBox("RW 1", (rw1,))
    rb2 = __HBox("RW 2", (rw2,))
    rb3 = __HBox("RO", (rw3,))

    rectX1Y1X2Y2Box = __HBox("Rect X1Y1X2Y2", (rb1, rb2, rb3))

    rectBox = __VBox("Rect", (rectXYWHBox, rectX1Y1X2Y2Box))
    layout.addWidget(rectBox)

    # Rect

    rw1 = QRectWidget(obj=rectangle2)
    rw2 = QRectWidget(obj=rectangle2)
    rw3 = QRectWidget(obj=rectangle2)
    rw3.setView(1)

    rb1 = __HBox("RW 1", (rw1,))
    rb2 = __HBox("RW 2", (rw2,))
    rb3 = __HBox("RW 3", (rw3,))

    rectBox = __HBox("Rect", (rb1, rb2, rb3))
    layout.addWidget(rectBox)

    ## Vector 2D

    v2w1 = QVector2DWidget(obj=vector2)
    v2w2 = QVector2DWidget(obj=vector2)
    v2w2.setLabelLocation(LabelLocation.Inside)
    v2w2.setUnitsLocation(UnitsLocation.Inside)
    v2w3 = QVector2DWidget(obj=vector2)
    v2w3.setReadOnly(True)

    v2b1 = __HBox("RW 1", (v2w1,))
    v2b2 = __HBox("RW 2", (v2w2,))
    v2b3 = __HBox("RO", (v2w3,))

    vector2Box = __HBox("Vector 2D", (v2b1, v2b2, v2b3))
    layout.addWidget(vector2Box)

    ## Vector 3D

    v3w1 = QVector3DWidget(obj=vector3)
    v3w2 = QVector3DWidget(obj=vector3)
    v3w2.setLabelLocation(LabelLocation.Inside)
    v3w2.setUnitsLocation(UnitsLocation.Inside)
    v3w3 = QVector3DWidget(obj=vector3)
    v3w3.setReadOnly(True)

    v3b1 = __HBox("RW 1", (v3w1,))
    v3b2 = __HBox("RW 2", (v3w2,))
    v3b3 = __HBox("RO", (v3w3,))

    vector3Box = __HBox("Vector 3D", (v3b1, v3b2, v3b3))
    layout.addWidget(vector3Box)

    ## Flip HV

    flipw1 = QFlipHVWidget(obj=flip)
    flipw2 = QFlipHVWidget(obj=flip)
    flipw2.setLabelLocation(LabelLocation.Inside)
    flipw2.setUnitsLocation(UnitsLocation.Inside)
    flipw3 = QFlipHVWidget(obj=flip)
    flipw3.setReadOnly(True)

    flipb1 = __HBox("RW 1", (flipw1,))
    flipb2 = __HBox("RW 2", (flipw2,))
    flipb3 = __HBox("RO", (flipw3,))

    flipBox = __HBox("Flip HV", (flipb1, flipb2, flipb3))
    layout.addWidget(flipBox)

    w.show()
    app.exec_()

if __name__ == "__main__":
    main()
