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

"""This module contains all taurus tango database"""

from __future__ import with_statement

__all__ = ["TangoDevice"]

__docformat__ = "restructuredtext"

import time
import PyTango
from PyTango import CmdArgType

from taurus import Factory
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.taurusbasetypes import TaurusSWDevState, TaurusLockInfo, LockStatus

DFT_TANGO_DEVICE_DESCRIPTION = "A TANGO device"

class _TangoInfo(object):

    def __init__(self):
        self.dev_class = self.dev_type = 'TangoDevice'
        self.doc_url = 'http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/'
        self.server_host = 'Unknown'
        self.server_id = 'Unknown'
        self.server_version = 1

        
class _TimeoutContext(object):

    def __init__(self, device, timeout=None):
        self.__device = device
        self.__timeout = timeout

    def __enter__(self):
        timeout = self.__timeout
        if timeout is None:
            return
        old_timeout = self.__device.get_timeout_millis()
        timeout = int(timeout*1000)
        if old_timeout == timeout:
            self.__timeout = None
        else:
            self.__device.set_timeout_millis(timeout)
            self.__timeout = old_timeout

    def __exit__(self, etype, evalue, etraceback):
        timeout = self.__timeout
        if timeout is None:
            return
        self.__device.set_timeout_millis(timeout)


class _CallbackModelContext(object):

    def __init__(self, cb_model=None):
        self.__cb_model = cb_model

    def __enter__(self):
        cb_model = self.__cb_model
        if cb_model is None:
            return
        api_util = PyTango.ApiUtil.instance()
        old_cb_model = api_util.get_asynch_cb_sub_model()
        if old_cb_model == cb_model:
            self.__cb_model = None
        else:
            api_util.set_asynch_cb_sub_model(cb_model)
            self.__cb_model = old_cb_model

    def __exit__(self, etype, evalue, etraceback):
        cb_model = self.__cb_model
        if cb_model is None:
            return
        api_util = PyTango.ApiUtil.instance()
        api_util.set_asynch_cb_sub_model(cb_model)


