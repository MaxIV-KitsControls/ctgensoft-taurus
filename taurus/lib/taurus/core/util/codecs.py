#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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
"""
This module contains a list of codecs for the DEV_ENCODED attribute type.
All codecs are based on the pair *format, data*. The format is a string 
containing the codec signature and data is a sequence of bytes (string) 
containing the encoded data. 

This module contains a list of codecs capable of decoding several codings like
bz2, zip and json.

The :class:`CodecFactory` class allows you to get a codec object for a given 
format and also to register new codecs.
The :class:`CodecPipeline` is a special codec that is able to code/decode a
sequence of codecs. This way you can have codecs 'inside' codecs.

Example::

    >>> from taurus.core.util.codecs import CodecFactory
    >>> cf = CodecFactory()
    >>> json_codec = cf.getCodec('json')
    >>> bz2_json_codec = cf.getCodec('bz2_json')
    >>> data = range(100000)
    >>> f1, enc_d1 = json_codec.encode(('', data))
    >>> f2, enc_d2 = bz2_json_codec.encode(('', data))
    >>> print len(enc_d1), len(enc_d2)
    688890 123511
    >>> 
    >>> f1, dec_d1 = json_codec.decode((f1, enc_d1))
    >>> f2, dec_d2 = bz2_json_codec.decode((f2, enc_d2))

A Taurus related example::

    >>> # this example shows how to automatically get the data from a DEV_ENCODED attribute
    >>> import taurus
    >>> from taurus.core.util.codecs import CodecFactory
    >>> cf = CodecFactory()
    >>> devenc_attr = taurus.Attribute('a/b/c/devenc_attr')
    >>> v = devenc_attr.read()
    >>> codec = CodecFactory().getCodec(v.format)
    >>> f, d = codec.decode((v.format, v.value))
"""

__all__ = ["Codec", "NullCodec", "ZIPCodec", "BZ2Codec", "JSONCodec",
           "FunctionCodec", "PlotCodec", "CodecPipeline", "CodecFactory"]

__docformat__ = "restructuredtext"

import copy
import operator
import types

#need by VideoImageCodec
import struct
import numpy

from singleton import Singleton
from log import Logger, DebugIt
from containers import CaselessDict


class Codec(Logger):
    """The base class for all codecs"""
    
    def __init__(self):
        """Constructor"""
        Logger.__init__(self, self.__class__.__name__)
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data. This method is abstract an therefore must
        be implemented in the subclass.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :raises: RuntimeError"""
        raise RuntimeError("decode cannot be called on abstract Codec")
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data. This method is abstract an therefore must
        be implemented in the subclass.
        
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :raises: RuntimeError"""
        raise RuntimeError("decode cannot be called on abstract Codec")

    @classmethod
    def isEnabled(cls):
        """tell the codec factory if the class is able to function. 
        Implement in subclass if your codec is only enabled in some conditions
        (ex.: if a third party python module is present).

        Default implementation returns True."""
        return True
    
    def __str__(self):
        return '%s()' % self.__class__.__name__
    
    def __repr__(self):
        return '%s()' % self.__class__.__name__


class NullCodec(Codec):

    def encode(self, data, *args, **kwargs):
        """encodes with Null encoder. Just returns the given data

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        return data
    
    def decode(self, data, *args, **kwargs):
        """decodes with Null encoder. Just returns the given data

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        return data


class ZIPCodec(Codec):
    """A codec able to encode/decode to/from gzip format. It uses the :mod:`zlib` module
    
    Example::
    
        >>> from taurus.core.util.codecs import CodecFactory
        
        >>> # first encode something
        >>> data = 100 * "Hello world\\n"
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('zip')
        >>> format, encoded_data = codec.encode(("", data))
        >>> print len(data), len(encoded_data)
        1200, 31
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data[20]
        'Hello world\\nHello wo'"""
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a gzip string. The given data **must** be a string
        
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import zlib
        format = 'zip'
        if len(data[0]): format += '_%s' % data[0]
        return format, zlib.compress(data[1])
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a gzip string.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import zlib
        if not data[0].startswith('zip'):
            return data
        format = data[0].partition('_')[2]
        return format, zlib.decompress(data[1])


