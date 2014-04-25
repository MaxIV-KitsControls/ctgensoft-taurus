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

"""This module contains a set of useful logging elements based on python's
:mod:`logging` system."""

__all__ = ["LogIt", "TraceIt", "DebugIt", "InfoIt", "WarnIt", "ErrorIt",
           "CriticalIt", "MemoryLogHandler", "LogExceptHook", "Logger",
           "LogFilter",
           "_log", "trace", "debug", "info", "warning", "error", "critical"]

__docformat__ = "restructuredtext"

import os
import sys
import logging.handlers
import weakref
import warnings
import traceback
import inspect
import threading

from object import Object
from wrap import wraps
from excepthook import BaseExceptHook
from taurus import tauruscustomsettings

#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
#
if hasattr(sys, 'frozen'): #support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)

# next bit filched from 1.5.2's inspect.py
def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back

if hasattr(sys, '_getframe'): currentframe = lambda: sys._getframe(3)
# done filching


class LogIt(object):
    """A function designed to be a decorator of any method of a Logger subclass.
    The idea is to log the entrance and exit of any decorated method of a Logger
    subclass.
    Example::

        from taurus.core.util.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug)
            def go(self):
                print "Hello world "

    This will generate two log messages of Debug level, one before the function
    go is called and another when go finishes. Example output::

        MainThread     DEBUG    2010-11-15 15:36:11,440 Example: -> go
        Hello world of mine
        MainThread     DEBUG    2010-11-15 15:36:11,441 Example: <- go

    This decorator can receive two optional arguments **showargs** and **showret**
    which are set to False by default. Enabling them will had verbose infomation
    about the parameters and return value. The following example::

        from taurus.core.uti.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug, showargs=True, showret=True)
            def go(self, msg):
                msg = "Hello world",msg
                print msg
                return msg

    would generate an output like::

        MainThread     DEBUG    2010-11-15 15:42:02,353 Example: -> go('of mine',)
        Hello world of mine
        MainThread     DEBUG    2010-11-15 15:42:02,353 Example: <- go = Hello world of mine

    .. note::
        it may happen that in these examples that the output of the method
        appears before or after the log messages. This is because log
        messages are, by default, written to the *stardard error* while the print
        message inside the go method outputs to the *standard ouput*. On many
        systems these two targets are not synchronized.
    """

    def __init__(self, level=logging.DEBUG, showargs=False, showret=False, col_limit=0):
        self._level = level
        self._showargs = showargs
        self._showret = showret
        self._col_limit = col_limit

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f_self = args[0]
            if f_self._logger.log_level > self._level:
                return f(*args, **kwargs)

            has_log = hasattr(f_self, "log")
            fname = f.func_name
            log_obj = f_self
            if not has_log:
                log_obj = logging.getLogger()
                try:
                    fname = "%s.%s" % (f_self.__class__.__name__, fname)
                except:
                    pass
            in_msg = "-> %s" % fname
            if self._showargs:
                if len(args) > 1: in_msg += str(args[1:])
                if len(kwargs):   in_msg += str(kwargs)
            if self._col_limit and len(in_msg) > self._col_limit: in_msg = "%s [...]" % in_msg[:self._col_limit-6]
            log_obj.log(self._level, in_msg)
            out_msg = "<-"
            try:
                ret = f(*args, **kwargs)
            except Exception, e:
                exc_info = sys.exc_info()
                out_msg += " (with %s) %s" % (e.__class__.__name__, fname)
                log_obj.log(self._level, out_msg, exc_info=exc_info)
                raise
            out_msg += " %s" % fname
            if not ret is None and self._showret:
                out_msg += " = %s" % str(ret)
            if self._col_limit and len(out_msg) > self._col_limit:
                out_msg = "%s [...]" % out_msg[:self._col_limit-6]
            log_obj.log(self._level, out_msg)
            return ret
        return wrapper


class TraceIt(LogIt):
    """Specialization of LogIt for trace level messages.
    Example::

        from taurus.core.util.log import Logger, TraceIt
        class Example(Logger):

            @TraceIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.DEBUG, showargs=showargs, showret=showret)

class DebugIt(LogIt):
    """Specialization of LogIt for debug level messages.
    Example::

        from taurus.core.util.log import Logger, DebugIt
        class Example(Logger):

            @DebugIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.DEBUG, showargs=showargs, showret=showret)


class InfoIt(LogIt):
    """Specialization of LogIt for info level messages.
    Example::

        from taurus.core.util.log import Logger, InfoIt
        class Example(Logger):

            @InfoIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.INFO, showargs=showargs, showret=showret)


class WarnIt(LogIt):
    """Specialization of LogIt for warn level messages.
    Example::

        from taurus.core.util.log import Logger, WarnIt
        class Example(Logger):

            @WarnIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.WARN, showargs=showargs, showret=showret)


