static const char *RcsId = "$Header$";
//+=============================================================================
//
// file :         Motor.cpp
//
// description :  C++ source for the Motor and its commands. 
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                Motor are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.56  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.55  2007/08/17 13:07:29  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.54  2007/08/07 09:51:06  tcoutinho
// Fix bug 24: Motor.state() and ghostGroup.state() return different states
//
// Revision 1.53  2007/05/30 14:54:28  etaurel
// - Forget exception thrown by  the inform_ghost() method during DS startup
// sequence
// - Change the inform_ghost() method to propagate event only if the old
// state value is not MOVING
//
// Revision 1.52  2007/05/25 12:48:10  tcoutinho
// fix the same dead locks found on motor system to the acquisition system since release labeled for Josep Ribas
//
// Revision 1.51  2007/05/25 07:50:01  tcoutinho
// - fix internal event propagation to ghost motor group when client asks for state and the new calculated state is different from the one previously stored
// - added position events on DefinePosition commnad
//
// Revision 1.50  2007/05/22 13:43:09  tcoutinho
// - added new method
//
// Revision 1.49  2007/05/17 09:29:21  tcoutinho
// - fix bug when abort is called notify listeners
//
// Revision 1.48  2007/05/15 07:20:09  etaurel
// - Fix a case-sesitivity problem
//
// Revision 1.47  2007/05/10 09:35:25  etaurel
// - All attributes name are now case sensitive
//
// Revision 1.46  2007/05/07 09:42:27  etaurel
// - Small changes for better 64 bits portability
//
// Revision 1.45  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.44  2007/02/08 07:57:47  etaurel
// - Changes after compilation -Wall. Small small changes
//
// Revision 1.43  2007/01/30 16:42:41  etaurel
// - Fix bug in PoolBaseDev data member initialization
//
// Revision 1.42  2007/01/30 15:58:32  etaurel
// - Fix a memory leak
//
// Revision 1.41  2007/01/16 14:26:02  etaurel
// - First release with the PoolBaseDev base class
//
// Revision 1.40  2007/01/05 14:55:47  etaurel
// - Replace nb_motor with nb_dev
//
// Revision 1.39  2007/01/05 13:04:40  tcoutinho
// - added pseudo motor limit check for motors used by pseudo motors
//
// Revision 1.38  2007/01/04 11:54:13  etaurel
// - Added the CounterTimer controller
//
// Revision 1.37  2006/12/28 15:34:13  etaurel
// - Fire change event on limit_switches attributes
// - Manage position limit on dial position
// - Throw events even in Simulation mode
//
// Revision 1.36  2006/12/20 10:26:17  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.35  2006/12/18 11:35:29  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.34  2006/12/05 10:12:37  etaurel
// - Remove a log message
//
// Revision 1.33  2006/11/29 08:01:54  etaurel
// - Add a new test in the write_Position method() in order to check several
// times the same thing
//
// Revision 1.32  2006/11/23 10:48:11  etaurel
// - Change in write_position to check psm (in case of)
//
// Revision 1.31  2006/11/20 14:35:00  etaurel
// - Add ghost group and event on group position
//
// Revision 1.30  2006/11/07 15:07:37  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.29  2006/11/03 15:48:14  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.28  2006/10/30 11:36:55  etaurel
// - Some changes in the motor init sequence
//
// Revision 1.27  2006/10/25 10:05:02  etaurel
// - Complete implementation of the ReloadControllerCode command
// - Handle end of movment when reading position in polling mode
//
// Revision 1.26  2006/10/20 15:42:09  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.25  2006/10/06 10:43:19  etaurel
// - Rounding motor feature is now supported
//
// Revision 1.24  2006/10/05 14:54:09  etaurel
// - Test suite of motor controller features is now working
//
// Revision 1.23  2006/10/05 08:00:16  etaurel
// - Controller now supports dynamic features
//
// Revision 1.22  2006/10/02 09:19:46  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.21  2006/09/21 08:01:55  etaurel
// - Now all test suite is OK withou ID on motor interface
//
// Revision 1.20  2006/09/21 07:26:17  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.19  2006/09/20 13:11:33  etaurel
// - For the user point of view, the controller does not have ID any more.
// We are now using the controller instance name (uniq) to give them a name
//
// Revision 1.18  2006/09/15 07:50:53  etaurel
// - Abort command always possible
// - Remove the Reset command
//
// Revision 1.17  2006/08/17 09:56:12  etaurel
// - Add limit_switches attributes
//
// Revision 1.16  2006/07/07 12:39:54  etaurel
// - Commit after implementing the group multi motor read
//
// Revision 1.15  2006/07/03 08:40:21  etaurel
// - Add DialPosition and Offset attributes
//
// Revision 1.14  2006/06/28 15:56:10  etaurel
// - Commit after first series of tests
//
// Revision #define		MAX_EXTRA_ATTRIBUTES		1281.13  2006/06/23 10:02:18  etaurel
// - Add some protection against multi-threaded access
//
// Revision 1.12  2006/06/21 14:48:34  etaurel
// - Don't remember the changes I did..
//
// Revision 1.11  2006/06/19 15:25:27  etaurel
// - before adding a new UNKNOWN state
//
// Revision 1.10  2006/06/19 12:34:36  etaurel
// - Changes in the Motr state machine and in the delete_device() method for a better pool shut down
//
// Revision 1.9  2006/06/12 10:28:26  etaurel
// - Many changes dur to bug fixes found when writing test units...
//
// Revision 1.8  2006/05/26 09:12:24  etaurel
// - Add some exception checking between the thread used to move motor and the
// write_Position method
//
// Revision 1.7  2006/05/24 14:12:07  etaurel
// - Several changes...
//
// Revision 1.6  2006/05/15 10:56:04  etaurel
// - Change the event used to report on motor movement from USER event to CHANGE event
//
// Revision 1.5  2006/04/27 07:28:44  etaurel
// - Many changes after the travel to Boston
//
// Revision 1.4  2006/03/27 12:53:49  etaurel
// - Commit before adding MotorGroup class
//
// Revision 1.3  2006/03/21 14:31:55  etaurel
// - Many changes.....
//
// Revision 1.2  2006/03/20 08:26:13  etaurel
// - Commit changes before changing the Motor interface
//
// Revision 1.1.1.1  2006/03/10 13:40:58  etaurel
// Initial import
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//-=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================



//===================================================================
//
//	The following table gives the correspondance
//	between commands and method's name.
//
//  Command's name  |  Method's name
//	----------------------------------------
//  State           |  dev_state()
//  Status          |  dev_status()
//  Abort           |  abort()
//  DefinePosition  |  define_position()
//  SaveConfig      |  save_config()
//  MoveRelative    |  move_relative()
//
//===================================================================

#include <math.h>

#include <CtrlFiCa.h>
#include <tango.h>
#include <Motor.h>
#include <MotorClass.h>
#include <MotorUtil.h>
#include <Pool.h>
#include <PoolThread.h>
#include <PseudoMotor.h>
#include <MotorGroup.h>