class BZ2Codec(Codec):
    """A codec able to encode/decode to/from BZ2 format. It uses the :mod:`bz2` module

    Example::
    
        >>> from taurus.core.util.codecs import CodecFactory
        
        >>> # first encode something
        >>> data = 100 * "Hello world\\n"
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('bz2')
        >>> format, encoded_data = codec.encode(("", data))
        >>> print len(data), len(encoded_data)
        1200, 68
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data[20]
        'Hello world\\nHello wo'"""
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a bz2 string. The given data **must** be a string
        
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import bz2
        format = 'bz2'
        if len(data[0]): format += '_%s' % data[0]
        return format, bz2.compress(data[1])
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a bz2 string.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import bz2
        if not data[0].startswith('bz2'):
            return data
        format = data[0].partition('_')[2]
        return format, bz2.decompress(data[1])


class PickleCodec(Codec):
    """A codec able to encode/decode to/from pickle format. It uses the
    :mod:`pickle` module.
    
    Example::
        
        >>> from taurus.core.util.codecs import CodecFactory
        
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('pickle')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>>
        >>> # now decode it
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a pickle string. The given data **must** be
        a python object that :mod:`pickle` is able to convert.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import pickle
        format = 'pickle'
        if len(data[0]): format += '_%s' % data[0]
        # make it compact by default
        kwargs['protocol'] = kwargs.get('protocol', pickle.HIGHEST_PROTOCOL)
        return format, pickle.dumps(data[1], *args, **kwargs)
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a pickle string.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import pickle
        if not data[0].startswith('pickle'):
            return data
        format = data[0].partition('_')[2]
        
        if isinstance(data[1], buffer):
            data = data[0], str(data[1])
        
        return format, pickle.loads(data[1])


class JSONCodec(Codec):
    """A codec able to encode/decode to/from json format. It uses the
    :mod:`json` module.
    
    Example::
        
        >>> from taurus.core.util.codecs import CodecFactory
        
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('json')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>> print encoded_data
        '{"hello": "world", "goodbye": 1000}'
        >>>
        >>> # now decode it
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a json string. The given data **must** be
        a python object that json is able to convert.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import json
        format = 'json'
        if len(data[0]): format += '_%s' % data[0]
        # make it compact by default
        kwargs['separators'] = kwargs.get('separators', (',',':'))
        return format, json.dumps(data[1], *args, **kwargs)
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a json string.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import json
        if not data[0].startswith('json'):
            return data
        format = data[0].partition('_')[2]
        
        ensure_ascii = kwargs.pop('ensure_ascii', False)
        
        if isinstance(data[1], buffer):
            data = data[0], str(data[1])
        
        data = json.loads(data[1])
        if ensure_ascii:
            data = self._transform_ascii(data)
        return format, data

    def _transform_ascii(self, data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, dict):
            return self._transform_dict(data)
        elif isinstance(data, list):
            return self._transform_list(data)
        elif isinstance(data, tuple):
            return tuple(self._transform_list(data))
        else:
            return data
        
    def _transform_list(self, lst):
        return [ self._transform_ascii(item) for item in lst ]

    def _transform_dict(self, dct):
        newdict = {}
        for k, v in dct.iteritems():
            newdict[self._transform_ascii(k)] = self._transform_ascii(v)
        return newdict


