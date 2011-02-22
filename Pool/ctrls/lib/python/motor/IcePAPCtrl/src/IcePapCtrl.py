import PyTango
import socket
import errno
from pool import MotorController
from pyIcePAP import *
import time

class IcepapController(MotorController):
    "This class is the Tango Sardana motor controller for the ICEPAP with properties"

    #ctrl_features = ['Encoder','Home_speed','Home_acceleration']

    class_prop = {'Host':{'Type':'PyTango.DevString','Description':'The host name'},
                 'Port':{'Type':'PyTango.DevLong','Description':'The port number','DefaultValue':5000},
		          'Timeout':{'Type':'PyTango.DevLong','Description':'Connection timeout','DefaultValue':3}}

    ctrl_extra_attributes = {'Indexer':{'Type':'PyTango.DevString','R/W Type':'PyTango.READ_WRITE'},
                             'Position_Register':{'Type':'PyTango.DevString','R/W Type':'PyTango.READ_WRITE'},
                             'PowerOn':{'Type':'PyTango.DevBoolean','R/W Type':'PyTango.READ_WRITE'},
                             'InfoA':{'Type':'PyTango.DevString','R/W Type':'PyTango.READ_WRITE'},
                             'InfoB':{'Type':'PyTango.DevString','R/W Type':'PyTango.READ_WRITE'},
                             'InfoC':{'Type':'PyTango.DevString','R/W Type':'PyTango.READ_WRITE'},
                             'EnableEncoder_5V':{'Type':'PyTango.DevBoolean','R/W Type':'PyTango.READ_WRITE'},
                             ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                             'Pulses_per_unit':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'}
                             }

    
    gender = "Motor"
    model = "Icepap"
    organization = "Esrf Alba"
    image = "icepaphw.png"
    logo = "icepap.png"
    icon = "icepapicon.png"
    state = ""
    status = ""
    
    MaxDevice = 128
    
    def __init__(self,inst,props):
        
        MotorController.__init__(self,inst,props)
        
        #
        # Connect to the icepap
        #
        
        #print "IcePap on",self.Host," and port",self.Port," with timeout = ",self.Timeout
        #try:
        self.iPAP = EthIcePAP(self.Host, self.Port, self.Timeout)
            
        if self.iPAP.connect() == 0:
            #print "IcePAP -> Connected to", self.Host, " on port", self.Port
            self.state=PyTango.DevState.ON
            self.status="Device is ON"

        else:
            #print "IcePAP -> Error Connecting to IcePAP host", self.Host
            self.state=PyTango.DevState.FAULT
            self.status="Ethernet connection to the IcePAP failed"
        #except:
                #print "IcePAP -> Error Initializing the IcePAP, try block failed"        
                #self.state=PyTango.DevState.FAULT
                #self.status="IcePAP object could not be initialized"
	self.attributes = {}

    def AddDevice(self,axis):
        #Check Axis

        #print "IcePAP -> IcePapController/",self.inst_name,": In AddDevice method for axis",axis

        if self.iPAP.connected==0:
            if self.iPAP.connect()==0:
                #print "New connection to IcePap ", self.Host, " on port ", self.Port, "\n"
                self.state=PyTango.DevState.ON
                self.status="Device is ON"
            else:
                #print "Could not connect to IcePap ", self.Host, "\n"
                PyTango.Except.throw_exception("IcepapController_AddDevice", "Error adding axis, axis not available", "AddDevice()")
            addr = axis % 10
            cratenr = axis / 10
            cratespresent = self.iPAP.getSysStatus()
            cratespresent = int(cratespresent, 16)
            if ((cratespresent >> cratenr) & 1) == 1:
                driversalive =  self.iPAP.getRackStatus(cratenr)[1]
                driversalive = int(driversalive, 16)
                if ((driversalive >> (addr-1)) & 1) == 1:
                    #print "IcePAP -> IcePapController/",self.inst_name,": Axis added"
                    self.attributes[axis] = {}
                    self.attributes[axis]["pos_sel"] = ""
                    self.attributes[axis]["step_per_unit"] = 1  
                    ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                    self.attributes[axis]["pulses_per_unit"] = 1
                else:
                    PyTango.Except.throw_exception("IcepapController_AddDevice", "Error adding axis, axis not available", "AddDevice()")
        else:
            addr = axis % 10
            cratenr = axis / 10
            cratespresent = self.iPAP.getSysStatus()
            cratespresent = int(cratespresent, 16)
            if ((cratespresent >> cratenr) & 1) == 1:
                driversalive =  self.iPAP.getRackStatus(cratenr)[1]
                driversalive = int(driversalive, 16)
                if ((driversalive >> (addr-1)) & 1) == 1:
                    #print "IcePAP -> IcePapController/",self.inst_name,": Axis added"
                    self.attributes[axis] = {}
                    self.attributes[axis]["pos_sel"] = ""
                    self.attributes[axis]["step_per_unit"] = 1  
                    ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                    self.attributes[axis]["pulses_per_unit"] = 1
                else:
                    PyTango.Except.throw_exception("IcepapController_AddDevice", "Error adding axis, axis not available", "AddDevice()")

        
    def DeleteDevice(self,axis):
        pass
        #print "IcePAP -> IcePapController/",self.inst_name,": In DeleteDevice method for axis",axis
    
    
    def StateOne(self,axis):
        #print "PYTHON -> IcePapController/",self.inst_name,": In StateOne method for axis",axis
        if self.iPAP.connected:
            try:
                register = self.iPAP.getStatus(axis)
                if "x" in register:
                    register = int(register,16)
                else:
                    register = int(register)
                stat = IcepapStatus.isDisabled(register)
                if int(stat) == 1:
                    stat = PyTango.DevState.OFF
                else:
                    power = self.iPAP.getPower(axis)
                    power = (power == IcepapAnswers.ON)
                    if power:
                        stat = PyTango.DevState.ON
                    else:
                        stat = PyTango.DevState.OFF
                    mov = IcepapStatus.isMoving(register)
                    if int(mov) == 1:
                        stat = PyTango.DevState.MOVING
                if self.iPAP.getMode(axis) == IcepapMode.CONFIG:
                    stat = PyTango.DevState.OFF
                lower = IcepapStatus.getLimitNegative(register) 
                upper = IcepapStatus.getLimitPositive(register) 
                switchstate = 0
                if int(lower) == 1 and int(upper) == 1:
                    switchstate = 6
                elif int(lower) == 1:
                    switchstate = 4
                elif int(upper) == 1:
                    switchstate = 2
                self.state = (int(stat), switchstate)
                return self.state
            except e:
                #print "StateOne Exception",e,"\t",type(e),"\n"
                PyTango.Except.throw_exception("IcepapController_StateOne", "Error trying to get IcePap status", "StateOne()")
        else:
            self.state=(int(PyTango.DevState.FAULT),0)
            self.status="Ethernet connection to the IcePAP is dead"
            return self.state

    def PreReadAll(self):
        #print "PYTHON -> IcePapController/",self.inst_name,": In PreReadAll method"
        pass

    def PreReadOne(self,axis):
        #print "PYTHON -> IcePapController/",self.inst_name,": In PreReadOne method for axis",axis
        pass

    def ReadAll(self):
        #print "PYTHON -> IcePapController/",self.inst_name,": In ReadAll method"
        pass

    def ReadOne(self,axis):
        #print "PYTHON -> IcePapController/",self.inst_name,": In ReadOne method for axis",axis
        if self.iPAP.connected:
            try:
                pos_sel = self.attributes[axis]["pos_sel"]
                pos = float(self.iPAP.getPosition(axis, pos_sel))
                if pos_sel == "" or pos_sel == "AXIS":
                    return pos / self.attributes[axis]["step_per_unit"]
                else:
                    ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                    return  pos / self.attributes[axis]["pulses_per_unit"]
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")
            except Exception,e:
                PyTango.Except.throw_exception("IcepapController_ReadOne", "Error reading position, axis not available", "ReadOne()")

    def PreStartAll(self):
        #print "PYTHON -> IcePapController/",self.inst_name,": In PreStartAll method"
        pass

    def PreStartOne(self,axis,pos):
        #print "PYTHON -> IcePapController/",self.inst_name,": In PreStartOne method for axis",axis," with pos",pos
        if self.iPAP.connected:
            return True
        else:
            return -1

    def StartOne(self,axis,pos):
        #print "PYTHON -> IcePapController/",self.inst_name,": In StartOne method for axis",axis," with pos",pos
        if self.iPAP.connected:
            try:
                pos = int(pos * self.attributes[axis]["step_per_unit"])
                self.GOAbsolute(axis, pos)
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")            
            except:
                #print "IcePAP -> IcePapController Error StartOne"
                PyTango.Except.throw_exception("IcepapController_StartOne", "Error setting position, axis not available", "StartOne()")
            
    def StartAll(self):
        #print "PYTHON -> IcePapController/",self.inst_name,": In StartAll method"
        pass

    def SetPar(self,axis,name,value):
        #print "IcePAP -> IcePapController/",self.inst_name,": In SetPar method for axis",axis," name=",name," value=",value
        if self.iPAP.connected:
            try:
                if name.lower() == "velocity":
                    self.iPAP.setSpeed(axis, value)
                elif name.lower() == "base_rate":
                    pass
                elif name.lower() == "acceleration" or name == "deceleration":
                    self.iPAP.setAcceleration(axis, value)        
                elif name.lower() == "backlash":
                    PyTango.Except.throw_exception("IcepapController_SetPar", "Error setting backlash, not implemented", "SetPar()")
                elif name.lower() == "step_per_unit":
                    self.attributes[axis]["step_per_unit"] = float(value)
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")
            except:
                PyTango.Except.throw_exception("IcepapController_SetPar", "Error setting " + name , "SetPar()")
        

    def GetPar(self,axis,name):
        #print "IcePAP -> IcePapController/",self.inst_name,": In GetPar method for axis",axis," name=",name
        if self.iPAP.connected:
            try:
                if name.lower() == "velocity":
                    return float(self.iPAP.getSpeed(axis))
                elif name.lower() == "base_rate":
                    return float(self.iPAP.getCfgParameter(axis, "DEFIVEL"))
                elif name.lower() == "acceleration" or name.lower() == "deceleration":
                    return float(self.iPAP.getAcceleration(axis))
                elif name.lower() == "backlash":
                    PyTango.Except.throw_exception("IcepapController_GetPar", "Error getting backlash, not implemented", "GetPar()")
                elif name.lower() == "step_per_unit":
                    return float(self.attributes[axis]["step_per_unit"]) 
                return 0
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")
            except:
                PyTango.Except.throw_exception("IcepapController_GetPar", "Error getting " + name , "GetPar()")
        else:
            return -1

    def GetExtraAttributePar(self,axis,name):
        if self.iPAP.connected:
            name = name.lower()
            try:
                if name == "indexer":
                    return self.iPAP.getIndexerSource(axis)
                elif name == "position_register":
                    return self.attributes[axis]["pos_sel"]
                elif name == "enableencoder_5v":
                    ans = self.iPAP.getAuxPS(axis)
                    return ans == IcepapAnswers.ON
                elif name.startswith("info"):
                    name = name.upper()
                    result = self.iPAP.getInfoSource(axis, name)
                    return result
                elif name == "poweron":
                    ans = self.iPAP.getPower(axis)
                    return ans == IcepapAnswers.ON
                ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                elif name == "pulses_per_unit":
                    return float(self.attributes[axis]["pulses_per_unit"])
                else:
                    PyTango.Except.throw_exception("IcepapController_GetExtraAttributePar()r", "Error getting " + name + ", not implemented", "GetExtraAttributePar()")
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")
            except:
                #print sys.exc_info()
                PyTango.Except.throw_exception("IcepapController_GetExtraAttributePar", "Error getting " + name , "GetExtraAttributePar()")

    def SetExtraAttributePar(self,axis,name,value):
        #print "PYTHON -> IcePapController/",self.inst_name,": In SetExtraAttributePar method for axis",axis," name=",name," value=",value
        if self.iPAP.connected:
            name = name.lower()
            try:
                if name == "indexer":
                    if value in IcepapRegisters.IndexerRegisters:
                        self.iPAP.setIndexerSource(axis, value)
                    else:
                        PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar()", "Error setting " + name + ", wrong value", "SetExtraAttributePar()")
                elif name == "position_register":
                    if value in IcepapRegisters.PositionRegisters:
                        self.attributes[axis]["pos_sel"] = value
                    else:
                        PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar()", "Error setting " + name + ", wrong value", "SetExtraAttributePar()")                
                elif name == "enableencoder_5v":
                    if value:
                        self.iPAP.setAuxPS(axis, IcepapAnswers.ON)
                    else:
                        self.iPAP.setAuxPS(axis, IcepapAnswers.OFF)
                elif name == "poweron":
                    if value:
                        self.iPAP.setPower(axis, IcepapAnswers.ON)
                    else:
                        self.iPAP.setPower(axis, IcepapAnswers.OFF)
                ## THIS IS A TEMPORARY TRICK UNTIL THE ICEPAP MANAGES ENCODER PULSES INPUT
                elif name == "pulses_per_unit":
                    self.attributes[axis]["pulses_per_unit"] = float(value)
                    
                elif name.startswith("info"):
                    name = name.upper()
                    value = value.split()
                    src = value[0].upper()
                    if not src in IcepapInfo.Sources:
                        PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar(r", "Error setting " + name + ", [Source = ("+str(IcepapInfo.Sources) + "), Polarity= ("+str(IcepapInfo.Polarity)+")]", "SetExtraAttributePar()")
                    polarity = "NORMAL"
                    if len(value) > 1:
                        polarity = value[1].upper()
                        if not polarity in IcepapInfo.Polarity:
                            PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar(r", "Error setting " + name + ", [Source = ("+str(IcepapInfo.Sources) + "), Polarity= ("+str(IcepapInfo.Polarity)+")]", "SetExtraAttributePar()")
                    
                    
                    self.iPAP.setInfoSource(axis, name, src, polarity)                            
                else:
                    PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar()r", "Error setting " + name + ", not implemented", "SetExtraAttributePar()")
            except IcePAPException, e:
                PyTango.Except.throw_exception("IcepapController_StateOne", e.name, "StateOne()")
            except PyTango.DevFailed, e:
                raise e
            except:
                #print sys.exc_info()
                PyTango.Except.throw_exception("IcepapController_SetExtraAttributePar", "Error setting " + name , "SetExtraAttributePar()")


    def AbortOne(self,axis):
        #print "IcePAP-->before abortone"
        if self.iPAP.connected:
            self.iPAP.abortMotor(axis)
            time.sleep(0.050)
            #print "IcePAP-->Abort"

    def StopOne(self,axis):
        if self.iPAP.connected:
            self.iPAP.stopMotor(axis)
            #print "IcePAP-->Stop"


    def DefinePosition(self, axis, position):
        #print "IcePAP-->Set Position %d in axis %d" % (axis, position)
        if self.iPAP.connected:
            position = int(position * self.attributes[axis]["step_per_unit"])
            self.iPAP.setPosition(axis, position, self.attributes[axis]["pos_sel"])

    def GOAbsolute(self, axis, finalpos):
        if self.iPAP.connected:
            ret = self.iPAP.move(axis, finalpos)

    def SendToCtrl(self,cmd):
        #print "IcePAP-->SendToCtrl with data '%s'" % cmd
        # determine if the command has an answer
        if self.iPAP.connected:
            cmd = cmd.upper()
            if cmd.find("?") >= 0 or cmd.find("#")>= 0:
                res = self.iPAP.sendWriteReadCommand(cmd)
            elif cmd.find("HELP")>=0:
                res = self.iPAP.sendWriteReadCommand(cmd)
            else:
                res = self.iPAP.sendWriteCommand(cmd)
            return res 

    def __del__(self):
        #print "IcePAP -> IcePapController/",self.inst_name,": Exiting"
        if self.iPAP.connected:
            self.iPAP.disconnect()
            self.iPAP.connected=0
        
        
if __name__ == "__main__":
    obj = IcepapController('test')
#    obj.AddDevice(2)
#    obj.DeleteDevice(2)