class ErrorIt(LogIt):
    """Specialization of LogIt for error level messages.
    Example::

        from taurus.core.util.log import Logger, ErrorIt
        class Example(Logger):

            @ErrorIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.ERROR, showargs=showargs, showret=showret)


class CriticalIt(LogIt):
    """Specialization of LogIt for critical level messages.
    Example::

        from taurus.core.util.log import Logger, CriticalIt
        class Example(Logger):

            @CriticalIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""
    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.CRITICAL, showargs=showargs, showret=showret)


class MemoryLogHandler(list, logging.handlers.BufferingHandler):
    """An experimental log handler that stores temporary records in memory.
       When flushed it passes the records to another handler"""

    def __init__(self, capacity=1000):
        list.__init__(self)
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)
        self._handler_list_changed = False

    def shouldFlush(self, record):
        """Determines if the given record should trigger the flush

           :param record: (logging.LogRecord) a log record
           :return: (bool) wheter or not the handler should be flushed
        """
        return (len(self.buffer) >= self.capacity) or \
                (record.levelno >= Logger.getLogLevel()) or \
                self._handler_list_changed

    def flush(self):
        """Flushes this handler"""
        for record in self.buffer:
            for handler in self:
                handler.handle(record)
        self.buffer = []

    def close(self):
        """Closes this handler"""
        self.flush()
        del self[:]
        logging.handlers.BufferingHandler.close(self)


class LogExceptHook(BaseExceptHook):
    """A callable class that acts as an excepthook that logs the exception in
    the python logging system.

    :param hook_to: callable excepthook that will be called at the end of
                    this hook handling [default: None]
    :type hook_to: callable
    :param name: logger name [default: None meaning use class name]
    :type name: str
    :param level: log level [default: logging.ERROR]
    :type level: int"""

    def __init__(self, hook_to=None, name=None, level=logging.ERROR):
        BaseExceptHook.__init__(self, hook_to=hook_to)
        name = name or self.__class__.__name__
        self._level = level
        self._log = Logger(name=name)

    def report(self, *exc_info):
        text = "".join(traceback.format_exception(*exc_info))
        if text[-1] == '\n':
            text = text[:-1]
        self._log.log(self._level, "Unhandled exception:\n%s", text)


class _Logger(logging.Logger):
    
    def findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename in (_srcfile, logging._srcfile):
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