namespace Motor_ns
{

//+----------------------------------------------------------------------------
//
// method : 		Motor::Motor(string &s)
// 
// description : 	constructor for simulated Motor
//
// in : - cl : Pointer to the DeviceClass object
//      - s : Device name 
//
//-----------------------------------------------------------------------------
Motor::Motor(Tango::DeviceClass *cl,string &s)
//:Tango::Device_3Impl(cl,s.c_str())
:Pool_ns::PoolIndBaseDev(cl,s.c_str())
{
	init_cmd = false;
	init_device();
}

Motor::Motor(Tango::DeviceClass *cl,const char *s)
//:Tango::Device_3Impl(cl,s)
:Pool_ns::PoolIndBaseDev(cl,s)
{
	init_cmd = false;
	init_device();
}

Motor::Motor(Tango::DeviceClass *cl,const char *s,const char *d)
//:Tango::Device_3Impl(cl,s,d)
:Pool_ns::PoolIndBaseDev(cl,s,d)
{
	init_cmd = false;
	init_device();
}
//+----------------------------------------------------------------------------
//
// method : 		Motor::delete_device()
// 
// description : 	will be called at device destruction or at init command.
//
//-----------------------------------------------------------------------------
void Motor::delete_device()
{
	//	Delete device's allocated object


//
// A trick to inform client(s) listening on events that the pool device is down.
// Without this trick, the clients will have to wait for 3 seconds before being informed 
// This is the Tango device time-out.
// To know that we are executing this code due to a pool shutdown and not due to a
// "Init" command, we are using the polling thread ptr which is cleared in the DS
// shutdown sequence before the device destruction
//
	bool sd = false;
	
	Tango::Util *tg = Tango::Util::instance();
	if (tg->get_polling_thread_object() == NULL)
	{
		sd = true;
		struct timespec req_sleep;
		req_sleep.tv_sec = 0;
		req_sleep.tv_nsec = 500000000;
		
		pool_dev->set_moving_state();
		
		while(get_state() == Tango::MOVING)
		{
cout << "Waiting for end of mov of motor " << device_name << endl;
			nanosleep(&req_sleep,NULL);
		}
	}
	else
	{
		if (get_state() == Tango::MOVING)
		{
			TangoSys_OMemStream o;
			o << "Init command on motor device is not allowed while a motor is moving" << ends;

			Tango::Except::throw_exception((const char *)"Motor_InitNotAllowed",o.str(),
				  	(const char *)"Motor::delete_device");
		}
		

	}		
//
// If we are not in a shutdown sequence:
// Lock the ghost group in order the polling thread not to
// start requesting for motor state while we are deleting it and
// inform ghost group that there is one motor less
//
// If we are called due to a Init command on the DServer admin,
// the motor_group class is already deleted and the ghost group
// as well
//

	if (sd == false)
	{
		bool motorgroup_class_deleted = false;
		MotorGroup_ns::MotorGroup *ghost_ptr;
		
		try
		{
			ghost_ptr = pool_dev->get_ghost_motor_group_ptr();
		}
		catch (Tango::DevFailed &e)
		{
			motorgroup_class_deleted = true;
		}
		
		if (motorgroup_class_deleted == false)
		{
			Tango::AutoTangoMonitor atm(ghost_ptr);
			ghost_ptr->remove_motor_from_ghost_group(motor_id);
		}
	}
	delete pos_mon;
	if (save_atts != NULL)
		delete save_atts;
//
// Delete the device from its controller and from the pool
//

	delete_from_pool();
	delete_utils();
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::init_device()
// 
// description : 	will be called at device initialization.
//
//-----------------------------------------------------------------------------
void Motor::init_device()
{
	INFO_STREAM << "Motor::Motor() create device " << device_name << endl;

	// Initialise variables to default values
	//--------------------------------------------
	get_device_property();
	
	set_state(Tango::ON);
	string &_status = get_status();
	_status = StatusNotSet;

//
// If we are called due to a init command, also re-init variables in the
// base class
//

	if (init_cmd == true)
		base_init();
			
	init_from_db_done = false;
	save_atts = NULL;
	grp_mov = false;
	mot_NaN = strtod("NAN",NULL);
	motor_idx = ct_idx;
		
	pos_mon = new Tango::TangoMonitor("PoolThread");
	
	attr_Acceleration_write = 0.0;
	attr_Deceleration_write = 0.0;
	attr_Velocity_write = 0.0;
	attr_Base_rate_write = 0.0;
	attr_Position_write = 0.0;
	attr_Offset_write = 0.0;
	
	attr_Step_per_unit_write = 1.0;
	depl_per_step = 1.0;
	
	attr_Backlash_write = 0;
	backlash_depl = 0.0;
	back_pos = 0.0;
	writed_pos = 0.0;
	
	for (long l = 0;l < 3;l++)
		switches[l] = false;
	old_switches = 0;
	attr_Limit_switches_read = switches;
		
	attr_Position_read = &attr_Position_write;
	attr_SimulationMode_read = &simu;
	attr_Acceleration_read = &attr_Acceleration_write;
	attr_Velocity_read = &attr_Velocity_write;
	attr_Deceleration_read = &attr_Deceleration_write;
	attr_Base_rate_read = &attr_Base_rate_write;
	attr_Offset_read = &attr_Offset_write;
	attr_Step_per_unit_read = &attr_Step_per_unit_write;
	attr_Backlash_read = &attr_Backlash_write;

//
// Convert sleep before last read property into the right unit
//
	
	if (sleep_bef_last_read != 0)
	{
		if (sleep_bef_last_read < 1000)
		{
			sbr_sec = 0;
			sbr_nsec = sleep_bef_last_read * 1000000;
		}
		else
		{
			sbr_sec = (time_t)(sleep_bef_last_read / 1000);
			sbr_nsec = (sleep_bef_last_read - (sbr_sec * 1000)) * 1000000;
		}
	}
	else
	{
		sbr_sec = 0;
		sbr_nsec = 0;
	}
	
//
// We will push change event on State, Position and Limit_switches attributes
//

	Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
	state_att.set_change_event(true,false);
	
	Tango::Attribute &pos_att = dev_attr->get_attr_by_name("Position");
	pos_att.set_change_event(true);

	Tango::Attribute &l_switch = dev_attr->get_attr_by_name("Limit_Switches");
	l_switch.set_change_event(true,false);
	
//
// Build the PoolBaseUtils class depending on the
// controller type
//

	set_utils(new MotorUtil(pool_dev));
	
//
// Inform Pool of our birth
//

	Pool_ns::MotorPool ctp;
	init_pool_element(&ctp);
	
	{
		Tango::AutoTangoMonitor atm(pool_dev);	
		pool_dev->add_motor(ctp);
	}

			
//
// Inform controller of our birth
//

	if (my_ctrl != NULL)
	{
		a_new_child(ctp.ctrl_id);
			
//
// Set Step_per_unit, velocity, Base_rate, Acceleration and Deceleration to the values found from Db
//

		always_executed_hook();		
		if (get_state() != Tango::FAULT)
		{
			init_from_db();
		}	
	}
	else
		set_state(Tango::FAULT);

//
// If we are called due to a init command, update our info in the
// ghost group
//
		
	if (init_cmd == true)
	{
		MotorGroup_ns::MotorGroup *ghost_ptr = pool_dev->get_ghost_motor_group_ptr();
		{
			Tango::AutoTangoMonitor atm(ghost_ptr);
			ghost_ptr->add_motor_to_ghost_group(motor_id);
		}
		init_cmd = false;
	}
}

void Motor::init_pool_element(Pool_ns::PoolElement *pe)
{
	PoolIndBaseDev::init_pool_element(pe);
	
	Pool_ns::MotorPool *mp = static_cast<Pool_ns::MotorPool *>(pe);
	
	mp->motor = this;
}


//+----------------------------------------------------------------------------
//
// method : 		Motor::get_device_property()
// 
// description : 	Read the device properties from database.
//
//-----------------------------------------------------------------------------
void Motor::get_device_property()
{
	//	Initialize your default values here (if not done with  POGO).
	//------------------------------------------------------------------

	//	Read device properties from database.(Automatic code generation)
	//------------------------------------------------------------------
	Tango::DbData	dev_prop;
	dev_prop.push_back(Tango::DbDatum("Motor_id"));
	dev_prop.push_back(Tango::DbDatum("_Acceleration"));
	dev_prop.push_back(Tango::DbDatum("_Velocity"));
	dev_prop.push_back(Tango::DbDatum("_Base_rate"));
	dev_prop.push_back(Tango::DbDatum("_Deceleration"));
	dev_prop.push_back(Tango::DbDatum("Sleep_bef_last_read"));

	//	Call database and extract values
	//--------------------------------------------
	if (Tango::Util::instance()->_UseDb==true)
		get_db_device()->get_property(dev_prop);
	Tango::DbDatum	def_prop, cl_prop;
	MotorClass	*ds_class =
		(static_cast<MotorClass *>(get_device_class()));
	int	i = -1;

	//	Try to initialize Motor_id from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  motor_id;
	//	Try to initialize Motor_id from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  motor_id;
	//	And try to extract Motor_id value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_id;

	//	Try to initialize _Acceleration from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  _Acceleration;
	//	Try to initialize _Acceleration from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  _Acceleration;
	//	And try to extract _Acceleration value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  _Acceleration;

	//	Try to initialize _Velocity from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  _Velocity;
	//	Try to initialize _Velocity from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  _Velocity;
	//	And try to extract _Velocity value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  _Velocity;

	//	Try to initialize _Base_rate from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  _Base_rate;
	//	Try to initialize _Base_rate from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  _Base_rate;
	//	And try to extract _Base_rate value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  _Base_rate;

	//	Try to initialize _Deceleration from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  _Deceleration;
	//	Try to initialize _Deceleration from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  _Deceleration;
	//	And try to extract _Deceleration value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  _Deceleration;

	//	Try to initialize Sleep_bef_last_read from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  sleep_bef_last_read;
	//	Try to initialize Sleep_bef_last_read from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  sleep_bef_last_read;
	//	And try to extract Sleep_bef_last_read value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  sleep_bef_last_read;



	//	End of Automatic code generation
	//------------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//
// method : 		Motor::always_executed_hook()
// 
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void Motor::always_executed_hook()
{
	if (simu == false)
	{
		Tango::DevState old_state = get_state();
		
		if (fica_built == true)
		{
			Pool_ns::PoolLock &pl = fica_ptr->get_mon();
			Pool_ns::AutoPoolLock lo(pl);
			if ((my_ctrl == NULL) || (this->ctrl_code_online == false))
			{
				set_state(Tango::FAULT);
			}
			else
			{
				if (ctrl_dev_built == true)
				{
					MotorController::MotorState mi;
					try
					{
						
//
// There is a trick here for client getting position using polling mode
// The motion thread stores motor position in the polling buffer and
// the client is getting position from this polling buffer
// When the motion thread detects that the motion is over
// (state != MOVING), it invalidates data from the polling buffer and
// therefore all clients will get data from hardware access.
// What could happens, is that a client thread detects first the
// end of the motion (before the motion thread). If this thread
// immediately reads the position after it detects the motion end, it will
// get the last value written in the polling buffer because the mov thread has not
// yet invalidate it.
// Therefore, if the thread executing this code is not the mov thread and if the state
// changed from MOVING to ON, delay the state changes that it will be detected by the
// motion thread. This motion thread is doing a motor call every 10 mS
//

						int th_id = omni_thread::self()->id();

						read_state_from_ctrl(mi,false);
						
						set_state((Tango::DevState)mi.state);
						store_switches(mi.switches);

						if (mov_th_id != 0)
						{						
							if ((old_state == Tango::MOVING) && 
							    ((get_state() == Tango::ON) || (get_state() == Tango::ALARM)) && 
							    (th_id != mov_th_id) && 
							    (abort_cmd_executed == false))
									set_state(Tango::MOVING);
						}
							
						if ((mi.switches >= 2) && (get_state() != Tango::MOVING))
							set_state(Tango::ALARM);
						if ((Tango::DevState)mi.state == Tango::FAULT)
							ctrl_error_str = mi.status;
					}
					catch(Tango::DevFailed &e)
					{
						set_state(Tango::UNKNOWN);
						ctrl_error_str = "\nError reported from controller when requesting for motor state";
						ctrl_error_str = ctrl_error_str + "\n\t" + e.errors[0].desc.in();
					}					
				}
				else
				{
					set_state(Tango::FAULT);
				}
			}
		}
		else
		{
			set_state(Tango::FAULT);
		}

//
// If necessary notify the ghost group of changes in the motor.
// The ghost group will itself notify any internal listeners.
// During DS startup sequence, the motors are created before the ghost 
// group. Forget the exception throw if we call this method during startup
// sequence
//

		try
		{
			inform_ghost(old_state,get_state());
		}
		catch (Tango::DevFailed &e) {}
	}
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::inform_ghost
// 
// description : 	inform ghost group of a change in the state
//
//-----------------------------------------------------------------------------
void Motor::inform_ghost(Tango::DevState old_state,Tango::DevState new_state)
{
	if (old_state != Tango::MOVING)
	{
		if(old_state != new_state && 
	   	   new_state != Tango::ON &&
	       new_state != Tango::MOVING &&
	       new_state != Tango::ALARM)
		{
			MotorGroup_ns::MotorGroup *ghost = pool_dev->get_ghost_motor_group_ptr();
			long idx = ghost->get_ind_elt_idx_from_id(motor_id);
			Tango::AutoTangoMonitor synch(ghost);
			ghost->update_state_from_ctrls(idx,new_state);
		}
	}	
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_attr_hardware
// 
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
void Motor::read_attr_hardware(vector<long> &attr_list)
{
	DEBUG_STREAM << "Motor::read_attr_hardware(vector<long> &attr_list) entering... "<< endl;
	//	Add your own code here
}
//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Step_per_unit
// 
// description : 	Extract real attribute values for Step_per_unit acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Step_per_unit(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Step_per_unit(Tango::Attribute &attr) entering... "<< endl;
	attr.set_value(attr_Step_per_unit_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Step_per_unit
// 
// description : 	Write Step_per_unit attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Step_per_unit(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Step_per_unit(Tango::WAttribute &attr) entering... "<< endl;
	double old_step = attr_Step_per_unit_write;
	attr.get_write_value(attr_Step_per_unit_write);
	
	if (attr_Step_per_unit_write <= 0.0)
	{
		attr_Step_per_unit_write = old_step;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Step_per_unit cannot be negative or null",
					  (const char *)"Motor::write_Step_per_unit");
	}
	
	DEBUG_STREAM << "Motor: new Step_per_unit value = " << attr_Step_per_unit_write << endl;
	
//
// The Step_per_unit attribute is a memorized attribute. If we are in simulatioin mode,
// reset the value stored in db to the value it had when the simulation mode
// was set to true
//

	if (simu == true)
	{
		try
		{
			Tango::DbDevice *db_dev = get_db_device();
			Tango::DbDatum off("__value");
			Tango::DbDatum att("Step_per_unit");
			Tango::DbData db_data;

			short nb_att = 1;
			att << nb_att;		
			off << save_atts->simu_step;
			db_data.push_back(att);
			db_data.push_back(off);
			db_dev->put_attribute_property(db_data);
		}
		catch (Tango::DevFailed &e)
		{
			Tango::Except::print_exception(e);
			throw;
		}
	}
	else
	{
		string par_name("Step_per_unit");
		Controller::CtrlData cd;
		cd.data_type = Controller::DOUBLE;
		cd.db_data = attr_Step_per_unit_write;
	
		{
			Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
			try
			{
				MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
				typed_ctrl->SetPar(motor_idx,par_name,cd);
			}
			SAFE_CATCH(fica_ptr->get_name(),"write_Step_per_unit");
		}
	}
	
//
// Compute some values which are linked to the step per unit
//

	depl_per_step = 1 / attr_Step_per_unit_write;
	
	Pool_ns::MotCtrlFiCa *typed_fica_ptr = static_cast<Pool_ns::MotCtrlFiCa *>(fica_ptr);
	if (typed_fica_ptr->ctrl_has_backlash() == false)
		backlash_depl = attr_Backlash_write * depl_per_step;
		
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Backlash
// 
// description : 	Extract real attribute values for Backlash acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Backlash(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Backlash(Tango::Attribute &attr) entering... "<< endl;
	
	string par_name("Backlash");
	if (simu == false)
	{
		Pool_ns::MotCtrlFiCa *typed_fica_ptr = static_cast<Pool_ns::MotCtrlFiCa *>(fica_ptr);
		if (typed_fica_ptr->ctrl_has_backlash() == true)
		{
			Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
			Controller::CtrlData tmp_val;
			try
			{
				MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);				
				tmp_val = typed_ctrl->GetPar(motor_idx,par_name);
			}
			SAFE_CATCH(fica_ptr->get_name(),"read_Backlash");
		
			if (tmp_val.lo_data == LONG_MAX)
			{
				Tango::Except::throw_exception((const char *)"Motor_BadController",
					  (const char *)"The motor controller class has not re-defined method to get motor parameters",
					  (const char *)"Motor::read_backlash");
			}
			attr_Backlash_write = tmp_val.lo_data;
		}
	}	
	attr.set_value(attr_Backlash_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Backlash
// 
// description : 	Write Backlash attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Backlash(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Backlash(Tango::WAttribute &attr) entering... "<< endl;
	Tango::DevLong old_backlash = attr_Backlash_write;
	attr.get_write_value(attr_Backlash_write);
	DEBUG_STREAM << "Motor: new Backlash value = " << attr_Backlash_write << endl;
	
//
// The Backlash attribute is a memorized attribute. If we are in simulatioin mode,
// reset the value stored in db to the value it had when the simulation mode
// was set to true
//

	if (simu == true)
	{
		try
		{
			Tango::DbDevice *db_dev = get_db_device();
			Tango::DbDatum off("__value");
			Tango::DbDatum att("Backlash");
			Tango::DbData db_data;

			short nb_att = 1;
			att << nb_att;		
			off << save_atts->simu_backlash;
			db_data.push_back(att);
			db_data.push_back(off);
			db_dev->put_attribute_property(db_data);
		}
		catch (Tango::DevFailed &e)
		{
			Tango::Except::print_exception(e);
		}
	}
	else
	{
		
//
// If the backlash is done by the controller, send it the new value
//

		Pool_ns::MotCtrlFiCa *typed_fica_ptr = static_cast<Pool_ns::MotCtrlFiCa *>(fica_ptr);
		if (typed_fica_ptr->ctrl_has_backlash() == true)
		{
			string par_name("Backlash");
			Controller::CtrlData feat_value;
			feat_value.lo_data = attr_Backlash_write;
			feat_value.data_type = Controller::LONG;
				
			{
				Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
				try
				{
					MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
					typed_ctrl->SetPar(motor_idx,par_name,feat_value);
				}
				SAFE_CATCH(fica_ptr->get_name(),"write_Backlash");
			}
		}
		else
		{
			
//
// Compute the moving due to backlash
//

			backlash_depl = attr_Backlash_write * depl_per_step;
			
//
// Check if the position attribute has some limit defined
//

			Tango::Attribute &pos_att = dev_attr->get_attr_by_name("Position");
			Tango::AttributeConfig conf;
			pos_att.get_properties(conf);

//
// Compute new low limit position according to backlash
//

			double new_low_limit,new_upp_limit;			
			if (::strcmp(conf.min_value,AlrmValueNotSpec) != 0)
			{
				TangoSys_MemStream str;
				double old_min_value;

				str << conf.min_value;					
				str >> old_min_value;
				if (old_backlash > 0)
					old_min_value = old_min_value - (old_backlash * depl_per_step);

				if (attr_Backlash_write > 0)
					new_low_limit = old_min_value + backlash_depl;
				else
					new_low_limit = old_min_value;				
			}

//
// Compute new upper limit position according to backlash
//
			
			if (::strcmp(conf.max_value,AlrmValueNotSpec) != 0)
			{
				TangoSys_MemStream str;
				double old_max_value;

				str << conf.max_value;				
				str >> old_max_value;
				if (old_backlash < 0)
					old_max_value = old_max_value + (old_backlash * depl_per_step);
				
				if (attr_Backlash_write < 0)
					new_upp_limit = old_max_value + backlash_depl;	
				else
					new_upp_limit = old_max_value;			
			}
		}
	}	
}


//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Limit_switches
// 
// description : 	Extract real attribute values for Limit_switches acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Limit_switches(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Limit_switches(Tango::Attribute &attr) entering... "<< endl;
	attr.set_value(attr_Limit_switches_read,3);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Offset
// 
// description : 	Extract real attribute values for Offset acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Offset(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Offset(Tango::Attribute &attr) entering... "<< endl;
	attr.set_value(attr_Offset_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Offset
// 
// description : 	Write Offset attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Offset(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Offset(Tango::WAttribute &attr) entering... "<< endl;

	double old_offset = attr_Offset_write;	
	attr.get_write_value(attr_Offset_write);
	DEBUG_STREAM << "Motor: new Offset value = " << attr_Offset_write << endl;

//
// Compute mew limit positions for the Position attribute
//

	Tango::WAttribute &pos = get_device_attr()->get_w_attr_by_name("Position");
					
	bool min_set = pos.is_min_value();
	bool max_set = pos.is_max_value();

//
// Compute new values
//
					
	Tango::DevDouble limit;
								
	if (min_set == true)
	{
		pos.get_min_value(limit);
		double min_in_dial = limit - old_offset;
		double new_min_limit = min_in_dial + attr_Offset_write;
		pos.set_min_value(new_min_limit);
	}
	
	if (max_set == true)
	{
		pos.get_max_value(limit);
		double max_in_dial = limit - old_offset;
		double new_max_limit = max_in_dial + attr_Offset_write;
		pos.set_max_value(new_max_limit);
	}						
									
//
// The Offset attribute is a memorized attribute. If we are in simulatioin mode,
// reset the value stored in db to the value it had when the simulation mode
// was set to true
//

	if (simu == true)
	{
		try
		{
			Tango::DbDevice *db_dev = get_db_device();
			Tango::DbDatum off("__value");
			Tango::DbDatum att("Offset");
			Tango::DbData db_data;

			short nb_att = 1;
			att << nb_att;		
			off << save_atts->simu_offset;
			db_data.push_back(att);
			db_data.push_back(off);
			db_dev->put_attribute_property(db_data);
		}
		catch (Tango::DevFailed &e)
		{
			Tango::Except::print_exception(e);
		}
	}	
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_DialPosition
// 
// description : 	Extract real attribute values for DialPosition acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_DialPosition(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_DialPosition(Tango::Attribute &attr) entering... "<< endl;
	
	if (simu == false)
	{
		dial_pos = read_position_from_ctrl();
		attr.set_value(&dial_pos);
	}
	else
	{
		attr.set_value(&dial_pos);
	}

	Tango::DevState mot_sta = get_state();
	
	if (mot_sta == Tango::MOVING)
		attr.set_quality(Tango::ATTR_CHANGING);
	else if (mot_sta == Tango::ALARM)
	  	attr.set_quality(Tango::ATTR_ALARM);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Acceleration
// 
// description : 	Extract real attribute values for Acceleration acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Acceleration(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Acceleration(Tango::Attribute &attr) entering... "<< endl;

	string par_name("Acceleration");
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		Controller::CtrlData tmp_val;
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			tmp_val = typed_ctrl->GetPar(motor_idx,par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Acceleration");
		
		if ((tmp_val.data_type != Controller::DOUBLE) || (isnan(tmp_val.db_data) != 0))
		{
			Tango::Except::throw_exception((const char *)"Motor_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor parameters",
					  (const char *)"Motor::read_Acceleration");
		}
		attr_Acceleration_write = tmp_val.db_data;
	}	
	attr.set_value(attr_Acceleration_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Acceleration
// 
// description : 	Write Acceleration attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Acceleration(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Acceleration(Tango::WAttribute &attr) entering... "<< endl;

	double old_acc = attr_Acceleration_write;	
	attr.get_write_value(attr_Acceleration_write);
	DEBUG_STREAM << "Motor: new acceleration value = " << attr_Acceleration_write << endl;
	if (attr_Acceleration_write <= 0)
	{
		attr_Acceleration_write = old_acc;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Acceleration cannot be negative or null",
					  (const char *)"Motor::write_acceleration");
	}

	string par_name("Acceleration");
	Controller::CtrlData tmp_data;
	tmp_data.data_type = Controller::DOUBLE;
	tmp_data.db_data = attr_Acceleration_write;
	
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->SetPar(motor_idx,par_name,tmp_data);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Acceleration");
	}
	
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Velocity
// 
// description : 	Extract real attribute values for Velocity acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Velocity(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Velocity(Tango::Attribute &attr) entering... "<< endl;

	string par_name("Velocity");
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		Controller::CtrlData tmp_val;
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			tmp_val = typed_ctrl->GetPar(motor_idx,par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Velocity");
		
		if ((tmp_val.data_type != Controller::DOUBLE) || (isnan(tmp_val.db_data) != 0))
		{
			Tango::Except::throw_exception((const char *)"Motor_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor parameters",
					  (const char *)"Motor::read_Velocity");
		}
		attr_Velocity_write = tmp_val.db_data;
	}	
	attr.set_value(attr_Velocity_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Velocity
// 
// description : 	Write Velocity attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Velocity(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Velocity(Tango::WAttribute &attr) entering... "<< endl;

	double old_velo = attr_Velocity_write;	
	attr.get_write_value(attr_Velocity_write);
	DEBUG_STREAM << "Motor: new velocity value = " << attr_Velocity_write << endl;
	if (attr_Velocity_write <= 0)
	{
		attr_Velocity_write = old_velo;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Velocity cannot be negative or null",
					  (const char *)"Motor::write_velocity");
	}
	if (attr_Velocity_write <= attr_Base_rate_write)
	{
		attr_Velocity_write = old_velo;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Velocity cannot be less or equal to base rate",
					  (const char *)"Motor::write_velocity");
	}	

	string par_name("Velocity");
	Controller::CtrlData tmp_data;
	tmp_data.data_type = Controller::DOUBLE;
	tmp_data.db_data = attr_Velocity_write;
		
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->SetPar(motor_idx,par_name,tmp_data);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Velocity");
	}

}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Base_rate
// 
// description : 	Extract real attribute values for Base_rate acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Base_rate(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Base_rate(Tango::Attribute &attr) entering... "<< endl;