class TangoDevice(TaurusDevice):

    def __init__(self, name, **kw):
        """Object initialization."""
        self.__commands_info = None
        self.call__init__(TaurusDevice, name, **kw)

    def __refreshCommandInfo(self):
        cmds_info = {}
        for cmd_info in self.command_list_query():
            cmds_info[cmd_info.cmd_name.lower()] = cmd_info
        self.__commands_info = cmds_info
        return cmds_info
    
    def __getCommandInfo(self, cmd_name):
        # so far commands are not dynamic in Tango so we can create a cache
        cmds_info = self.__commands_info
        if cmds_info is None:
            cmds_info = self.__refreshCommandInfo()
        try:
            return cmds_info[cmd_name.lower()]
        except KeyError:
            raise KeyError("Unknown command '{0}'".format(cmd_name))
        
    def __encodeCommandArguments(self, cmd_name, args, kwargs):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}        
        if len(kwargs):
            raise TypeError("Tango command doesn't support keyword arguments")
        len_args = len(args)
        if len_args > 1:
            raise TypeError("{0}() takes exactly 1 argument ({1} given)".format(cmd_name, len_args))

        cmd_info = self.__getCommandInfo(cmd_name)
        param_type = cmd_info.in_type
        if len_args == 0:
            if param_type != CmdArgType.DevVoid:
                raise TypeError("{0} takes exactly 1 argument (0 given)".format(cmd_name))
            return args, kwargs

        if param_type == CmdArgType.DevVoid:
            raise TypeError("{0} takes no arguments (1 given)".format(cmd_name))
        return args, kwargs
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='tango')
        return cls._factory

    # command API

    def command(self, cmd_name, args=None, kwargs=None, asynch=False,
                callback=None, timeout=None):
        try:
            return self.__command(cmd_name, args=args, kwargs=kwargs,
                                  asynch=asynch, callback=callback,
                                  timeout=timeout)
        except Exception as e:
            self.error("Error executing command '%s' on %s: %s", cmd_name,
                       self.getNormalName(), str(e))
            self.debug("Details:", exc_info=1)
            raise
                       
    def __command(self, cmd_name, args=None, kwargs=None, asynch=False,
                  callback=None, timeout=None):
        args, kwargs = self.__encodeCommandArguments(cmd_name, args, kwargs)
        cmd_args = [cmd_name] 
        cmd_args.extend(args)
        device = self.getHWObj()
        cmd_info = self.__getCommandInfo(cmd_name)
        def __cb(e):
            error = False
            if e.err:
                error = True
                cmd_result = PyTango.DevFailed(*e.errors)
            else:
                if cmd_info.out_type == CmdArgType.DevVoid:
                    cmd_result = None
                else:
                    cmd_result = e.argout_raw.extract()
            try:
                callback(cmd_result, error)
            except:
                self.error("Unhandled exception running '{0}' "
                           "callback".format(cmd_name))
                self.debug("Details:", exc_info=1)

        if asynch:
            if callback is None:
                # forget = True
                cmd_args.append(True)
            else:
                cmd_args.append(__cb)
            with _TimeoutContext(device, timeout):
                with _CallbackModelContext(PyTango.cb_sub_model.PUSH_CALLBACK):
                    return device.command_inout_asynch(*cmd_args)
        else:
            if callback:
                error = False
                try:
                    with _TimeoutContext(device, timeout):
                        result = device.command_inout(*cmd_args)
                except Exception as exc:
                    error = True
                    result = exc
                    raise
                finally:
                    try:
                        callback(result, error)
                    except:
                        self.error("Unhandled exception running '{0}' "
                                   "callback".format(cmd_name))
                return result
            else:  
                with _TimeoutContext(device, timeout):
                    return device.command_inout(*cmd_args)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusDevice necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def _createHWObject(self):
        try:
            return PyTango.DeviceProxy(self.getFullName())
        except PyTango.DevFailed, e:
            self.warning('Could not create HW object: %s' % (e[0].desc))
            self.traceback()
            
    def isValidDev(self):
        '''see: :meth:`TaurusDevice.isValid`'''
        return self._deviceObj is not None

    def lock(self, force=False):
        li = self.getLockInfo()
        if force:
            if self.getLockInfo().status == TaurusLockInfo.Locked:
                self.unlock(force=True)
        return self.getHWObj().lock()

    def unlock(self, force=False):
        return self.getHWObj().unlock(force)
    
    def getLockInfo(self, cache=False):
        lock_info = self._lock_info
        if cache and lock_info.status != LockStatus.Unknown:
            return lock_info
        try:
            dev = self.getHWObj()
            li = PyTango.LockerInfo()
            locked = dev.get_locker(li)
            msg = "%s " % self.getSimpleName()
            if locked:
                lock_info.id = pid = li.li
                lock_info.language = li.ll
                lock_info.host = host = li.locker_host
                lock_info.klass = li.locker_class
                if dev.is_locked_by_me():
                    status = LockStatus.LockedMaster
                    msg += "is locked by you!"
                else:
                    status = LockStatus.Locked
                    msg += "is locked by PID %s on %s" % (pid, host)
            else:
                lock_info.id = None
                lock_info.language = None
                lock_info.host = host = None
                lock_info.klass = None
                status = LockStatus.Unlocked
                msg += "is not locked"
            lock_info.status = status
            lock_info.status_msg = msg
        except:
            self._lock_info = lock_info = TaurusLockInfo()
        return lock_info
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Protected implementation
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def _server_state(self):
        state = None
        try:
            self.dev.ping()
            state = TaurusSWDevState.Running
        except:
            try:
                if self.dev.import_info().exported:
                    state = TaurusSWDevState.Crash
                else:
                    state = TaurusSWDevState.Shutdown
            except:
                state = TaurusSWDevState.Shutdown
        return state
        
    def decode(self, event_value):
        if isinstance(event_value, PyTango.DeviceAttribute):
            new_sw_state = TaurusSWDevState.Running
        elif isinstance(event_value, PyTango.DevFailed):
            new_sw_state = self._handleExceptionEvent(event_value)
        elif isinstance(event_value, int): # TaurusSWDevState
            new_sw_state = event_value
        else:
            self.info("Unexpected value to decode: %s" % str(event_value))
            new_sw_state = TaurusSWDevState.Crash
            
        value = PyTango.DeviceAttribute()
        value.value = new_sw_state
        
        return value
        
    def _handleExceptionEvent(self, event_value):
        """Handles the tango error event and returns the proper SW state."""
        
        new_sw_state = TaurusSWDevState.Uninitialized
        reason = event_value[0].reason
        # API_EventTimeout happens when: 
        # 1 - the server where the device is running shuts down/crashes
        # 2 - the notifd shuts down/crashes
        if reason == 'API_EventTimeout':
            if not self._deviceSwState in self.SHUTDOWNS:
                serv_state = self._server_state()
                # if the device is running it means that it must have been 
                # the event system that failed
                if serv_state == TaurusSWDevState.Running:
                    new_sw_state = TaurusSWDevState.EventSystemShutdown
                else:
                    new_sw_state = serv_state
            else:
                # Keep the old state
                new_sw_state = self._deviceSwState
                
        # API_BadConfigurationProperty happens when: 
        # 1 - at client startup the server where the device is is not 
        #     running.
        elif reason == 'API_BadConfigurationProperty':
            assert(self._deviceSwState != TaurusSWDevState.Running)
            new_sw_state = TaurusSWDevState.Shutdown
        
        # API_EventChannelNotExported happens when:
        # 1 - at client startup the server is running but the notifd
        #     is not
        elif reason == 'API_EventChannelNotExported':
            new_sw_state = TaurusSWDevState.EventSystemShutdown
        return new_sw_state
    
    def _getDefaultDescription(self):
        return DFT_TANGO_DEVICE_DESCRIPTION

    def __pollResult(self, attrs, ts, result, error=False):
        if error:
            for attr in attrs.values():
                attr.poll(single=False, value=None, error=result, time=ts)
            return

        for da in result:
            if da.has_failed:
                v, err = None, PyTango.DevFailed(*da.get_err_stack())
            else:
                v, err = da, None
            attr = attrs[da.name]
            attr.poll(single=False, value=v, error=err, time=ts)

    def __pollAsynch(self, attrs):
        ts = time.time()
        try:
            req_id = self.read_attributes_asynch(attrs.keys())
        except PyTango.DevFailed as e:
            return False, e, ts
        return True, req_id, ts

    def __pollReply(self, attrs, req_id, timeout=None):
        ok, req_id, ts = req_id
        if not ok:
            self.__pollResult(attrs, ts, req_id, error=True)
            return

        if timeout is None:
            timeout = 0
        timeout = int(timeout*1000)
        result = self.read_attributes_reply(req_id, timeout)
        self.__pollResult(attrs, ts, result)

    def poll(self, attrs, asynch=False, req_id=None):
        '''optimized by reading of multiple attributes in one go'''
        if req_id is not None:
            return self.__pollReply(attrs, req_id)

        if asynch:
            return self.__pollAsynch(attrs)

        error = False
        ts = time.time()
        try:
            result = self.read_attributes(attrs.keys())
        except PyTango.DevFailed as e:
            error = True
            result = e
        self.__pollResult(attrs, ts, result, error=error)
    
    def _repr_html_(self):
        try:
            info = self.getHWObj().info()
        except:
            info = _TangoInfo()
        txt = """\
<table>
    <tr><td>Short name</td><td>{simple_name}</td></tr>
    <tr><td>Standard name</td><td>{normal_name}</td></tr>
    <tr><td>Full name</td><td>{full_name}</td></tr>
    <tr><td>Device class</td><td>{dev_class}</td></tr>
    <tr><td>Server</td><td>{server_id}</td></tr>
    <tr><td>Documentation</td><td><a target="_blank" href="{doc_url}">{doc_url}</a></td></tr>
</table>
""".format(simple_name=self.getSimpleName(), normal_name=self.getNormalName(),
           full_name=self.getFullName(), dev_class=info.dev_class,
           server_id=info.server_id, doc_url=info.doc_url)
        return txt