class BSONCodec(Codec):
    """A codec able to encode/decode to/from bson format. It uses the
    :mod:`bson` module.
    
    Example::
        
        >>> from taurus.core.util.codecs import CodecFactory
        
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('bson')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>>
        >>> # now decode it
        >>> _, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a bson string. The given data **must** be
        a python object that bson is able to convert.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import bson
        format = 'bson'
        if len(data[0]): format += '_%s' % data[0]
        return format, bson.BSON.encode(data[1], *args, **kwargs)
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a bson string.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        if not data[0].startswith('bson'):
            return data
        format = data[0].partition('_')[2]
        ensure_ascii = kwargs.pop('ensure_ascii', False)
        
        data = data[0], bson.BSON(data[1])
        
        data = decode(data[1])
        if ensure_ascii:
            data = self._transform_ascii(data)
        return format, data

    def _transform_ascii(self, data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, dict):
            return self._transform_dict(data)
        elif isinstance(data, list):
            return self._transform_list(data)
        elif isinstance(data, tuple):
            return tuple(self._transform_list(data))
        else:
            return data
        
    def _transform_list(self, lst):
        return [ self._transform_ascii(item) for item in lst ]

    def _transform_dict(self, dct):
        newdict = {}
        for k, v in dct.iteritems():
            newdict[self._transform_ascii(k)] = self._transform_ascii(v)
        return newdict


class FunctionCodec(Codec):
    """A generic function codec"""
    def __init__(self, func_name):
        Codec.__init__(self)
        self._func_name = func_name
    
    def encode(self, data, *args, **kwargs):
        format = self._func_name
        if len(data[0]): format += '_%s' % data[0]
        return format, { 'type' : self._func_name, 'data' : data[1] }
    
    def decode(self, data, *args, **kwargs):
        if not data[0].startswith(self._func_name):
            return data
        format = data[0].partition('_')[2]
        return format, data[1]


class PlotCodec(FunctionCodec):
    """A specialization of the :class:`FunctionCodec` for plot function"""    
    def __init__(self):
        FunctionCodec.__init__(self, 'plot')


class Frame(numpy.ndarray):
    def __init__(self, *args, **kwargs):
        self.meta = dict()


class VideoImageCodec(Codec):
    """A codec able to encode/decode to/from LImA video_image format.
    
    Example::
    
        >>> from taurus.core.util.codecs import CodecFactory
        >>> import PyTango
        
        >>> #first get an image from a LImA device to decode
        >>> data = PyTango.DeviceProxy(ccdName).read_attribute('video_last_image').value
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('VIDEO_IMAGE')
        >>> format,decoded_data = codec.decode(data)
        >>> # encode it again to check
        >>> format, encoded_data = codec.encode(("",decoded_data))
        >>> #compare images excluding the header:
        >>> data[1][32:] == encoded_data[32:]
        >>> #The headers can be different in the frameNumber
        >>> struct.unpack('!IHHqiiHHHH',data[1][:32])
        (1447314767, 1, 0, 6868, 1294, 964, 0, 32, 0, 0)
        >>> struct.unpack('!IHHqiiHHHH',encoded_data[:32])
        (1447314767, 1, 0, -1, 1294, 964, 0, 32, 0, 0)
    """
    
    VIDEO_HEADER_FORMAT = '!IHHqiiHHHH'
    VIDEO_HEADER_FORMAT_SIZE = struct.calcsize(VIDEO_HEADER_FORMAT)
    FMT = 'VIDEO_IMAGE'
    MAGIC = 0x5644454f
    
    VIDEO_2_NP = {
        0: 'uint8',
        1: 'uint16',
        2: 'uint32',
        3: 'uint64',
    }
    NP_2_VIDEO = dict((v,k) for k, v in VIDEO_2_NP.items())

    def __init__(self):
        Codec.__init__(self)
    
    def encode(self, data, *args, **kwargs):
        """encodes the given data to a LImA's video_image. The given data **must** be an numpy.array
        
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""

        fmt, raw_data = data
        if len(fmt):
            fmt = self.FMT + "_" + fmt
        else:
            fmt = self.FMT

        #mode depends on numpy.array dtype
        mode = self.NP_2_VIDEO[raw_data.dtype.name]
        try:
            frame_nb = raw_data.meta['frame_nb']
        except (AttributeError, KeyError):
            frame_nb = -1
        height, width = raw_data.shape
        header = self.__packHeader(mode, frame_nb, width, height)
        buff = raw_data.tostring()
        return fmt, header+buff

    @classmethod
    def getHeader(cls, raw_data):
        """Returns the header: a tuple of
        magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1

        Raises exception if header is invalid"""
        raw_data_size = len(raw_data)
        min_header_size = cls.VIDEO_HEADER_FORMAT_SIZE
        magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1 = \
            struct.unpack(cls.VIDEO_HEADER_FORMAT, raw_data[:min_header_size])
        if magic != cls.MAGIC:
            raise TypeError("Unsupported magic '%s" % magic)
        if raw_data_size == min_header_size:
            w, h = 0, 0
        return magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a LImA's video_image.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""

        fmt, raw_data = data
        if not fmt.startswith(self.FMT):
            return data
        frame = None
        raw_data_size = len(raw_data)
        min_header_size = self.VIDEO_HEADER_FORMAT_SIZE        
        if raw_data_size >= min_header_size:
            magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1 = \
              self.getHeader(raw_data)
            mode = self.VIDEO_2_NP.get(img_mode)
            if mode is None:
                raise TypeError("Unsupported mode %s" % img_mode)
            frame = Frame((h, w), dtype=mode, buffer=raw_data[h_size:])
            frame.meta['frame_nb'] = frame_nb
        return fmt[len(self.FMT)+1:], frame
    
    def __packHeader(self, imgMode, frameNumber, width, height):
        version = 1
        endian = ord(struct.pack('=H',1)[-1])
        return struct.pack(self.VIDEO_HEADER_FORMAT,
                           self.MAGIC,
                           version,
                           imgMode,
                           frameNumber,
                           width,
                           height,
                           endian,
                           self.VIDEO_HEADER_FORMAT_SIZE,
                           0,0)#padding

                           
