# -*- coding: utf-8 -*-
#
# This file is part of LimaGUI
#
# Copyright (c) 2014 European Synchrotron Radiation Facility, Grenoble, France
#
# Distributed under the terms of the GNU Lesser General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#

import time
import struct

import numpy

IMAGE_HEADER_FORMAT = '<IHHIIHHHHHHHHHHHHHHHHHHIII'
IMAGE_HEADER_SIZE = struct.calcsize(IMAGE_HEADER_FORMAT)
IMAGE_MAGIC = 0x44544159
IMAGE_VERSION = 1

IMAGE_2_NP = {
        0: 'uint8',
        1: 'uint16',
        2: 'uint32',
        4: 'uint64',
}

VIDEO_2_NP = {
        0: 'uint8',
        1: 'uint16',
        2: 'uint32',
        3: 'uint64',
}

NP_2_VIDEO = dict((v,k) for k, v in VIDEO_2_NP.items())

VIDEO_HEADER_FORMAT = '!IHHqiiHHHH'
VIDEO_MAGIC = 0x5644454f
VIDEO_VERSION = 1
VIDEO_FORMAT = 1
VIDEO_ENDIANNESS = ord(struct.pack('=H',1)[-1])
VIDEO_HEADER_SIZE = struct.calcsize(VIDEO_HEADER_FORMAT)
VIDEO_PAD0 = 0
VIDEO_PAD1 = 0

VIDEO_HEADER = bytearray(struct.pack(
    VIDEO_HEADER_FORMAT,
    VIDEO_MAGIC,         # Magic
    VIDEO_VERSION,       # header version
    2**16-1,             # Y16
    -1,                  # frame number
    0,                   # width
    0,                   # height
    VIDEO_ENDIANNESS,    # endianness
    VIDEO_HEADER_SIZE,   # header size
    VIDEO_PAD0, VIDEO_PAD1))

VIDEO_FORMAT_OFFSET = struct.calcsize('!IH')
FRAME_NB_OFFSET = struct.calcsize('!IHH')
WIDTH_OFFSET = struct.calcsize('!IHHq')
HEIGHT_OFFSET = struct.calcsize('!IHHqi')

_ERR_IMG_LEN = 128
_ERR_IMG_PEN = _ERR_IMG_LEN / 16
_ERR_IMG = numpy.zeros(shape=(_ERR_IMG_LEN, _ERR_IMG_LEN), dtype=numpy.uint8)
for i in range(_ERR_IMG_LEN):
    for j in range(_ERR_IMG_PEN):
        _ERR_IMG[min(i+j, _ERR_IMG_LEN-1)][i] = 255
        _ERR_IMG[max(i-j, 0)][i] = 255
        _ERR_IMG[min(_ERR_IMG_LEN-1-i+j, _ERR_IMG_LEN-1)][i] = 255
        _ERR_IMG[max(_ERR_IMG_LEN-1-i-j, 0)][i] = 255


# ------------------------------------------------------------------------------
# encode / decode
# ------------------------------------------------------------------------------

def video_raw_2_struct(frame_nb, data=None, struct_data=None, writable=False):
    if struct_data is None:
        fmt, (h, w) = NP_2_VIDEO[data.dtype.name], data.shape
        video_header = struct.pack(
            VIDEO_HEADER_FORMAT,
            VIDEO_MAGIC,         # Magic
            VIDEO_VERSION,       # header version
            fmt,                 # Y16
            frame_nb,            # frame number
            w,                   # width
            h,                   # height
            VIDEO_ENDIANNESS,    # endianness
            VIDEO_HEADER_SIZE,   # header size
            VIDEO_PAD0,
            VIDEO_PAD1)          # padding
        if writable:
            struct_data = bytearray(video_header) + data.data[:]
        else:
            struct_data = buffer(video_header) + data.data
    else:
        struct.pack_into('!q', struct_data, FRAME_NB_OFFSET, frame_nb)
    return struct_data

try:
    import Lima.Core
    from Qub.CTools.pixmaptools import LUT
    _lima_qub = True
except ImportError:
    _lima_qub = False

if _lima_qub:

    LimaVideoMode_2_QubImageType = {
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

    def video_struct_2_raw(struct_data):
        raw_data_size = len(struct_data)
        if raw_data_size < VIDEO_HEADER_SIZE:
            raise TypeError("Invalid frame")

        magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1 = \
            struct.unpack(VIDEO_HEADER_FORMAT, struct_data[:VIDEO_HEADER_SIZE])
        if magic != VIDEO_MAGIC:
            raise TypeError("Unsupported magic '%s" % magic)
        mode = LimaVideoMode_2_QubImageType.get(img_mode)
        if mode is None:
            raise TypeError("Unsupported mode %s" % img_mode)
        if raw_data_size == VIDEO_HEADER_SIZE:
            w, h = 0, 0
        if mode == LUT.Scaling.Y32:
            # At the time Qub.LUT is not implementing Y32
            frame = numpy.ndarray((h, w), dtype=numpy.uint32, buffer=struct_data[h_size:])
        else:
            frame = LUT.raw_video_2_luma(struct_data[h_size:], w, h, mode)
        return frame_nb, frame

else:
    def video_struct_2_raw(struct_data):
        raw_data_size = len(struct_data)
        if raw_data_size < VIDEO_HEADER_SIZE:
            raise TypeError("Invalid frame")

        magic, h_version, img_mode, frame_nb, w, h, endian, h_size, pad0, pad1 = \
            struct.unpack(VIDEO_HEADER_FORMAT, struct_data[:VIDEO_HEADER_SIZE])
        if magic != VIDEO_MAGIC:
            raise TypeError("Unsupported magic '%s" % magic)
        mode = VIDEO_2_NP.get(img_mode)
        if mode is None:
            raise TypeError("Unsupported mode %s" % img_mode)
        if raw_data_size == VIDEO_HEADER_SIZE:
            w, h = 0, 0
        frame = numpy.ndarray((h, w), dtype=mode, buffer=struct_data[h_size:])
        return frame_nb, frame

def image_struct_2_raw(struct_data):
    raw_data_size = len(struct_data)
    if raw_data_size < IMAGE_HEADER_SIZE:
        raise TypeError("Invalid frame")

    magic, h_version, h_size, category, dtype, endian, nb_dims, w, h = \
        struct.unpack(IMAGE_HEADER_FORMAT, struct_data[:IMAGE_HEADER_SIZE])[:9]
    if magic != IMAGE_MAGIC:
        raise TypeError("Unsupported magic '%s" % magic)
    mode = IMAGE_2_NP.get(dtype)
    if mode is None:
        raise TypeError("Unsupported data_type %s" % dtype)
    if raw_data_size == IMAGE_HEADER_SIZE:
        w, h = 0, 0
    frame = numpy.ndarray((h, w), dtype=mode, buffer=struct_data[h_size:])
    return frame


def data_2_raw(data_fmt, struct_data):
    if data_fmt == 'VIDEO_IMAGE':
        _, data = video_struct_2_raw(struct_data)
    elif data_fmt == 'DATA_ARRAY':
        data = image_struct_2_raw(struct_data)
    else:
        raise TypeError("Cannot decode format %s" % data_fmt)
    return data

