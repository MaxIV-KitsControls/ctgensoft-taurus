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

"""A rectangle as a QObject. Emits signal when rectangle geometry changes or
when rectangle units change"""

__all__ = ["Rectangle"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt


class BaseObject(Qt.QObject):

    changed = Qt.Signal(object)
    unitsChanged = Qt.Signal()

    ObjClass = None

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        units = kwargs.pop('units', None)
        Qt.QObject.__init__(self, parent)
        self.__artificial_methods = set()
        self.__obj = self.ObjClass(*args)
        self.__units = units

    def _isWriteFuncName(self, fname):
        return fname.startswith("set")

    def __getattr__(self, name):
        if not hasattr(self.__obj, name):
            raise AttributeError("class {0} has no attribute "
                                 "'{1}'".format(self.__class__.__name__, name))

        # methods which change object
        if self._isWriteFuncName(name):
            def new_f(*args, **kwargs):
                o = self.getObject()
                old = self.ObjClass(o)
                o_func = getattr(o, name)
                result = o_func(*args, **kwargs)
                if old != self.getObject():
                    self.changed.emit(self.getObject())
                return result
        else:
            def new_f(*args, **kwargs):
                o_func = getattr(self.getObject(), name)
                return o_func(*args, **kwargs)
        new_f.__name__ = name
        setattr(self, name, new_f)
        self.__artificial_methods.add(name)
        return getattr(self, name)

    def __str__(self):
        return str(self.__obj)

    def set(self, **kwargs):
        obj = self.__obj
        bs = self.blockSignals(True)
        try:
            for k, v in kwargs.items():
                getattr(obj, "set" + k.capitalize())(v)
        finally:
            self.blockSignals(bs)
        self.changed.emit(obj)

    def getUnits(self):
        if self.__units is None:
            return ""
        return self.__units

    Qt.Slot(str)
    def setUnits(self, units):
        self.__units = units

    def resetUnits(self):
        self.setUnits(None)

    units = Qt.Property(str, getUnits, setUnits, resetUnits)

    def setObject(self, obj):
        methods = self.__artificial_methods
        while methods:
            method = methods.pop()
            delattr(self, method)
        self.__obj = obj
        self.changed.emit(obj)

    def getObject(self):
        return self.__obj

    def __eq__(self, obj):
        return obj == self.__obj


class _FlipHV(object):

    def __init__(self, *args):
        largs = len(args)
        flipH, flipV = False, False
        if largs == 1: # copy constructor
            flip = args[0]
            if not isinstance(flip, _FlipHV):
                raise TypeError("Expected _FlipHV, given %s" % str(type(flip)))
            flipH = flip.flipH()
            flipV = flip.flipV()
        elif largs == 2:
            flipH, flipV = map(bool, args)
        elif largs > 2:
            raise TypeError("__init__() takes 1 or 2 arguments (%d given)" % largs)
        self.__flipH = flipH
        self.__flipV = flipV

    def setFlipHV(self, flipH=False, flipV=False):
        self.__flipH = flipH
        self.__flipV = flipV

    def setFlipH(self, flipH):
        self.__flipH = flipH

    def setFlipV(self, flipV):
        self.__flipV = flipV

    def flipH(self):
        return self.__flipH

    def flipV(self):
        return self.__flipV

    def __str__(self):
        return "{0}({1}, {2})".format(self.__class__.__name__,
                                      self.__flipH, self.__flipV)

class FlipHV(BaseObject):

    ObjClass = _FlipHV

    def getDataType(self):
        return bool


class Rectangle(BaseObject):

    ObjClass = Qt.QRect

    def __init__(self, *args, **kwargs):
        if float in map(type, args):
            self.ObjClass = Qt.QRectF
        BaseObject.__init__(self, *args, **kwargs)

    def _isWriteFuncName(self, fname):
        return fname.startswith('set') or fname.startswith("move") or \
          fname in ("adjust", "translate")

    def getRectangle(self):
        return self.getObject()

    def getDataType(self):
        return type(self.x())


class Size(BaseObject):

    ObjClass = Qt.QSize

    def __init__(self, *args, **kwargs):
        if float in map(type, args):
            self.ObjClass = Qt.QSizeF
        BaseObject.__init__(self, *args, **kwargs)

    def _isWriteFuncName(self, fname):
        return fname.startswith('set') or \
           fname in ("adjust", "transpose", "scale")

    def getSize(self):
        return self.getObject()

    def getDataType(self):
        return type(self.width())


class Point(BaseObject):

    ObjClass = Qt.QPoint

    def __init__(self, *args, **kwargs):
        if float in map(type, args):
            self.ObjClass = Qt.QPointF
        BaseObject.__init__(self, *args, **kwargs)

    def getPoint(self):
        return self.getObject()

    def getDataType(self):
        return type(self.x())


class _BaseVector(BaseObject):

    def __init__(self, *args, **kwargs):
        BaseObject.__init__(self, *args, **kwargs)

    def _isWriteFuncName(self, fname):
        return fname.startswith('set') or fname == "normalize"

    def getVector(self):
        return self.getObject()

    def getDataType(self):
        return float


class Vector2D(_BaseVector):

    ObjClass = Qt.QVector2D


class Vector3D(_BaseVector):

    ObjClass = Qt.QVector3D


class Vector4D(_BaseVector):

    ObjClass = Qt.QVector4D


def main():
    r = Rectangle(10, 10, 20, 20, units='px')
    def onRectangleChanged(qrect):
        print("Rectangle changed to: {0}!".format(qrect))
    r.changed.connect(onRectangleChanged)
    r.setBottom(100)

    s = Size(10, 20)
    def onSizeChanged(qsize):
        print("Size changed to: {0}!".format(qsize))
    s.changed.connect(onSizeChanged)
    s.setWidth(30)

    p = Point(10.6, 20, units="mm")
    def onPointChanged(qpoint):
        print("Point changed to {0}!".format(qpoint))
    p.changed.connect(onPointChanged)
    p.setX(30.6)
    p.setX(30.6)

    v2d = Vector2D(4, 8)
    def onVector2DChanged(vector2d):
        print("Vector2D changed to {0}!".format(vector2d))
    v2d.changed.connect(onVector2DChanged)
    v2d.setX(30)

    v3d = Vector3D(4, 8, 12)
    def onVector3DChanged(vector3d):
        print("Vector3D changed to {0}!".format(vector3d))
    v3d.changed.connect(onVector3DChanged)
    v3d.setZ(30)

    flip = FlipHV(True, False)
    def onFlipChanged(flip):
        print("FlipHV changed to {0}!".format(flip))
    flip.changed.connect(onFlipChanged)
    flip.setFlipX(False)
    flip.setFlipY(True)
    flip.setFlipHV(True, False)

if __name__ == "__main__":
    main()