class _LoggerHelper(object):
    #: Internal usage
    root_inited    = False

    #: Internal usage
    root_init_lock = threading.Lock()

    #: Critical message level (constant)
    Critical = logging.CRITICAL

    #: Error message level (constant)
    Error    = logging.ERROR

    #: Warning message level (constant)
    Warning  = logging.WARNING

    #: Info message level (constant)
    Info     = logging.INFO

    #: Debug message level (constant)
    Debug    = logging.DEBUG

    #: Trace message level (constant)
    Trace    = logging.DEBUG

    #: Default log level (constant)
    DftLogLevel = Info

    #: Default log message format (constant)
    DftLogMessageFormat = '%(threadName)-14s %(levelname)-8s %(asctime)s %(name)s: %(message)s'

    #: Default log format (constant)
    DftLogFormat = logging.Formatter(DftLogMessageFormat)

    #: Current global log level
    log_level = DftLogLevel

    #: Default log message format
    log_format = DftLogFormat

    #: the main stream handler
    stream_handler = None

    def __init__(self):
        self.name = ''
        self.fullname = ''
        self.parent = None
        self.log_obj = None
        self.log_handlers = []
        self.log_children = {}

        init_logger = getattr(tauruscustomsettings, \
                'ENABLE_TAURUS_LOGGER', True) 
        if init_logger:
            self.initLogger()

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setFullName(self, fullname):
        self.fullname = fullname

    def getFullName(self):
        return self.fullname

    def setParent(self, parent):
        self.parent = weakref.ref(parent)

    def getParent(self):
        if self.parent is None:
            return None
        return self.parent()

    def setLogObj(self, fullname):
        self.log_obj = logging.getLogger(fullname)

    def getLogObj(self):
        return self.log_obj

    @classmethod
    def initLogger(cls):
        if not cls.root_inited:
            try:
                cls.root_init_lock.acquire()
                root_logger = logging.getLogger()
                cls.stream_handler = logging.StreamHandler(sys.__stderr__)
                cls.stream_handler.setFormatter(cls.log_format)
                root_logger.addHandler(cls.stream_handler)
                console_log_level = os.environ.get("TAURUSLOGLEVEL", None)
                if console_log_level is not None:
                    console_log_level = console_log_level.capitalize()
                    if hasattr(cls, console_log_level):
                        cls.log_level = getattr(cls, console_log_level)
                root_logger.setLevel(cls.log_level)
                _LoggerHelper.root_inited = True
            finally:
                cls.root_init_lock.release()

    @classmethod
    def addRootLogHandler(cls, h):
        """Adds a new handler to the root logger

           :param h: (logging.Handler) the new log handler
        """
        h.setFormatter(cls.getLogFormat())
        logging.getLogger().addHandler(h)


    @classmethod
    def getLogLevel(cls):
        """Retuns the current log level (the root log level)

           :return: (int) a number representing the log level
        """
        return cls.log_level

    @classmethod
    def setLogLevel(cls,level):
        """sets the new log level (the root log level)

           :param level: (int) the new log level
        """
        cls.log_level = level
        logging.getLogger().setLevel(level)

    @classmethod
    def resetLogLevel(cls):
        """Resets the log level (the root log level)"""
        cls.setLogLevel(cls.DftLogLevel)


    @classmethod
    def setLogFormat(cls,format):
        cls.log_format = logging.Formatter(format)
        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            h.setFormatter(cls.log_format)

    @classmethod
    def getLogFormat(cls):
        """Retuns the current log message format (the root log format)

           :return: (str) the log message format
        """
        return cls.log_format

    @classmethod
    def resetLogFormat(cls):
        """Resets the log message format (the root log format)"""
        cls.setLogFormat(cls.DftLogFormat)

    @classmethod
    def enableLogOutput(cls):
        """Enables the :class:`logging.StreamHandler` which dumps log records,
           by default, to the stderr.
        """
        logging.getLogger().addHandler(cls.stream_handler)

    @classmethod
    def disableLogOutput(cls):
        """Disables the :class:`logging.StreamHandler` which dumps log records,
           by default, to the stderr.
        """
        logging.getLogger().removeHandler(cls.stream_handler)

    @classmethod
    def removeRootLogHandler(cls, h):
        """Removes the given handler from the root logger

           :param h: (logging.Handler) the handler to be removed
        """
        logging.getLogger().removeHandler(h)

    def _format_trace(self):
        return self._format_stack(inspect.trace)

    def _format_stack(self, stack_func=inspect.stack):
        line_count = 3
        stack = stack_func(line_count)
        out = ''
        for frame_record in stack:
            out += '\n\t' + 60*'-'
            frame, filename, line, funcname, lines, index = frame_record
            #out += '\n\t    depth = %d' % frame[5]
            out += '\n\t filename = %s' % filename
            out += '\n\t function = %s' % funcname
            if lines is None:
                code = '<code could not be found>'
                out += '\n\t     line = [%d]: %s' % (line, code)
            else:
                lines, line_nb = [ s.strip(' \n') for s in lines ], len(lines)
                if line_nb >= 3:
                    out += '\n\t     line = [%d]: %s' % (line-1, lines[0])
                    out += '\n\t  -> line = [%d]: %s' % (line, lines[1])
                    out += '\n\t     line = [%d]: %s' % (line+1, lines[2])
                elif line_nb > 0:
                    out += '\n\t  -> line = [%d]: %s' % (line, lines[0])
            if frame:
                out += '\n\t   locals = '
                for k,v in frame.f_locals.items():
                    out += '\n\t\t%20s = ' % k
                    try:
                        cut = False
                        v = str(v)
                        i = v.find('\n')
                        if i == -1:
                            i = 80
                        else:
                            i = min(i, 80)
                            cut = True
                        if len(v) > 80: cut = True
                        out += v[:i]
                        if cut: out += '[...]'
                    except:
                        out += '<could not find suitable string representation>'
        return out

    def addLogHandler(self, handler):
        """Registers a new handler in this object's logger

           :param handler: (logging.Handler) the new handler to be added
        """
        self.getLogObj().addHandler(handler)
        self.log_handlers.append(handler)

    def copyLogHandlers(self, other):
        """Copies the log handlers of other object to this object

           :param other: (object) object which contains 'log_handlers'
        """
        for handler in other.log_handlers:
            self.addLogHandler(handler)

    def getChildren(self):
        """Returns the log children for this object

           :return: (sequence<logging.Logger) the list of log children
        """
        children = []
        for _, ref in self.log_children.iteritems():
            child = ref()
            if child is not None:
                children.append(child)
        return children

    def addChild(self, child):
        """Adds a new logging child

           :param child: (logging.Logger) the new child
        """
        if not self.log_children.get(id(child)):
            self.log_children[id(child)]=weakref.ref(child)

    def changeLogName(self,name):
        """Change the log name for this object.

           :param name: (str) the new log name
        """
        self.setName(name)
        p = self.getParent()
        if p is not None:
            log_full_name = '%s.%s' % (p._logger.getFullName(), name)
        else:
            log_full_name = name
        self.setFullName(log_full_name)
        self.setLogObj(log_full_name)
        for handler in self.log_handlers:
            self.getLogObj().addHandler(handler)
        for child in self.getChildren():
            child._logger.changeLogName(child._logger.name)

    @classmethod
    def addLevelName(cls, level_no, level_name):
        """Registers a new log level

           :param level_no: (int) the level number
           :param level_name: (str) the corresponding name
        """
        logging.addLevelName(level_no, level_name)
        level_name = level_name.capitalize()
        if not hasattr(cls, level_name):
            setattr(cls, level_name, level_no)