	string par_name("Base_rate");
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		Controller::CtrlData tmp_val;
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			tmp_val = typed_ctrl->GetPar(motor_idx,par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Base_rate");
		
		if ((tmp_val.data_type != Controller::DOUBLE) || (isnan(tmp_val.db_data) != 0))
		{
			Tango::Except::throw_exception((const char *)"Motor_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor parameters",
					  (const char *)"Motor::read_Base_rate");
		}
		attr_Base_rate_write = tmp_val.db_data;
	}		
	attr.set_value(attr_Base_rate_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Base_rate
// 
// description : 	Write Base_rate attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Base_rate(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Base_rate(Tango::WAttribute &attr) entering... "<< endl;

	double old_base = attr_Base_rate_write;	
	attr.get_write_value(attr_Base_rate_write);
	DEBUG_STREAM << "Motor: new Base_rate value = " << attr_Base_rate_write << endl;
	if (attr_Base_rate_write <= 0)
	{
		attr_Base_rate_write = old_base;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Base rate cannot be negative or null",
					  (const char *)"Motor::write_Base_rate");
	}
	if (attr_Base_rate_write >= attr_Velocity_write)
	{
		attr_Base_rate_write = old_base;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Base rate cannot be greater or equal to velocity",
					  (const char *)"Motor::write_Base_rate");
	}		
	
	string par_name("Base_rate");
	Controller::CtrlData tmp_val;
	tmp_val.data_type = Controller::DOUBLE;
	tmp_val.db_data = attr_Base_rate_write;
	
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->SetPar(motor_idx,par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Base_rate");
	}
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Deceleration
// 
// description : 	Extract real attribute values for Deceleration acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Deceleration(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Deceleration(Tango::Attribute &attr) entering... "<< endl;

	string par_name("Deceleration");
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		Controller::CtrlData tmp_val;
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			tmp_val = typed_ctrl->GetPar(motor_idx,par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Deceleration");
		
		if ((tmp_val.data_type != Controller::DOUBLE) || (isnan(tmp_val.db_data) != 0))
		{
			Tango::Except::throw_exception((const char *)"Motor_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor parameters",
					  (const char *)"Motor::read_deceleration");
		}
		attr_Deceleration_write = tmp_val.db_data;
	}		
	attr.set_value(attr_Deceleration_read);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Deceleration