class QVideoImageCodec(VideoImageCodec):
    """A codec able to encode/decode to/from LImA video_image format.
    
    Example::
    
        >>> from taurus.core.util.codecs import CodecFactory
        >>> import PyTango
        
        >>> #first get an image from a LImA device to decode
        >>> data = PyTango.DeviceProxy(ccdName).read_attribute('video_last_image').value
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('VIDEO_IMAGE')
        >>> format,decoded_data = codec.decode(data)
        >>> # encode it again to check
        >>> format, encoded_data = codec.encode(("",decoded_data))
        >>> #compare images excluding the header:
        >>> data[1][32:] == encoded_data[32:]
        >>> #The headers can be different in the frameNumber
        >>> struct.unpack('!IHHqiiHHHH',data[1][:32])
        (1447314767, 1, 0, 6868, 1294, 964, 0, 32, 0, 0)
        >>> struct.unpack('!IHHqiiHHHH',encoded_data[:32])
        (1447314767, 1, 0, -1, 1294, 964, 0, 32, 0, 0)
    """

    def __init__(self):
        if not self.isEnabled():
            raise RuntimeError("QVideoImageCodec cannot be initialized")
        VideoImageCodec.__init__(self)

        import Lima.Core
        from Qub.CTools.pixmaptools import LUT
        self.LUT = LUT
        self.LimaVideoMode_2_QubImageType = {
            Lima.Core.Y8: LUT.Scaling.Y8,
            Lima.Core.Y16: LUT.Scaling.Y16,
            Lima.Core.Y32: LUT.Scaling.Y32,
            Lima.Core.Y64: LUT.Scaling.Y64,
            Lima.Core.RGB555: LUT.Scaling.RGB555,
            Lima.Core.RGB565: LUT.Scaling.RGB565,
            Lima.Core.RGB24: LUT.Scaling.RGB24,
            Lima.Core.RGB32: LUT.Scaling.RGB32,
            Lima.Core.BGR24: LUT.Scaling.BGR24,
            Lima.Core.BGR32: LUT.Scaling.BGR32,
            Lima.Core.BAYER_RG8: LUT.Scaling.BAYER_RG8,
            Lima.Core.BAYER_RG16: LUT.Scaling.BAYER_RG16,
            Lima.Core.BAYER_BG8: LUT.Scaling.BAYER_BG8,
            Lima.Core.BAYER_BG16: LUT.Scaling.BAYER_BG16,
            Lima.Core.I420: LUT.Scaling.I420,
            Lima.Core.YUV411: LUT.Scaling.YUV411,
            Lima.Core.YUV422: LUT.Scaling.YUV422,
            Lima.Core.YUV444: LUT.Scaling.YUV444,
        }
        # default scaling
        self.__scaling = LUT.Scaling()

    @classmethod
    def isEnabled(cls):
        try:
            import Lima.Core
            from Qub.CTools.pixmaptools import LUT
            LUT.Scaling
            LUT.raw_video_2_image
        except:
            
            return False
        return True
                
    def decode(self, data, *args, **kwargs):
        """decodes the given data from a LImA's video_image.
            
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""

        fmt, raw_data = data
        if not fmt.startswith(self.FMT):
            return data
        frame = None
        raw_data_size = len(raw_data)
        min_header_size = self.VIDEO_HEADER_FORMAT_SIZE
        if raw_data_size >= min_header_size:
            magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1 = \
              self.getHeader(raw_data)
            qub_mode = self.LimaVideoMode_2_QubImageType.get(img_mode)            
            if qub_mode is None:
                raise TypeError("Unsupported mode %s" % img_mode)
            data = raw_data[h_size:]
            if qub_mode == self.LUT.Scaling.Y32:
                # At the time Qub.LUT is not implementing Y32
                frame = Frame((h, w), dtype=numpy.uint32, buffer=data)
                frame.meta['frame_nb'] = frame_nb
            else:
                # a QImage here
                scaling = self.LUT.Scaling()
                scaling.autoscale_plus_minus_sigma(data, w, h, qub_mode, 3)
                res, qimage = self.LUT.raw_video_2_image(raw_data[h_size:],
                                                         w, h, qub_mode, scaling)
                if not res:
                    raise ValueError("Cannot decode frame")
                frame = QVideoImageCodec.imageToArray(qimage, copy=True)
                
        return fmt[len(self.FMT)+1:], frame

    @staticmethod
    def imageToArray(qimage, copy=False, transpose=False):
        """
        Convert a QImage into numpy array. The image must have format RGB32,
        ARGB32, or ARGB32_Premultiplied. By default, the image is not copied;
        changes made to the array will appear in the QImage as well (beware: if 
        the QImage is collected before the array, there may be trouble).
        The array will have shape (width, height, (b,g,r,a)).
        """
        fmt = qimage.format()
        ptr = qimage.bits()
        if ptr is None:
            arr = numpy.ndarray((0,0), dtype=numpy.ubyte)
        else:
            ptr.setsize(qimage.byteCount())
            arr = numpy.asarray(ptr)
        if qimage.byteCount() != arr.size * arr.itemsize:
            # Required for Python 2.6, PyQt 4.10
            # If this works on all platforms, then there is no need to use np.asarray..
            arr = numpy.frombuffer(ptr, numpy.ubyte, qimage.byteCount())
    
        if fmt == qimage.Format_RGB32:
            arr = arr.reshape(qimage.height(), qimage.width(), 3)
        elif fmt == qimage.Format_ARGB32 or fmt == qimage.Format_ARGB32_Premultiplied:
            arr = arr.reshape(qimage.height(), qimage.width(), 4)
    
        if copy:
            arr = arr.copy()
        
        if transpose:
            return arr.transpose((1,0,2))
        else:
            return arr
        
        
class CodecPipeline(Codec, list):
    """The codec class used when encoding/decoding data with multiple encoders

    Example usage::
        
        >>> from taurus.core.util.codecs import CodecPipeline
        
        >>> data = range(100000)
        >>> codec = CodecPipeline('bz2_json')
        >>> format, encoded_data = codec.encode(("", data))
        
        # decode it 
        format, decoded_data = codec.decode((format, encoded_data))
        print decoded_data"""
        
    def __init__(self, format):
        """Constructor. The CodecPipeline object will be created using 
        the :class:`CodecFactory` to search for format(s) given in the format
        parameter.
        
        :param format: (str) a string representing the format."""
        
        Codec.__init__(self)
        list.__init__(self)
        
        f = CodecFactory()
        for i in format.split('_'):
            codec = f.getCodec(i)
            self.debug("Appending %s => %s" % (i,codec))
            if codec is None:
                raise TypeError('Unsupported codec %s (namely %s)' % (format, i))
            self.append(codec)
        self.debug("Done")
        
    def encode(self, data, *args, **kwargs):
        """encodes the given data.
        
        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        for codec in reversed(self):
            data = codec.encode(data, *args, **kwargs)
        return data
    
    def decode(self, data, *args, **kwargs):
        """decodes the given data.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object
        
        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        for codec in self:
            data = codec.decode(data, *args, **kwargs)
        return data


class CodecFactory(Singleton, Logger):
    """The singleton CodecFactory class.
    
    To get the singleton object do::
    
        from taurus.core.util.codecs import CodecFactory
        f = CodecFactory()
        
    The :class:`CodecFactory` class allows you to get a codec object for a given 
    format and also to register new codecs.
    The :class:`CodecPipeline` is a special codec that is able to code/decode a
    sequence of codecs. This way you can have codecs 'inside' codecs.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory
        >>> cf = CodecFactory()
        >>> json_codec = cf.getCodec('json')
        >>> bz2_json_codec = cf.getCodec('bz2_json')
        >>> data = range(100000)
        >>> f1, enc_d1 = json_codec.encode(('', data))
        >>> f2, enc_d2 = bz2_json_codec.encode(('', data))
        >>> print len(enc_d1), len(enc_d2)
        688890 123511
        >>> 
        >>> f1, dec_d1 = json_codec.decode((f1, enc_d1))
        >>> f2, dec_d2 = bz2_json_codec.decode((f2, enc_d2))

    A Taurus related example::

        >>> # this example shows how to automatically get the data from a DEV_ENCODED attribute
        >>> import taurus
        >>> from taurus.core.util.codecs import CodecFactory
        >>> cf = CodecFactory()
        >>> devenc_attr = taurus.Attribute('a/b/c/devenc_attr')
        >>> v = devenc_attr.read()
        >>> codec = CodecFactory().getCodec(v.format)
        >>> f, d = codec.decode((v.format, v.value))
    """
    
    #: Default minimum map of registered codecs
    CODEC_MAP = CaselessDict({
        'json'   : [JSONCodec,],
        'bson'   : [BSONCodec,],
        'bz2'    : [BZ2Codec,],
        'zip'    : [ZIPCodec,],
        'pickle' : [PickleCodec,],
        'plot'   : [PlotCodec,],
        'VIDEO_IMAGE' : [QVideoImageCodec, VideoImageCodec],
        'null'   : [NullCodec,],
        'none'   : [NullCodec,],
        ''       : [NullCodec], })

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        
        self._codec_klasses = copy.copy(CodecFactory.CODEC_MAP)
        
        # dict<str, Codec> 
        # where:
        #  - key is the codec format
        #  - value is the codec object that supports the format
        self._codecs = CaselessDict()

    def registerCodec(self, format, klass):
        """Registers a new codec with highest priority. If codecs already
        exist for the given format they are pushed behind in priority
        
        :param format: (str) the codec id
        :param klass: (Codec class) the class that handles the format"""
        klasses = self._codec_klasses.get(format)
        if klasses is None:
            self._codec_klasses[format] = klasses = []
        klasses.insert(0, klass)
        
        # del old codec if exists
        if self._codecs.has_key(format):
            del self._codecs[format]

    def unregisterCodec(self, format, klass=None):
        """Unregisters the given format. If the format does not exist an exception
        is thrown.
        
        :param format: (str) the codec id
        
        :raises: KeyError"""
        if format in self._codec_klasses:
            if klass is None:
                del self._codec_klasses[format]
            else:
                klasses = self._codec_klasses[format]
                klasses.remove(klass)
                if not len(klasses):
                    del self._codec_klasses[format]
                    
        if format in self._codecs:
            del self._codecs[format]

    def getCodec(self, format):
        """Returns the codec object for the given format or None if no suitable
        codec is found
        
        :param format: (str) the codec id
        
        :return: (Codec or None) the codec object for the given format"""
        codec = self._codecs.get(format)
        if codec is None:
            codec = self._getNewCodec(format)
            if not codec is None:
                self._codecs[format] = codec
        return codec
        
    def _getNewCodec(self, format):
        klasses = self._codec_klasses.get(format)
        if klasses is not None:
            for klass in klasses:
                if klass.isEnabled():
                    return klass()
        try:
            ret = CodecPipeline(format)
        except:
            ret = self._getNewCodec(None)
        return ret
    
    def decode(self, data, *args, **kwargs):
        while len(data[0]):
            data = self.getCodec(data[0]).decode(data, *args, **kwargs)
        return data[1]
        
    def encode(self, format, data, *args, **kwargs):
        return self.getCodec(format).encode(data, *args, **kwargs)
    