class Logger(Object):
    """The taurus logger class. All taurus pertinent classes should inherit
    directly or indirectly from this class if they need taurus logging
    facilities."""


    def __init__(self, name='', parent=None, format=None):
        """The Logger constructor

        :param name: (str) the logger name (default is empty string)
        :param parent: (Logger) the parent logger or None if no parent exists (default is None)
        :param format: (str) the log message format or None to use the default log format (default is None)
        """
        self.call__init__(Object)
        self._logger = _LoggerHelper()

        if format: 
            self._logger.log_format = format

        if name is None or len(name) == 0:
            name = self.__class__.__name__
        self._logger.setName(name)
        if parent is not None:
            log_full_name = '%s.%s' % (parent._logger.getFullName(), name)
            self._logger.setParent(parent)
            parent._logger.addChild(self)
        else:
            log_full_name = name

        self._logger.setFullName(log_full_name)
        self._logger.setLogObj(log_full_name)


    def trace(self, msg, *args, **kw):
        """Record a trace message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.deprecated("Trace level is marked as deprecated. Use *DEBUG* level instead of *TRACE*")
        self._logger.getLogObj().debug(msg, *args, **kw)

    def traceback(self, level=None, extended=True):
        """Log the usual traceback information, followed by a listing of all the
           local variables in each frame.

           :param level: (int) the log level assigned to the traceback record
           :param extended: (bool) if True, the log record message will have multiple lines

           :return: (str) The traceback string representation
        """
        if level is None:
            level = self._logger.Trace

        out = traceback.format_exc()
        if extended:
            out += "\n"
            out += self._logger._format_trace()

        self._logger.getLogObj().log(level, out)
        return out


    def log(self, level, msg, *args, **kw):
        """Record a log message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.

           :param level: (int) the record level
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().log(level, msg, *args, **kw)

    def debug(self, msg, *args, **kw):
        """Record a debug message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.debug`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().debug(msg, *args, **kw)

    def info(self, msg, *args, **kw):
        """Record an info message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.info`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().info(msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        """Record a warning message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.warning`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().warning(msg, *args, **kw)

    def deprecated(self, msg, *args, **kw):
        """Record a deprecated warning message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.warning`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        filename, lineno, func = self._logger.getLogObj().findCaller()
        depr_msg = warnings.formatwarning(msg, DeprecationWarning, filename, lineno)
        self._logger.getLogObj().warning(depr_msg, *args, **kw)

    def error(self, msg, *args, **kw):
        """Record an error message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.error`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().error(msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        """Record a critical message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.critical`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self._logger.getLogObj().critical(msg, *args, **kw)

    def exception(self, msg, *args):
        """Log a message with severity 'ERROR' on the root logger, with
           exception information.. Accepted *args* are the same as
           :meth:`logging.Logger.exception`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
        """
        self._logger.getLogObj().exception(msg, *args)

    def getTaurusLogger(self):
        """ Return the Taurus logger obj 
        """
        return self._logger



class LogFilter(logging.Filter):
    """Experimental log filter"""

    def __init__(self, level):
        self.filter_level = level
        logging.Filter.__init__(self)

    def filter(self, record):
        ok = (record.levelno == self.filter_level)
        return ok

def __getrootlogger():
    init_logger = getattr(tauruscustomsettings, \
            'ENABLE_TAURUS_LOGGER', True) 
    if init_logger:
        _LoggerHelper.initLogger()    
    return logging.getLogger("TaurusRootLogger")


# cannot export log because upper package taurus.core.util imports this 'log' 
# module and it would itself be overwritten by this log function
def _log(level, msg, *args, **kw):
    return __getrootlogger().log(level, msg, *args, **kw)

def trace(msg, *args, **kw):
    return _log(Logger._logger.Trace, msg, *args, **kw)

def debug(msg, *args, **kw):
    return __getrootlogger().debug(msg, *args, **kw)

def info(msg, *args, **kw):
    return __getrootlogger().info(msg, *args, **kw)

def warning(msg, *args, **kw):
    return __getrootlogger().warning(msg, *args, **kw)

def error(msg, *args, **kw):
    return __getrootlogger().error(msg, *args, **kw)

def critical(msg, *args, **kw):
    return __getrootlogger().critical(msg, *args, **kw)