// 
// description : 	Write Deceleration attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Deceleration(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Deceleration(Tango::WAttribute &attr) entering... "<< endl;

	double old_dec = attr_Deceleration_write;	
	attr.get_write_value(attr_Deceleration_write);
	DEBUG_STREAM << "Motor: new deceleration value = " << attr_Deceleration_write << endl;
	if (attr_Deceleration_write <= 0)
	{
		attr_Deceleration_write = old_dec;
		Tango::Except::throw_exception((const char *)"Motor_BadArgument",
					  (const char *)"Deceleration cannot be negative or null",
					  (const char *)"Motor::write_deceleration");
	}
	
	string par_name("Deceleration");
	Controller::CtrlData tmp_val;
	tmp_val.data_type = Controller::DOUBLE;
	tmp_val.db_data = attr_Deceleration_write;
		
	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->SetPar(motor_idx,par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Deceleration");
	}
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_SimulationMode
// 
// description : 	Extract real attribute values for SimulationMode acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_SimulationMode(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_SimulationMode(Tango::Attribute &attr) entering... "<< endl;
	
	attr.set_value(attr_SimulationMode_read);
}


//+----------------------------------------------------------------------------
//
// method : 		Motor::read_Position
// 
// description : 	Extract real attribute values for Position acquisition result.
//
//-----------------------------------------------------------------------------
void Motor::read_Position(Tango::Attribute &attr)
{
	DEBUG_STREAM << "Motor::read_Position(Tango::Attribute &attr) entering... "<< endl;

	if (simu == false)
	{	
		dial_pos = read_position_from_ctrl();
		attr_Position_write = dial_pos + attr_Offset_write;
		attr.set_value(attr_Position_read);
	}
	else
	{
		attr_Position_write_simu = dial_pos + attr_Offset_write;
		attr.set_value(&attr_Position_write_simu);
	}
		
	Tango::DevState mot_sta = get_state();

//
// Set the attribute quality factor
// Do not forget to take the backlash into account
//
	
	if (mot_sta == Tango::MOVING)
		attr.set_quality(Tango::ATTR_CHANGING);
	else if (mot_sta == Tango::ALARM)
	  	attr.set_quality(Tango::ATTR_ALARM);
	else if ((mot_sta == Tango::ON) && (get_back_pos() != 0.0) && (get_writed_pos() == dial_pos))
		attr.set_quality(Tango::ATTR_CHANGING);
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::write_Position
// 
// description : 	Write Position attribute values to hardware.
//
//-----------------------------------------------------------------------------
void Motor::write_Position(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "Motor::write_Position(Tango::WAttribute &attr) entering..."<< endl;

	double old_pos = attr_Position_write;
	double old_dial = dial_pos;
		
	attr.get_write_value(attr_Position_write);
	DEBUG_STREAM << "Motor::write_Position: New position = " << attr_Position_write << endl;

//
// If this motor is used as one of pseudo-motor element,
// and if this pseudo-motor has a min or max value
// set, ask the pm if it accepts this new motor value.
// It is not necessary to do this check if this method is called by the motion
// thread. In this case, this kind of check has already been done and it is not
// necessary to do it once more.
//

	int th_id = omni_thread::self()->id();

	if ((mov_th_id != 0) && (th_id != mov_th_id))
	{								
		list<Pool_ns::PseudoMotorPool>::iterator psm_ite;
		list<Pool_ns::PseudoMotorPool> &psm_list = pool_dev->get_psm_list();

		{
			Tango::AutoTangoMonitor atm(pool_dev);
				
			for (psm_ite = psm_list.begin();psm_ite != psm_list.end();++psm_ite)
			{
				if (psm_ite->is_member(alias) == true)
				{
					Tango::WAttribute &pos = psm_ite->pseudo_motor->get_device_attr()->get_w_attr_by_name("Position");
					
					bool min_set = pos.is_min_value();
					bool max_set = pos.is_max_value();
					
					Tango::DevDouble limit;
					double pm_pos;
								
					if ((min_set == true) || (max_set == true))
					{
						pm_pos = psm_ite->pseudo_motor->calc_pseudo(alias,attr_Position_write);
					}

//
// Check minimum value
//	
		
					if (min_set == true)
					{
						pos.get_min_value(limit);
						if (pm_pos < limit)
						{
							TangoSys_OMemStream o;
							o << "Motor device " << get_name() << " is used for pseudo-motor" << psm_ite->name;
							o << "\n. This pseudo-motor has a minimum authorized value of " << limit;
							o << "\n. Sending motor to the requested position will make the pseudo-motor having a position" ;
							o << " below the minimum authorized" << ends;
		
							Tango::Except::throw_exception((const char *)"Motor_BadParameter",o.str(),
						  								   (const char *)"Motor::write_Position");
						}
					}
			
//
// Check maximum value
//

					if (max_set == true)
					{
						pos.get_max_value(limit);
						if (pm_pos > limit)
						{
							TangoSys_OMemStream o;
							o << "Motor device " << get_name() << " is used for pseudo-motor" << psm_ite->name;
							o << "\n. This pseudo-motor has a maximum authorized value of " << limit;
							o << "\n. Sending motor to the requested position will make the pseudo-motor having a position" ;
							o << " above the maximum authorized" << ends;
		
							Tango::Except::throw_exception((const char *)"Motor_BadParameter",o.str(),
						  								   (const char *)"Motor::write_Position");
						}
					}
				}
			}
		}
	}
	
//
// Compute dial pos
//

	dial_pos = attr_Position_write - attr_Offset_write;

//
// Add backlash if necessary
//

	bool modified_pos = false;
	back_pos = 0.0;
	Pool_ns::MotCtrlFiCa *typed_fica_ptr = static_cast<Pool_ns::MotCtrlFiCa *>(fica_ptr);
	
	if ((attr_Backlash_write != 0.0) && typed_fica_ptr->ctrl_has_backlash() == false)
	{
		bool pos_depl = false;
		if (dial_pos > old_dial)
			pos_depl = true;
		if (attr_Backlash_write > 0.0)
		{
			if (pos_depl == false)
			{
				modified_pos = true;
				dial_pos = dial_pos - backlash_depl;
			}
		}
		else
		{
			if (pos_depl == true)
			{
				modified_pos = true;
				dial_pos = dial_pos - backlash_depl;
			}
		}
	}
	
//
// Compute a rounding value if necessary
//

	if (typed_fica_ptr->ctrl_want_rounding() == true)
	{
		double nb_step  = round(dial_pos / depl_per_step);
		dial_pos = nb_step * depl_per_step;
	}
	if (modified_pos == true)
		back_pos = dial_pos + backlash_depl;
	writed_pos = dial_pos;

//
// Check if the movement is allowed (due to limit switches)
//

/*	bool throw_ex = false;	
	if ((switches[1] == true) && (dial_pos >= old_dial))
	{
		throw_ex = true;
	}
	
	if ((throw_ex == false) && (switches[2] == true) && (dial_pos <= old_dial))
	{
		throw_ex = true;
	}
	
	if (throw_ex == true)
	{
		Tango::Except::throw_exception((const char *)"Motor_BadParameter",
				  (const char *)"The motor ia already on a limit switch. Your movement is not possible",
				  (const char *)"Motor::write_Position");
	}*/

//
// Do the movement
//	
				
	if (simu == false)
	{
		vector<long> mot_id_vector;
		mot_id_vector.push_back(motor_id);
		vector<double> pos_vector;
		pos_vector.push_back(dial_pos);

		th_failed = false;
		abort_cmd_executed = false;
		if (grp_mov == false)
		{
			
//
// Create the movement thread, but start it only while the pos_mon
// lock is taken. Otherwise, a dead-lock can happen, if the thread
// start excuting its code just after the start and before this code
// enter into the wait. The thread will send the signal but while
// this thread is not yet waiting for it and afterwards, we will have
// a dead-lock...
//
	
			Pool_ns::PoolThread *pool_th = new Pool_ns::PoolThread(mot_id_vector,pos_vector,pool_dev,pos_mon);

			{
				omni_mutex_lock lo(*pos_mon);
				pool_th->start();
				pos_mon->wait();
			}
		
			if (th_failed == true)
			{
				attr_Position_write = old_pos;
				dial_pos = old_dial;
			
				Tango::DevFailed ex(th_except);
				throw ex;
			}
		}
	}
	else
	{
		
//
// Fire events on state and position like the motion thread is doing
//

		Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
		set_state(Tango::MOVING);
		state_att.fire_change_event();
		
		set_state(Tango::ON);
		state_att.fire_change_event();
				
		read_Position(attr);
		attr.set_change_event(true,false);
		attr.fire_change_event();
		attr.set_change_event(true);
	}		
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::read_position_from_ctrl
// 
// description : 	Extract real attribute values for Position acquisition result.
//
//-----------------------------------------------------------------------------

double Motor::read_position_from_ctrl()
{
	double tmp_pos;
	Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());

	try
	{
		MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
		
		typed_ctrl->PreReadAll();
		typed_ctrl->PreReadOne(motor_idx);
		typed_ctrl->ReadAll();
		tmp_pos = typed_ctrl->ReadOne(motor_idx);
	}
	SAFE_CATCH(fica_ptr->get_name(),"read_position_from_ctrl");
		
	if (isnan(tmp_pos) != 0)
	{
		Tango::Except::throw_exception((const char *)"Motor_BadController",
				  (const char *)"The motor controller class has not re-defined method to read position (readOne(...))",
				  (const char *)"Motor::read_Position");
	}
	return tmp_pos;
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::set_state_from_group
// 
// description : 	Set the device state from the info gathered by a state
//					command on a group from which this motor is one of the element
//
//-----------------------------------------------------------------------------

void Motor::set_motor_state_from_group(MotorController::MotorState &mi)
{
	set_state((Tango::DevState)mi.state);
	switches[0] = mi.switches & 0x1;
	switches[1] = mi.switches & 0x2;
	switches[2] = mi.switches & 0x4;
							
	if ((mi.switches >= 2) && ((Tango::DevState)mi.state != Tango::MOVING))
		set_state(Tango::ALARM);
	if ((Tango::DevState)mi.state == Tango::FAULT)
		ctrl_error_str = mi.status;
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::init_from_db
// 
// description : 	Write the value found in DB for Velocity, Acceleration,
//					Deceleration and Base_rate in the device
//
//-----------------------------------------------------------------------------

void Motor::init_from_db()
{
	
	Tango::MultiAttribute *dev_attrs = get_device_attr();
	
//
// Retrieve the memorized value of the Step per unit attribute.
// The value is written into db by Tango kernel but we want to send it
// to the ctrl as the first parameter
//

	Tango::WAttribute &spu = dev_attrs->get_w_attr_by_name("Step_per_unit");
	string &mem_value = spu.get_mem_value();

	if (mem_value != MemNotUsed)
	{
		TangoSys_MemStream str;
		str << mem_value << ends;
					
		str >> attr_Step_per_unit_write;
	}
	else
		attr_Step_per_unit_write = 1.0;
	
	spu.set_write_value(attr_Step_per_unit_write);
	write_Step_per_unit(spu);
		
//
// The velocity
//

	Tango::WAttribute &vel_att = dev_attrs->get_w_attr_by_name("Velocity");
	if (_Velocity != -1)
	{
		vel_att.set_write_value(_Velocity);
		write_Velocity(vel_att);
	}
	else
	{
		read_Velocity(vel_att);
		vel_att.set_write_value(attr_Velocity_write);
	}

//
// Now, the acceleration
//

	Tango::WAttribute &acc_att = dev_attrs->get_w_attr_by_name("Acceleration");
	if (_Acceleration != -1)
	{
		acc_att.set_write_value(_Acceleration);
		write_Acceleration(acc_att);
	}
	else
	{
		read_Acceleration(acc_att);
		acc_att.set_write_value(attr_Acceleration_write);
	}	
			
//
// The deceleration
//

	Tango::WAttribute &dec_att = dev_attrs->get_w_attr_by_name("Deceleration");
	if (_Deceleration != -1)
	{
		dec_att.set_write_value(_Deceleration);
		write_Deceleration(dec_att);
	}
	else
	{
		read_Deceleration(dec_att);
		dec_att.set_write_value(attr_Deceleration_write);
	}

//
// Finally the Base_rate
//

	Tango::WAttribute &base_att = dev_attrs->get_w_attr_by_name("Base_rate");
	if (_Base_rate != -1)
	{
		base_att.set_write_value(_Base_rate);
		write_Base_rate(base_att);
	}
	else
	{
		read_Base_rate(base_att);
		base_att.set_write_value(attr_Base_rate_write);
	}
			
	init_from_db_done = true;
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::abort
 *
 *	description:	method to execute "Abort"
 *	Abort a running movement
 *
 *
 */
//+------------------------------------------------------------------
void Motor::abort()
{
	DEBUG_STREAM << "Motor::abort(): entering... !" << endl;

	//	Add your own code to control device here
	base_abort(false);
}

void Motor::base_abort(bool send_evt)
{
	DEBUG_STREAM << "Motor::abort(): entering... !" << endl;

	//	Add your own code to control device here

//
// Do nothing if the motor is not moving
//
	Tango::DevState initial_state = get_state();
	if (initial_state != Tango::MOVING)
		return;
		
//
// Send abort command to the controller
//

	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->AbortOne(motor_idx);
		}
		SAFE_CATCH(fica_ptr->get_name(),"abort");

		abort_cmd_executed = true;		

		if(send_evt == true)
		{

			always_executed_hook();
			Tango::MultiAttribute *dev_attrs = get_device_attr();
			Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
			state_att.fire_change_event();
			
			Pool_ns::MotorPool &mp = pool_dev->get_motor_from_id(motor_id);
			
			if(mp.has_listeners())
			{
				Pool_ns::PoolElementEvent evt(Pool_ns::StateChange, &mp);
				evt.old_state = initial_state;
				evt.new_state = get_state();
				
				mp.fire_pool_elem_change(&evt);
			}
	//
	// Position attribute quality factor is VALID
	//
	
			Tango::WAttribute &vel_att = dev_attrs->get_w_attr_by_name("Position");
			vel_att.set_quality(Tango::ATTR_VALID);
		}
	}
	else
	{
		Tango::Except::throw_exception((const char *)"Motor_SimuMode",
									   (const char *)"Command not allowed when motor is in simulation mode",
									   (const char *)"Motor::abort");
	}
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::define_position
 *
 *	description:	method to execute "DefinePosition"
 *	Define the motor position
 *
 * @param	argin	New position
 *
 */
//+------------------------------------------------------------------
void Motor::define_position(Tango::DevDouble argin)
{
	DEBUG_STREAM << "Motor::define_position(): entering... !" << endl;

	//	Add your own code to control device here

//
// Compute a rounding value if necessary
//
	double old_pos = attr_Position_write;
	
	Pool_ns::MotCtrlFiCa *typed_fica_ptr = static_cast<Pool_ns::MotCtrlFiCa *>(fica_ptr);
	if (typed_fica_ptr->ctrl_want_rounding() == true)
	{
		double nb_step  = round(argin / depl_per_step);
		argin = nb_step * depl_per_step;
	}
	
//
// Inform controller
//

	if (simu == false)
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			MotorController *typed_ctrl = static_cast<MotorController *>(my_ctrl);
			typed_ctrl->DefinePosition(motor_idx,argin);
		}
		SAFE_CATCH(fica_ptr->get_name(),"define_position()");
	}

	attr_Position_write = argin;

	Tango::MultiAttribute *dev_attrs = get_device_attr();		
	Tango::WAttribute &pos_att = dev_attrs->get_w_attr_by_name("Position");
	pos_att.set_write_value(argin);
	
	pos_att.set_value(attr_Position_read);
	
	bool check_change_criteria = pos_att.is_check_change_criteria(); 
	
	if(check_change_criteria == true)
		pos_att.set_change_event(true,false);

	pos_att.fire_change_event();
	
	if(check_change_criteria)
		pos_att.set_change_event(true,true);
	
	Pool_ns::PoolElement &m = get_pool_obj();
	if(m.has_listeners())
	{
		Pool_ns::PoolElementEvent evt(Pool_ns::PositionChange,&m);
		evt.old_value = old_pos;
		evt.new_value = attr_Position_write;
		evt.priority = true;
		m.fire_pool_elem_change(&evt);
	}
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::save_config
 *
 *	description:	method to execute "SaveConfig"
 *	Write motor parameters in database
 *
 *
 */
//+------------------------------------------------------------------
void Motor::save_config()
{
	DEBUG_STREAM << "Motor::save_config(): entering... !" << endl;

	//	Add your own code to control device here

	if (Tango::Util::instance()->_UseDb==false)
	{
		TangoSys_OMemStream o;
		o << "Motor device " << get_name() << " is not using database.";
		o << "\n. Command SaveConfig is not usable in this case" << ends;

		Tango::Except::throw_exception((const char *)"Motor_CantSaveConfig",o.str(),
				  (const char *)"Motor::save_config");
	}
	
	if (simu == true)
	{
		Tango::Except::throw_exception((const char *)"Motor_SimuMode",
									   (const char *)"Command not allowed when motor is in simulation mode",
									   (const char *)"Motor::save_config");
	}

	Tango::DbData	dev_prop;

	Tango::DbDatum acc("_Acceleration");
	acc << attr_Acceleration_write;
	dev_prop.push_back(acc);

	Tango::DbDatum vel("_Velocity");
	vel << attr_Velocity_write;
	dev_prop.push_back(vel);

	Tango::DbDatum base("_Base_rate");
	base << attr_Base_rate_write;	
	dev_prop.push_back(base);

	Tango::DbDatum dec("_Deceleration");
	dec << attr_Deceleration_write;	
	dev_prop.push_back(dec);

//
// Store values in database
//

	get_db_device()->put_property(dev_prop);
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::dev_status
 *
 *	description:	method to execute "Status"
 *	This command gets the device status (stored in its <i>device_status</i> data member) and returns it to the caller.
 *
 * @return	Status descrition
 *
 */
//+------------------------------------------------------------------
Tango::ConstDevString Motor::dev_status()
{
	Tango::ConstDevString	argout = DeviceImpl::dev_status();
	DEBUG_STREAM << "Motor::dev_status(): entering... !" << endl;

	//	Add your own code to control device here

	base_dev_status(argout);
	
	if (get_state() == Tango::ALARM)
	{
		if (switches[0] == true)
			tmp_status = tmp_status + "\nMotor is at home position";
		else if (switches[1] == true)
			tmp_status = tmp_status + "\nMotor is on upper switch";
		else if (switches[2] ==true)
			tmp_status = tmp_status + "\nMotor is on lower switch";
	}
		
	argout = tmp_status.c_str();
	return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::store_switches
 *
 *	description:	Store the new switches value and fire a change event
 * 					if they have changed
 * 
 *  args : - switch_val : The new swiches value
 *
 */
//+------------------------------------------------------------------
void Motor::store_switches(long &switch_val)
{

	if (old_switches != switch_val)
	{
			
//
// Store the new value
//

		switches[0] = switch_val & 0x1;
		switches[1] = switch_val & 0x2;
		switches[2] = switch_val & 0x4;
		
//
// Fire the event
//

		Tango::Attribute &l_switch = dev_attr->get_attr_by_name("Limit_Switches");
		l_switch.set_value(attr_Limit_switches_read,3);
		l_switch.fire_change_event();	
			
//
// Store the new value
//

		old_switches = switch_val;
	}
}



Motor::Simu_data::Simu_data(Motor *motor):mot(motor)
{
	Tango::AutoTangoMonitor atm(mot);
	
	simu_pos = mot->attr_Position_write;
	simu_acc = mot->attr_Acceleration_write;
	simu_dec = mot->attr_Deceleration_write;
	simu_vel = mot->attr_Velocity_write;
	simu_base = mot->attr_Base_rate_write;
	simu_offset = mot->attr_Offset_write;
	simu_step = mot->attr_Step_per_unit_write;
	simu_backlash = mot->attr_Backlash_write;
}

Motor::Simu_data::~Simu_data()
{
	Tango::AutoTangoMonitor atm(mot);
	
	Tango::MultiAttribute *ma_ptr = mot->get_device_attr();
	
	if (mot->attr_Position_write != simu_pos)
	{
		mot->attr_Position_write = simu_pos;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Position");
		att.set_write_value(simu_pos);
	}
	
	if (mot->attr_Acceleration_write != simu_acc)
	{
		mot->attr_Acceleration_write = simu_acc;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Acceleration");
		att.set_write_value(simu_acc);
	}
	
	if (mot->attr_Deceleration_write != simu_dec)
	{
		mot->attr_Deceleration_write = simu_dec;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Deceleration");
		att.set_write_value(simu_dec);
	}
			
	if (mot->attr_Velocity_write != simu_vel)
	{
		mot->attr_Velocity_write = simu_vel;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Velocity");
		att.set_write_value(simu_vel);
	}
	
	if (mot->attr_Base_rate_write != simu_base)
	{
		mot->attr_Base_rate_write = simu_base;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Base_rate");
		att.set_write_value(simu_base);
	}

	if (mot->attr_Offset_write != simu_offset)
	{	
		mot->attr_Offset_write = simu_offset;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Offset");
		att.set_write_value(simu_offset);
	}
	
	if (mot->attr_Step_per_unit_write != simu_step)
	{	
		mot->attr_Step_per_unit_write = simu_offset;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Step_per_unit");
		att.set_write_value(simu_step);
	}
	
	if (mot->attr_Backlash_write != simu_backlash)
	{	
		mot->attr_Step_per_unit_write = simu_backlash;
		Tango::WAttribute &att = ma_ptr->get_w_attr_by_name("Backlash");
		att.set_write_value(simu_backlash);
	}
}

//+----------------------------------------------------------------------------
//
// method : 		Motor::get_pool_obj
// 
// description : 	gets Pool motor object for this motor
//                  Warning: the following method should only be executed
//                  when the running thread has a lock on the Pool
//
// \return the pool motor
//-----------------------------------------------------------------------------

Pool_ns::PoolElement &Motor::get_pool_obj()
{ 
	return pool_dev->get_motor_from_id(motor_id); 
}

//+------------------------------------------------------------------
/**
 *	method:	Motor::move_relative
 *
 *	description:	method to execute "MoveRelative"
 *	Move relative command
 *
 * @param	argin	amount to move
 *
 */
//+------------------------------------------------------------------
void Motor::move_relative(Tango::DevDouble argin)
{
	DEBUG_STREAM << "Motor::move_relative(): entering... !" << endl;

	//	Add your own code to control device here
	Tango::Except::throw_exception(
			(const char *)"Motor_FeatureNotImplemented",
			(const char *)"This feature has not been implementd yet",
			(const char *)"Motor::move_relative");	
}

}	//	namespace
