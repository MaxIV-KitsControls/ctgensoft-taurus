static const char *RcsId = "$Header$";
//+=============================================================================
//
// file :         MotorGroup.cpp
//
// description :  C++ source for the MotorGroup and its commands. 
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                MotorGroup are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.58  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.57  2007/08/24 15:55:26  tcoutinho
// safety weekend commit
//
// Revision 1.56  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.55  2007/08/17 13:07:29  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.54  2007/08/07 09:51:06  tcoutinho
// Fix bug 24: Motor.state() and ghostGroup.state() return different states
//
// Revision 1.53  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.52  2007/05/31 09:53:54  etaurel
// - Fix some memory leaks
//
// Revision 1.51  2007/05/30 14:56:35  etaurel
// - Change the way the group state_array is populated when element are
// added/removed from the group
// - Do not get state from hardware while the pool is executing an Init
// command on the pool device
//
// Revision 1.50  2007/05/25 07:20:02  tcoutinho
// - fix internal event propagation to ghost motor group when client asks for state and the new calculated state is different from the one previously stored
//
// Revision 1.49  2007/05/24 09:24:07  tcoutinho
// - fixes to the position attribute quality
//
// Revision 1.48  2007/05/23 12:58:00  tcoutinho
// - fix bug in abort command: abort does not send state event anymore. Because deceleration can be very slow this is now done by the PoolThread.
// - fix position quality due to internal events
//
// Revision 1.47  2007/05/22 12:57:13  etaurel
// - Fix some bugs in event propagation
//
// Revision 1.46  2007/05/17 13:02:46  etaurel
// - Fix bug in reading_position and in state computation
//
// Revision 1.45  2007/05/17 09:31:36  tcoutinho
// - fix potential bug.
//
// Revision 1.44  2007/05/17 07:01:34  etaurel
// - Some tabs....
//
// Revision 1.43  2007/05/16 16:26:22  tcoutinho
// - fix dead lock
//
// Revision 1.42  2007/05/16 09:41:56  tcoutinho
// small code changes. No change in behaviour
//
// Revision 1.41  2007/05/15 15:02:40  tcoutinho
// - fix bugs
//
// Revision 1.40  2007/05/15 07:21:14  etaurel
// - Add a lock to protect the call to "update_state_from_ctrl" method
//
// Revision 1.39  2007/05/11 08:08:31  tcoutinho
// - fixed bugs
//
// Revision 1.38  2007/04/30 14:51:20  tcoutinho
// - make possible to Add/Remove elements on motorgroup that are part of other motor group(s)
//
// Revision 1.37  2007/04/26 08:23:04  tcoutinho
// - implemented add/remove elements feature
//
// Revision 1.36  2007/04/23 15:18:59  tcoutinho
// - first changes according to Sardana metting 26-03-2007: identical motor groups can be created, Add/Remove element from a MG, etc
//
// Revision 1.35  2007/02/22 11:57:41  tcoutinho
// - fix missing clear of containers
//
// Revision 1.34  2007/02/19 09:36:26  tcoutinho
// - Fix status bug
//
// Revision 1.33  2007/02/16 10:03:16  tcoutinho
// - development checkin related with measurement group
//
// Revision 1.32  2007/02/13 14:39:42  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.31  2007/02/08 09:40:17  etaurel
// - MAny changes after compilation -Wall
//
// Revision 1.30  2007/02/06 19:11:23  tcoutinho
// safe guard commit
//
// Revision 1.29  2007/02/06 09:37:45  tcoutinho
// - Motor Group now uses PoolGroupBaseDev
//
// Revision 1.28  2007/01/26 08:36:17  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.27  2007/01/23 08:30:12  tcoutinho
// -fixed error when user does not specify the pseudo_motor_roles attribute (case of only one pseudo motor)
//
// Revision 1.26  2007/01/16 14:27:36  etaurel
// - Change some names in the Pool structures
//
// Revision 1.25  2007/01/12 12:39:39  tcoutinho
// fix wrong commented line
//
// Revision 1.24  2007/01/12 12:03:02  tcoutinho
// fixed event changes
//
// Revision 1.23  2007/01/05 14:58:23  etaurel
// - Remove some print
//
// Revision 1.22  2007/01/05 13:03:56  tcoutinho
// -changes to internal event mechanism
// -support for gcc 4.1.1 compilation without errors
//
// Revision 1.21  2007/01/04 11:54:31  etaurel
// - Added the CounterTimer controller
//
// Revision 1.20  2006/12/28 15:35:13  etaurel
// - Clear group implied controllers vector during a "Init" command
//
// Revision 1.19  2006/12/20 10:40:21  tcoutinho
// - change: when an internal state change is received, the MG asks the Ctrl(s) for their state. This improves state changes event times in case some motors are in wrong state
//
// Revision 1.18  2006/12/20 10:26:08  tcoutinho
// - changes to support internal event propagation
// - bug fix in motor groups containing other motor groups or pseudo motors
//
// Revision 1.17  2006/12/18 11:39:45  etaurel
// - Add a print message
//
// Revision 1.16  2006/12/12 11:09:20  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.15  2006/12/11 16:37:29  tcoutinho
// - safety commit (before supporting pseudo motors in motor groups)
//
// Revision 1.14  2006/12/05 10:13:45  etaurel
// - Add a check on ctrl validity in the always_executed_hook() and a dev_status() method
//
// Revision 1.13  2006/11/24 08:46:45  tcoutinho
// - support for pseudo motors in motor group
//
// Revision 1.12  2006/11/20 14:35:16  etaurel
// - Add ghost group and event on group position
//
// Revision 1.11  2006/11/07 15:07:57  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.10  2006/11/03 15:48:27  etaurel
// - Miscellaneous changes that I don't remember
//
// Revision 1.9  2006/10/25 10:05:20  etaurel
// - Complete implementation of the ReloadControllerCode command
// - Handle end of movment when reading position in polling mode
//
// Revision 1.8  2006/10/20 15:42:38  etaurel
// - First release with GetControllerInfo command supported and with
// controller properties
//
// Revision 1.7  2006/09/21 10:21:10  etaurel
// - The motor group do not ID any more
//
// Revision 1.6  2006/09/21 08:02:15  etaurel
// - Now all test suite is OK withou ID on motor interface
//
// Revision 1.5  2006/09/21 07:26:38  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.4  2006/08/08 12:16:54  etaurel
// - It now uses the multi-motor controller interface
//
// Revision 1.3  2006/07/07 13:39:50  etaurel
// - Fix a small bug in the init_device() method
//
// Revision 1.2  2006/07/07 12:40:18  etaurel
// - Commit after implementing the group multi motor read
//
// Revision 1.1  2006/03/29 07:09:58  etaurel
// - Added motor group features
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
//  Command's name|  Method's name
//	----------------------------------------
//  State         |  dev_state()
//  Status        |  dev_status()
//  Abort         |  abort()
//  AddElement    |  add_element()
//  RemoveElement |  remove_element()
//
//===================================================================

#include <CtrlFiCa.h>
#include <tango.h>
#include <MotorGroup.h>
#include <MotorGroupClass.h>
#include <MotorGroupUtil.h>
#include <Pool.h>
#include <PoolThread.h>
#include <Motor.h>
#include <PseudoMotor.h>

#include <pool/Ctrl.h>
#include <pool/MotCtrl.h>
#include <pool/PseudoMotCtrl.h>

namespace MotorGroup_ns
{

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::MotorGroup(string &s)
// 
// description : 	constructor for simulated MotorGroup
//
// in : - cl : Pointer to the DeviceClass object
//      - s : Device name 
//
//-----------------------------------------------------------------------------
MotorGroup::MotorGroup(Tango::DeviceClass *cl,string &s)
//:Tango::Device_3Impl(cl,s.c_str())
:Pool_ns::PoolGroupBaseDev(cl,s.c_str())
{
	init_device();
}

MotorGroup::MotorGroup(Tango::DeviceClass *cl,const char *s)
//:Tango::Device_3Impl(cl,s)
:Pool_ns::PoolGroupBaseDev(cl,s)
{
	init_device();
}

MotorGroup::MotorGroup(Tango::DeviceClass *cl,const char *s,const char *d)
//:Tango::Device_3Impl(cl,s,d)
:Pool_ns::PoolGroupBaseDev(cl,s,d)
{
	init_device();
}
//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::delete_device()
// 
// description : 	will be called at device destruction or at init command.
//
//-----------------------------------------------------------------------------
void MotorGroup::delete_device()
{
	//	Delete device's allocated object

	DEBUG_STREAM << "Entering delete_device for dev " << get_name() << endl;
	
//
// A trick to inform client(s) listening on events that the pool device is down.
// Without this trick, the clients will have to wait for 3 seconds before being informed 
// This is the Tango device time-out.
// To know that we are executing this code due to a pool shutdown and not due to a
// "Init" command, we are using the polling thread ptr which is cleared in the DS
// shutdown sequence before the device destruction
//

	Tango::Util *tg = Tango::Util::instance();
	if (tg->get_polling_thread_object() == NULL)
	{
		struct timespec req_sleep;
		req_sleep.tv_sec = 0;
		req_sleep.tv_nsec = 500000000;
		
		pool_dev->set_moving_state();
		
		while(get_state() == Tango::MOVING)
		{
			nanosleep(&req_sleep,NULL);
		}
	}
	else
	{
		if (get_state() == Tango::MOVING)
		{
			TangoSys_OMemStream o;
			o << "Init command on group device is not allowed while a group is moving" << ends;

			Tango::Except::throw_exception((const char *)"Group_InitNotAllowed",o.str(),
				  	(const char *)"Group::delete_device");
		}
	}		
	
	base_delete_device();
		
	SAFE_DELETE_ARRAY(attr_Position_read);
	SAFE_DELETE_ARRAY(phys_mot_pos);

	SAFE_DELETE_ARRAY(attr_Elements_read);
	SAFE_DELETE_ARRAY(attr_Motors_read);
	SAFE_DELETE_ARRAY(attr_MotorGroups_read);
	SAFE_DELETE_ARRAY(attr_PseudoMotors_read);
	
	delete_from_pool();
	delete_utils();
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::init_device()
// 
// description : 	will be called at device initialization.
//
//-----------------------------------------------------------------------------
void MotorGroup::init_device()
{
	DEBUG_STREAM << "MotorGroup::MotorGroup() create device " << device_name << endl;

	// Initialise variables to default values
	//--------------------------------------------
	get_device_property();
	
	set_state(Tango::ON);
	string &_status = get_status();
	_status = StatusNotSet;
		
//
// If we are called due to a init command, re-init variables in the
// base class
//

	if (init_cmd)
	{
		base_init();
	}
	else
	{
        // if first time make sure that the pointers are properly clean 
		attr_Position_read = NULL;
		phys_mot_pos = NULL;
		attr_Elements_read = NULL;
		attr_Motors_read = NULL;
		attr_MotorGroups_read = NULL;
		attr_PseudoMotors_read = NULL;
	}
	
	if(!is_ghost())
	{
		ind_elt_nb = phys_group_elt.size();
		usr_elt_nb = user_group_elt.size();
	}
	else
	{
		alias = "The_ghost";
		
//
// Init motor list for the ghost group
//

		list<Pool_ns::MotorPool> &m_list = pool_dev->get_mot_list();
		ind_elt_nb = usr_elt_nb = m_list.size();

		state_array.clear();
		state_array.insert(state_array.begin(), usr_elt_nb, Tango::UNKNOWN);
	}
		
	pos_mon = new Tango::TangoMonitor("GroupPoolThread");

//
// We will push change event on State attribute
//

	Tango::Attribute &state_att = dev_attr->get_attr_by_name("state");
	state_att.set_change_event(true,false);
	
	Tango::Attribute &pos_att = dev_attr->get_attr_by_name("Position");
	pos_att.set_change_event(true);
	
	Tango::Attribute &elements_att = dev_attr->get_attr_by_name("Elements");
	elements_att.set_change_event(true,false);	

	Tango::Attribute &motors_att = dev_attr->get_attr_by_name("Motors");
	motors_att.set_change_event(true,false);	

	Tango::Attribute &motorgroups_att = dev_attr->get_attr_by_name("MotorGroups");
	motorgroups_att.set_change_event(true,false);	

	Tango::Attribute &pseudomotors_att = dev_attr->get_attr_by_name("PseudoMotors");
	pseudomotors_att.set_change_event(true,false);	

//
// Build the PoolBaseUtils class depending on the
// controller type
//

	set_utils(new MotorGroupUtil(pool_dev));	
	
	Pool_ns::MotorGroupPool mgp;
	init_pool_element(&mgp);

//
// Build group physical structure
//

	build_grp();
	mgp.mot_ids.clear();
	for (long i = 0;i < ind_elt_nb; i++)
		mgp.mot_ids.push_back(ind_elts[i]->id);
	
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
// Insert motor group into pool except for ghost group
//

	if (!is_ghost())
	{
		Tango::AutoTangoMonitor atm(pool_dev);
		pool_dev->add_motor_group(mgp);
	}

	if(!init_cmd)
	{
		read_Elements(elements_att);
		elements_att.fire_change_event();	

		read_Motors(motors_att);
		motors_att.fire_change_event();	

		read_MotorGroups(motorgroups_att);
		motorgroups_att.fire_change_event();	

		read_PseudoMotors(pseudomotors_att);
		pseudomotors_att.fire_change_event();	
	}
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::init_pool_element
// 
// description : 	Initialize all the data members of a PoolElement
//					structure. This method is used when a new device
//					is added to the Pool
//
// arg(s) : In : - pe : Pointer to the PoolElement structure which will
//						be initialized
//
//-----------------------------------------------------------------------------

void MotorGroup::init_pool_element(Pool_ns::PoolElement *pe)
{
	PoolGroupBaseDev::init_pool_element(pe);
	
	if(is_ghost())
		return;
	
	Pool_ns::MotorGroupPool *mgp = static_cast<Pool_ns::MotorGroupPool *>(pe);
	
	mgp->group_elts.clear();
	mgp->mot_elts.clear();
	mgp->pm_elts.clear();
	mgp->mg_elts.clear();
	
	vector<string>::iterator ite;
	for(ite = motor_list.begin(); ite != motor_list.end(); ite++)
		mgp->mot_elts.push_back(&pool_dev->get_motor_from_name(*ite));

	for(ite = motor_group_list.begin(); ite != motor_group_list.end(); ite++)
		mgp->mg_elts.push_back(&pool_dev->get_motor_group_from_name(*ite));

	for(ite = pseudo_motor_list.begin(); ite != pseudo_motor_list.end(); ite++)
		mgp->pm_elts.push_back(&pool_dev->get_pseudo_motor_from_name(*ite));
	
	for (long loop = 0;loop < usr_elt_nb;loop++)
	{
		Pool_ns::PoolElement &elem = pool_dev->get_pool_element_from_name(user_group_elt[loop]);
		
		mgp->group_elts.push_back(&elem);
		
		mgp->user_full_name += user_group_elt[loop];
		if (loop != usr_elt_nb - 1)
			mgp->user_full_name += ", ";
	}
	
	mgp->user_full_name += " (";
	for (long loop = 0;loop < ind_elt_nb;loop++)
	{
		mgp->user_full_name += phys_group_elt[loop];
		if (loop != ind_elt_nb - 1)
			mgp->user_full_name += ", ";
	}
	mgp->user_full_name += ")";
		
	mgp->group = this;
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::get_device_property()
// 
// description : 	Read the device properties from database.
//
//-----------------------------------------------------------------------------
void MotorGroup::get_device_property()
{
	//	Initialize your default values here (if not done with  POGO).
	//------------------------------------------------------------------

	//	Read device properties from database.(Automatic code generation)
	//------------------------------------------------------------------
	Tango::DbData	dev_prop;
	dev_prop.push_back(Tango::DbDatum("Motor_group_id"));
	dev_prop.push_back(Tango::DbDatum("Pool_device"));
	dev_prop.push_back(Tango::DbDatum("Motor_list"));
	dev_prop.push_back(Tango::DbDatum("Motor_group_list"));
	dev_prop.push_back(Tango::DbDatum("Pseudo_motor_list"));
	dev_prop.push_back(Tango::DbDatum("Sleep_bef_last_read"));
	dev_prop.push_back(Tango::DbDatum("User_group_elt"));
	dev_prop.push_back(Tango::DbDatum("Phys_group_elt"));
	dev_prop.push_back(Tango::DbDatum("Pos_spectrum_dim_x"));

	//	Call database and extract values
	//--------------------------------------------
	if (Tango::Util::instance()->_UseDb==true)
		get_db_device()->get_property(dev_prop);
	Tango::DbDatum	def_prop, cl_prop;
	MotorGroupClass	*ds_class =
		(static_cast<MotorGroupClass *>(get_device_class()));
	int	i = -1;

	//	Try to initialize Motor_group_id from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  motor_group_id;
	//	Try to initialize Motor_group_id from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  motor_group_id;
	//	And try to extract Motor_group_id value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_group_id;

	//	Try to initialize Pool_device from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  pool_device;
	//	Try to initialize Pool_device from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  pool_device;
	//	And try to extract Pool_device value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pool_device;

	//	Try to initialize Motor_list from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  motor_list;
	//	Try to initialize Motor_list from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  motor_list;
	//	And try to extract Motor_list value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_list;

	//	Try to initialize Motor_group_list from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  motor_group_list;
	//	Try to initialize Motor_group_list from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  motor_group_list;
	//	And try to extract Motor_group_list value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  motor_group_list;

	//	Try to initialize Pseudo_motor_list from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  pseudo_motor_list;
	//	Try to initialize Pseudo_motor_list from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  pseudo_motor_list;
	//	And try to extract Pseudo_motor_list value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pseudo_motor_list;
	
	//	Try to initialize Sleep_bef_last_read from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  sleep_bef_last_read;
	//	Try to initialize Sleep_bef_last_read from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  sleep_bef_last_read;
	//	And try to extract Sleep_bef_last_read value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  sleep_bef_last_read;

	//	Try to initialize User_group_elt from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  user_group_elt;
	//	Try to initialize User_group_elt from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  user_group_elt;
	//	And try to extract User_group_elt value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  user_group_elt;

	//	Try to initialize Phys_group_elt from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  phys_group_elt;
	//	Try to initialize Phys_group_elt from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  phys_group_elt;
	//	And try to extract Phys_group_elt value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  phys_group_elt;
	
	//	Try to initialize Pos_spectrum_dim_x from class property
	cl_prop = ds_class->get_class_property(dev_prop[++i].name);
	if (cl_prop.is_empty()==false)	cl_prop  >>  pos_spectrum_dim_x;
	//	Try to initialize Pos_spectrum_dim_x from default device value
	def_prop = ds_class->get_default_device_property(dev_prop[i].name);
	if (def_prop.is_empty()==false)	def_prop  >>  pos_spectrum_dim_x;
	//	And try to extract Pos_spectrum_dim_x value from database
	if (dev_prop[i].is_empty()==false)	dev_prop[i]  >>  pos_spectrum_dim_x;



	//	End of Automatic code generation
	//------------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::always_executed_hook()
// 
// description : 	method always executed before any command is executed
//
//-----------------------------------------------------------------------------
void MotorGroup::always_executed_hook()
{
	Pool_ns::PoolGroupBaseDev::always_executed_hook();

	//
// Check that the controllers implied in this group are correctly built
//

	vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
	Controller *ctrl;
	for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
	{
		Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
		ctrl = cp->ctrl;
		if ((cp->ctrl_fica_built == false) || (ctrl == NULL))
		{
			set_state(Tango::FAULT);
			break;
		}
	}
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_attr_hardware
// 
// description : 	Hardware acquisition for attributes.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_attr_hardware(vector<long> &attr_list)
{
	DEBUG_STREAM << "MotorGroup::read_attr_hardware(vector<long> &attr_list) entering... "<< endl;
	//	Add your own code here
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Elements
// 
// description : 	Extract real attribute values for Elements acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Elements(Tango::Attribute &attr)
{
	vector<string>::iterator ite;
	long l = 0;
	for (ite = user_group_elt.begin();ite != user_group_elt.end();++ite,++l)
	{
		attr_Elements_read[l] = const_cast<char *>(ite->c_str());
	}

	attr.set_value(attr_Elements_read, user_group_elt.size());	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Motors
// 
// description : 	Extract real attribute values for Motors acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Motors(Tango::Attribute &attr)
{
	vector<string>::iterator ite;
	long l = 0;
	for (ite = motor_list.begin();ite != motor_list.end();++ite)
	{
		attr_Motors_read[l++] = const_cast<char *>(ite->c_str());
	}

	attr.set_value(attr_Motors_read, motor_list.size());	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_MotorGroups
// 
// description : 	Extract real attribute values for MotorGroupss acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_MotorGroups(Tango::Attribute &attr)
{
	vector<string>::iterator ite;
	long l = 0;
	for (ite = motor_group_list.begin();ite != motor_group_list.end();++ite)
	{
		attr_MotorGroups_read[l++] = const_cast<char *>(ite->c_str());
	}

	attr.set_value(attr_MotorGroups_read, motor_group_list.size());	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_PseudoMotors
// 
// description : 	Extract real attribute values for PseudoMotors acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_PseudoMotors(Tango::Attribute &attr)
{
	vector<string>::iterator ite;
	long l = 0;
	for (ite = pseudo_motor_list.begin();ite != pseudo_motor_list.end();++ite)
	{
		attr_PseudoMotors_read[l++] = const_cast<char *>(ite->c_str());
	}

	attr.set_value(attr_PseudoMotors_read, pseudo_motor_list.size());
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::read_Position
// 
// description : 	Extract real attribute values for Position acquisition result.
//
//-----------------------------------------------------------------------------
void MotorGroup::read_Position(Tango::Attribute &attr)
{
	DEBUG_STREAM << "MotorGroup::read_Position(Tango::Attribute &attr) entering... "<< endl;

	bool ctrl_locked = false;
	bool mot_locked = false;

//
// If we have some pseudo-motor in this group,
// check that they are correctly built
//

	if (nb_psm_in_grp != 0)
	{
		for (unsigned long loop = 0;loop < nb_psm_in_grp;loop++)
		{
			if (!psm_in_grp[loop].pool_psm.pseudo_motor->is_fica_built())
			{
				TangoSys_OMemStream o;
				o << "Impossible to read position of group " << get_name();
				o << "\nThe pseudo-motor " << psm_in_grp[loop].pool_psm.name;
				o << " is invalid" << ends;
				Tango::Except::throw_exception(
						(const char *)"MotorGroup_InvalidPseudoMotor",
						o.str(),
						(const char *)"MotorGroup::read_Position");
			}
		}
	}
	
//
// Lock all the motors implied in this group
//

	long loop = -1;
	
	mot_locked = true;
	for (loop = 0;loop < ind_elt_nb;loop++)
		ind_elts[loop]->Lock();

	DEBUG_STREAM << "All motors locked" << endl;
			
//
// Lock all the controllers implied in this group
//

	ctrl_locked = true;
	vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
	for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
	{
		Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
		(*impl_ctrl_ite)->lock_ptr = new Pool_ns::AutoPoolLock(cp->get_ctrl_fica_mon());
	}
	DEBUG_STREAM << "ALl ctrl locked" << endl;
	
	string except_func("PreReadAll");
	try
	{
					
//
// Send PreReadAll to all controller(s)
//
			
		for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
		{
			Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
			MotorController *mc = static_cast<MotorController *>(cp->ctrl);
			try
			{
				mc->PreReadAll();		
			}
			SAFE_CATCH(cp->get_fica_name(),"PreReadAll()");	
		}
		DEBUG_STREAM << "PreReadAll sent to ctrl(s)" << endl;
				
//
// Send PreReadOne to each implied motor
//
				
		except_func = "PreReadOne";
		for (loop = 0;loop < ind_elt_nb;loop++)
		{
			IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
			Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;					
			MotorController *mc = static_cast<MotorController *>(cp->ctrl);
			try
			{
				mc->PreReadOne(ind_mov->idx_in_ctrl);
			}
			SAFE_CATCH(cp->get_fica_name(),"PreReadOne()");
		}
		loop = -1;
		DEBUG_STREAM << "All PreReadOne sent" << endl;
			
//
// Send the ReadAll to all implied controller
//

		except_func = "ReadAll";	
		for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
		{
			Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
			MotorController *mc = static_cast<MotorController *>(cp->ctrl);
			try
			{
				mc->ReadAll();	
			}
			SAFE_CATCH(cp->get_fica_name(),"ReadAll()");	
		}
		DEBUG_STREAM << "All ReadAll sent" << endl;
		
//
// Get each motor position
// The position returned by the controller is the dial position.
// We need to add motor offset
//

		except_func = "ReadOne";
		for (loop = 0;loop < ind_elt_nb;loop++)
		{
			IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
			Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;
			Motor_ns::Motor *m = ind_mov->get_motor()->motor;	
							
			MotorController *mc = static_cast<MotorController *>(cp->ctrl);
			double mot_dial_pos;
			try
			{
				mot_dial_pos = mc->ReadOne(ind_mov->idx_in_ctrl);
			}
			SAFE_CATCH(cp->get_fica_name(),"ReadOne()");
			
			if (isnan(mot_dial_pos) != 0)
			{
				Tango::Except::throw_exception((const char *)"Motor_BadController",
						  (const char *)"The motor controller class has not re-defined method to read position (readOne(...))",
						  (const char *)"MotorGroup::read_Position");
			}
			double mot_offset = m->get_offset();
			double mot_pos = mot_dial_pos + mot_offset;
			DEBUG_STREAM << "Position for motor " << ind_mov->id << " is " << mot_pos << endl;
			phys_mot_pos[ind_mov->idx_in_grp] = mot_pos;
		}
		loop = -1;
		
//
// Unlock all the controllers and all motor implied in this move
//

		for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
		{
			if ((*impl_ctrl_ite)->lock_ptr != NULL)
			{
				delete (*impl_ctrl_ite)->lock_ptr;
				(*impl_ctrl_ite)->lock_ptr = NULL;
			}
		}
		ctrl_locked = false;
		DEBUG_STREAM << "All ctrl unlocked" << endl;

		for (loop = 0;loop < ind_elt_nb;loop++)
		{
			ind_elts[loop]->Unlock();
		}
		mot_locked = false;
		DEBUG_STREAM << "All motors unlocked" << endl;
				
//
// Set attribute values
//

		from_phys_2_grp();	
		attr.set_value(attr_Position_read,pos_spectrum_dim_x);
		
	}
	catch (Tango::DevFailed &e)
	{
		
//
// Unlock everything if needed
//

		if (ctrl_locked == true)
		{
			for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
			{
				if ((*impl_ctrl_ite)->lock_ptr != NULL)
				{
					delete (*impl_ctrl_ite)->lock_ptr;
					(*impl_ctrl_ite)->lock_ptr = NULL;
				}
			}
		}

		if (mot_locked == true)
		{
			for (long ctr = 0;ctr < ind_elt_nb;ctr++)
			{
				ind_elts[ctr]->Unlock();
			}
		}
		
		TangoSys_OMemStream o;
		o << "Impossible to read position of group " << get_name();
		if (loop != -1)
		{
			o << "\nImpossible to read motor position for device " << ind_elts[loop]->get_alias() << " (";
			o << ind_elts[loop]->pe->obj_tango_name << ")";
		}
		else
		{
			o << "\nController " ;
		}
		o << ". The " << except_func << "() controller method throws an exception" << ends;		
		Tango::Except::re_throw_exception(e,(const char *)"Motor_ControllerFailed",
									o.str(),(const char *)"MotorGroup::read_Position");
	}

	Tango::DevState mot_sta = get_state();
	
	if (mot_sta == Tango::MOVING)
		attr.set_quality(Tango::ATTR_CHANGING);
	else if (mot_sta == Tango::ALARM)
	  	attr.set_quality(Tango::ATTR_ALARM);
	  	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::write_Position
// 
// description : 	Write Position attribute values to hardware.
//
//-----------------------------------------------------------------------------
void MotorGroup::write_Position(Tango::WAttribute &attr)
{
	DEBUG_STREAM << "MotorGroup::write_Position(Tango::WAttribute &attr) entering... "<< endl;
	
//
// Check that we receive new position for all motors
//

	long nb_received_pos = attr.get_write_value_length();
	if (nb_received_pos != pos_spectrum_dim_x)
	{
		TangoSys_OMemStream o;
		o << "This group is defined with " << pos_spectrum_dim_x << " motor(s) and you sent new position for ";
		o << nb_received_pos << " motor(s)" << ends;

		Tango::Except::throw_exception((const char *)"Motor_CantMoveGroup",o.str(),
				  (const char *)"MotorGroup::write_Position");
	}
	
//
// If we have some pseudo-motor in this group,
// check that they are correctly built
//

	if (nb_psm_in_grp != 0)
	{
		for (unsigned long loop = 0;loop < nb_psm_in_grp;loop++)
		{
			if (!psm_in_grp[loop].pool_psm.pseudo_motor->is_fica_built())
			{
				TangoSys_OMemStream o;
				o << "Impossible to write position of group " << get_name();
				o << "\nThe pseudo-motor " << psm_in_grp[loop].pool_psm.name;
				o << " is invalid" << ends;
				Tango::Except::throw_exception(
						(const char *)"MotorGroup_InvalidPseudoMotor",
						o.str(),
						(const char *)"MotorGroup::write_Position");
			}
		}
	}

//
// Get written data
//
	
	const Tango::DevDouble *received_data;
	attr.get_write_value(received_data);
	
//
// Compute physical position
//

	from_grp_2_phys(received_data);	
	
//
// Init vector to pass data to the movement thread
//

	vector<double> pos_vector;
	vector<long> mot_id_vector;
	unsigned long loop;
	
	for (loop = 0;loop < ind_elts.size();loop++)
	{
		IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
		mot_id_vector.push_back(ind_mov->id);
		pos_vector.push_back(phys_mot_pos[ind_mov->idx_in_grp]);
	}
	
//
// Start a movement thread
//
	
	th_failed = false;
	abort_cmd_executed = false;		
	Pool_ns::PoolThread *pool_th = new Pool_ns::PoolThread(mot_id_vector,pos_vector,pool_dev,pos_mon,motor_group_id);

//
// Start it only while the pos_mon
// lock is taken. Otherwise, a dead-lock can happen, if the thread
// starts excuting its code just after the start() and before this code
// enters into the wait(). The movment thread will send the signal() but while
// this thread is not yet waiting for it and afterwards, we will have
// a dead-lock...
//
		
	{
		omni_mutex_lock lo(*pos_mon);
		pool_th->start();
		pos_mon->wait();
	}
		
	if (th_failed == true)
	{		
		Tango::DevFailed ex(th_except);
		throw ex;
	}

}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort movement of all motors moving when the command is executed
 *
 *
 */
//+------------------------------------------------------------------
void MotorGroup::abort()
{
	DEBUG_STREAM << "MotorGroup::abort(): entering... !" << endl;

	//	Add your own code to control device here
	base_abort(true);
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::abort
 *
 *	description:	method to execute "Abort"
 *	Abort movement of all motors moving when the command is executed
 *
 *
 */
//+------------------------------------------------------------------
void MotorGroup::base_abort(bool send_evt)
{
//
// Send abort to all motors member of the group
//

	vector<Tango::DevFailed> v_except;
	unsigned long loop;
	abort_cmd_executed = true;	
	for (loop = 0;loop < ind_elts.size();loop++)
	{
		try
		{
			ind_elts[loop]->obj_proxy->command_inout("Abort");
		}
		catch (Tango::DevFailed &e)
		{
			v_except.push_back(e);
		}
	}
	
//
// Report exception to caller in case of
//

	if (v_except.size() != 0)
	{
		if (v_except.size() == 1)
		{
			Tango::Except::re_throw_exception(v_except[0],(const char *)"Motor_ExcepAbort",
											(const char *)"One motor throws exception during Abort command",
											(const char *)"MotorGroup::Abort");
		}
		else
		{
		}
	}
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::add_element
 *
 *	description:	method to execute "AddElement"
 *	Append a new experiment channel to the current list of channels in the measurement group.
 *
 * @param	argin	Experiment Channel name
 *
 */
//+------------------------------------------------------------------
void MotorGroup::add_element(Tango::DevString argin)
{
	DEBUG_STREAM << "MotorGroup::add_element(): entering... !" << endl;

	//	Add your own code to control device here
	
	Tango::AutoTangoMonitor atm(pool_dev);
	
	Pool_ns::MotorGroupPool &mgp = pool_dev->get_motor_group_from_id(motor_group_id);
	
//
// Check that this group is not used by any pseudo motor
//
	vector<string> used_by_pm;
	if (pool_dev->get_pseudo_motors_that_use_mg(mgp.id,used_by_pm) == true)
	{
		TangoSys_OMemStream o;
		o << "Can't add group elements. ";
		o << "This motor group is used by pseudo motor(s): ";

		vector<string>::iterator ite = used_by_pm.begin();
		for(;ite != used_by_pm.end(); ite++)
			o << "'" << *ite << "', ";
		o << ends;

		Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
							 (const char *)"MotorGroup::add_element");
	}
	
	string elt_name(argin);
	
//
// Check that the element to be added is not already part of any motor group 
// (including itself) in the hierarchy of motor groups to which this motor group 
// belongs
//
	vector<string> used_by_mg;
	if(pool_dev->get_motor_groups_in_hierarchy_containing_elt(mgp,elt_name,used_by_mg) == true)
	{
		TangoSys_OMemStream o;
		o << "Can't add '" << elt_name << "'. ";
		
		if(mgp.name == used_by_mg[0])
		{
			o << "This motor group already contains (directly or indirectly) '" << elt_name << "'.";
		}
		else
		{
			o << "This motor group is member of motor group(s) (";
			vector<string>::iterator ite = used_by_mg.begin();
			for(;ite != used_by_mg.end(); ite++)
				o << "'" << *ite << "', ";
			o << ") that already contain (directly or indirectly) '" << elt_name << "'." << ends;
		}
		
		Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
							 (const char *)"MotorGroup::add_element");
	}
	
//
// Check if the element exists in the pool
//
	Pool_ns::GrpEltType type;
	Pool_ns::PoolElement *elt = NULL;
	
	bool elt_exists = true;
	
	try
	{
		elt = &pool_dev->get_motor_from_name(elt_name);
		type = Pool_ns::MOTOR;
	}
	catch(Tango::DevFailed &e)
	{
		try
		{
			elt = &pool_dev->get_motor_group_from_name(elt_name);
			type = Pool_ns::GROUP;
		}
		catch(Tango::DevFailed &e)
		{
			try
			{
				elt = &pool_dev->get_pseudo_motor_from_name(elt_name);
				type = Pool_ns::PSEUDO_MOTOR;
			}
			catch(Tango::DevFailed &e)
			{
				elt_exists = false;			
			}
		}
	}
	
	if(elt_exists == false)
	{
		TangoSys_OMemStream o;
		o << "No valid element (motor, pseudo motor or motor group) with name " << elt_name << " found in the Pool." << ends;
	
		Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
					  				   (const char *)"MotorGroup::add_element");	
	}

//
// If it is a motor group or a pseudo motor check that none of its ind elements
// already belongs to this motor group
// Also update the object members which are device properties values
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//
	if(type == Pool_ns::GROUP)
	{
		Pool_ns::MotorGroupPool *grp = (Pool_ns::MotorGroupPool*)elt;
		
		IndMov *ind_elt = NULL;
		vector<long>::iterator ite = grp->mot_ids.begin();
		for(;ite != grp->mot_ids.end(); ite++)
		{
			try
			{
				ind_elt = &get_ind_mov_from_id(*ite);
				break;
			}
			catch(Tango::DevFailed &e) {}
		}
		
		if(ind_elt != NULL)
		{
			TangoSys_OMemStream o;
			o << "The motor group to be added contains an element (" << ind_elt->get_alias() << ") which is already part of the motor group" << ends;
		
			Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
						  				   (const char *)"MotorGroup::add_element");	
		}
		
		user_group_elt.push_back(grp->name);
		motor_group_list.push_back(grp->name);
		phys_group_elt.insert(phys_group_elt.end(),grp->group->phys_group_elt.begin(), grp->group->phys_group_elt.end());
		pos_spectrum_dim_x += grp->group->pos_spectrum_dim_x;	
	}
	else if(type == Pool_ns::PSEUDO_MOTOR)
	{
		Pool_ns::PseudoMotorPool *pm = (Pool_ns::PseudoMotorPool*)elt;
		
		vector<PsmCtrlInGrp>::iterator pm_ctrl_ite = psm_ctrls_in_grp.begin();
		for(;pm_ctrl_ite != psm_ctrls_in_grp.end(); pm_ctrl_ite++)
		{
			if(pm_ctrl_ite->pool_psm_ctrl == pm->pseudo_motor->get_ctrl())
				break;	
		}

//
// If there isn't already a pseudo motor with the same controller in the group
// we have to check that none of the motors involved in the pseudo motor are 
// already in the motor group.
//
		if(pm_ctrl_ite == psm_ctrls_in_grp.end())
		{
			IndMov *ind_elt = NULL;
			vector<Pool_ns::PoolElement*>::iterator ite = pm->mot_elts.begin();
			for(;ite != pm->mot_elts.end(); ite++)
			{
				try
				{
					ind_elt = &get_ind_mov_from_name((*ite)->name);
					break;
				}
				catch(Tango::DevFailed &e) {}
			}
			
			if(ind_elt != NULL)
			{
				TangoSys_OMemStream o;
				o << "The pseudo motor to be added contains an element (" << ind_elt->get_alias() << ") which is already part of the motor group" << ends;
			
				Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
							  				   (const char *)"MotorGroup::add_element");	
			}
			
			vector<Pool_ns::PoolElement*>::iterator pm_m_ite = pm->mot_elts.begin();
			for(;pm_m_ite != pm->mot_elts.end(); pm_m_ite++)
			{
				string mot_lower((*pm_m_ite)->name);
				transform(mot_lower.begin(),mot_lower.end(),mot_lower.begin(),::tolower);
				phys_group_elt.push_back(mot_lower);
			}
		}

		user_group_elt.push_back(pm->name);
		pseudo_motor_list.push_back(pm->name);
		pos_spectrum_dim_x++;
	}
	else if(type == Pool_ns::MOTOR)
	{
		Pool_ns::MotorPool *m = (Pool_ns::MotorPool*)elt;
		user_group_elt.push_back(m->name);
		phys_group_elt.push_back(m->name);
		motor_list.push_back(m->name);
		pos_spectrum_dim_x++;
	}

//
// Register for internal events on the new element
//
	elt->add_pool_elem_listener(&mgp);

	update_elements();

//
// Fire events on proper attributes	
//
	if(type == Pool_ns::GROUP)
	{
		Tango::Attribute &mgs = dev_attr->get_attr_by_name("MotorGroups");
	  	read_MotorGroups(mgs);
	  	mgs.fire_change_event();
	}
	else if(type == Pool_ns::PSEUDO_MOTOR)
	{
		Tango::Attribute &pms = dev_attr->get_attr_by_name("PseudoMotors");
	  	read_PseudoMotors(pms);
	  	pms.fire_change_event();
	}
	else if(type == Pool_ns::MOTOR)
	{
		Tango::Attribute &mots = dev_attr->get_attr_by_name("Motors");
	  	read_Motors(mots);
	  	mots.fire_change_event();
	}			

	Tango::Attribute &elts = dev_attr->get_attr_by_name("Elements");
  	read_Elements(elts);
  	elts.fire_change_event();

//
// Fire internal events to listeners
//
	Pool_ns::PoolElementEvent evt(Pool_ns::ElementListChange, &mgp);
	mgp.fire_pool_elem_change(&evt);

//
// Inform the pool so it can send a change event on the motor group list
//
	pool_dev->motor_group_elts_changed(motor_group_id);	
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::remove_element
 *
 *	description:	method to execute "RemoveElement"
 *	Removes the experiment channel from the list of experiment channels in the measurement group
 *
 * @param	argin	Experiment channel name
 *
 */
//+------------------------------------------------------------------
void MotorGroup::remove_element(Tango::DevString argin)
{
	DEBUG_STREAM << "MotorGroup::remove_element(): entering... !" << endl;

	//	Add your own code to control device here
	Tango::AutoTangoMonitor atm(pool_dev);

	Pool_ns::MotorGroupPool &mgp = pool_dev->get_motor_group_from_id(motor_group_id);
	
//
// Check that this group is not used by any pseudo motor
//
	vector<string> used_by_pm;
	if (pool_dev->get_pseudo_motors_that_use_mg(mgp.id,used_by_pm))
	{
		TangoSys_OMemStream o;
		o << "Can't delete group with name " << argin;
		o << ". It is used by pseudo motor(s): ";

		vector<string>::iterator ite = used_by_pm.begin();
		for(;ite != used_by_pm.end(); ite++)
			o << *ite << ", " << ends;
		o << ends;

		Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
							 (const char *)"MotorGroup::add_element");
	}

	string elt_name(argin);
	
//
// Check that the element is in the group
//
	
	if(mgp.is_user_member(elt_name) == false)
	{
		TangoSys_OMemStream o;
		o << "The element " << elt_name << " is not part of the motor group" << ends;
	
		Tango::Except::throw_exception((const char *)"MotorGroup_BadArgument",o.str(),
					  				   (const char *)"MotorGroup::remove_element");	
	}
	
//
// Check which type of element it is
//
	Pool_ns::GrpEltType type;
	Pool_ns::PoolElement *elt = NULL;
	
	try
	{
		elt = &pool_dev->get_motor_from_name(elt_name);
		type = Pool_ns::MOTOR;
	}
	catch(Tango::DevFailed &e)
	{
		try
		{
			elt = &pool_dev->get_motor_group_from_name(elt_name);
			type = Pool_ns::GROUP;
		}
		catch(Tango::DevFailed &e)
		{
			try
			{
				elt = &pool_dev->get_pseudo_motor_from_name(elt_name);
				type = Pool_ns::PSEUDO_MOTOR;
			}
			catch(Tango::DevFailed &e)
			{
				TangoSys_OMemStream o;
				o << "Unexpected error. " << elt_name << " exists in the motor group but not in the pool." << ends;
			
				Tango::Except::throw_exception((const char *)"MotorGroup_Unexpected",o.str(),
							  				   (const char *)"MotorGroup::remove_element");	
			}
		}
	}
	
//
// Update the object members which are device properties values
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//
	if(type == Pool_ns::GROUP)
	{
		Pool_ns::MotorGroupPool *grp = (Pool_ns::MotorGroupPool*)elt;
		
		// Remove the group
		vector<string>::iterator v_ite = find_in_user_group_lst(grp->name);
		if (v_ite != user_group_elt.end())
			user_group_elt.erase(v_ite);
			
		v_ite = find_in_motor_group_lst(grp->name);
		if (v_ite != motor_group_list.end())
			motor_group_list.erase(v_ite);
		
		// Remove the motors that are in the group
		for(v_ite = grp->group->phys_group_elt.begin(); v_ite != grp->group->phys_group_elt.end(); v_ite++)
		{
			vector<string>::iterator elt_ite = find_in_phys_group_lst(*v_ite);
			if (elt_ite != phys_group_elt.end())
				phys_group_elt.erase(elt_ite);
		}
		
		pos_spectrum_dim_x -= grp->group->pos_spectrum_dim_x;	
		
	}
	else if(type == Pool_ns::PSEUDO_MOTOR)
	{
		Pool_ns::PseudoMotorPool *pm = (Pool_ns::PseudoMotorPool*)elt;
		
		// Remove the pseudo motor
		vector<string>::iterator v_ite = find_in_user_group_lst(pm->name);
		if (v_ite != user_group_elt.end())
			user_group_elt.erase(v_ite);
		
		v_ite = find_in_pseudo_motor_lst(pm->name);
		if (v_ite != pseudo_motor_list.end())
			pseudo_motor_list.erase(v_ite);
//
// If no other pseudo motor uses the motors of this pseudo motor (i.e. they have
// the same controller), then remove the motors
//
		vector<PsmInGrp>::iterator pm_ite = psm_in_grp.begin();
		for(;pm_ite != psm_in_grp.end(); pm_ite++)
		{
			if(pm_ite->psm_alias == pm->name)
				continue;
			
			if(pm_ite->pool_psm.pseudo_motor->get_ctrl() == pm->pseudo_motor->get_ctrl())
				break;	
		}
		
		if(pm_ite == psm_in_grp.end())
		{
			vector<Pool_ns::PoolElement*>::iterator pm_elt_ite = pm->mot_elts.begin();
			for(;pm_elt_ite != pm->mot_elts.end(); pm_elt_ite++)
			{
				vector<string>::iterator elt_ite = find_in_phys_group_lst((*pm_elt_ite)->name);
				if (elt_ite != phys_group_elt.end())
					phys_group_elt.erase(elt_ite);
			}
		}
		pos_spectrum_dim_x--;
	}
	else if(type == Pool_ns::MOTOR)
	{
		Pool_ns::MotorPool *m = (Pool_ns::MotorPool*)elt;
		
		// Remove the motor
		vector<string>::iterator v_ite = find_in_user_group_lst(m->name);
		if (v_ite != user_group_elt.end())
			user_group_elt.erase(v_ite);	

		v_ite = find_in_motor_lst(m->name);
		if (v_ite != motor_list.end())
			motor_list.erase(v_ite);
		
		v_ite = find_in_phys_group_lst(m->name);
		if (v_ite != phys_group_elt.end())
			phys_group_elt.erase(v_ite);
		
		pos_spectrum_dim_x--;
	}
	
//
// Register for internal events on the new element
//
	elt->remove_pool_elem_listener(&mgp);
	
	update_elements();
	
//
// Fire events on proper attributes	
//
	
	if(type == Pool_ns::GROUP)
	{
		Tango::Attribute &mgs = dev_attr->get_attr_by_name("MotorGroups");
	  	read_MotorGroups(mgs);
	  	mgs.fire_change_event();
	}
	else if(type == Pool_ns::PSEUDO_MOTOR)
	{
		Tango::Attribute &pms = dev_attr->get_attr_by_name("PseudoMotors");
	  	read_PseudoMotors(pms);
	  	pms.fire_change_event();
	}
	else if(type == Pool_ns::MOTOR)
	{
		Tango::Attribute &mots = dev_attr->get_attr_by_name("Motors");
	  	read_Motors(mots);
	  	mots.fire_change_event();
	}			

	Tango::Attribute &elts = dev_attr->get_attr_by_name("Elements");
  	read_Elements(elts);
  	elts.fire_change_event();

//
// Fire internal events to listeners
//
	Pool_ns::PoolElementEvent evt(Pool_ns::ElementListChange, &mgp);
	mgp.fire_pool_elem_change(&evt);

//	
// Inform the pool so it can send a change event on the motor group list
//
	pool_dev->motor_group_elts_changed(motor_group_id);	

}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::update_elements
 *
 *	description: updates the motor group elements based on the values
 * of motor_list, user_group_elt, pos_spectrum_dim_x.
 *
 */
//+------------------------------------------------------------------
void MotorGroup::update_elements()
{

//
// Update some counters
//
	ind_elt_nb = phys_group_elt.size();
	usr_elt_nb = user_group_elt.size();
		
//
// Write the new values for the device properties
// (motor_list, user_group_elt, pos_spectrum_dim_x)
//	
	Tango::DbData dev_prop;
	Tango::DbDatum 
	mot_lst("Motor_list"),
	mg_lst("Motor_group_list"),
	pm_lst("Pseudo_motor_list"), 
	usr_grp_lst("User_group_elt"),
	phy_grp_lst("Phys_group_elt"),
	pos_dim("Pos_spectrum_dim_x");
	mot_lst << motor_list;
	dev_prop.push_back(mot_lst);
	mg_lst << motor_group_list;
	dev_prop.push_back(mg_lst);
	pm_lst << pseudo_motor_list;
	dev_prop.push_back(pm_lst);
	usr_grp_lst << user_group_elt;
	dev_prop.push_back(usr_grp_lst);
	phy_grp_lst << phys_group_elt;
	dev_prop.push_back(phy_grp_lst);
	pos_dim << pos_spectrum_dim_x;
	dev_prop.push_back(pos_dim);
	get_db_device()->put_property(dev_prop);
	
//
// Clear the necessary structures
// 
	unsigned long l;
	
	for(l = 0;l < ind_elts.size();l++)
		delete ind_elts[l];
	ind_elts.clear();

	for(l = 0; l < implied_ctrls.size(); l++)
		delete implied_ctrls[l];
	implied_ctrls.clear();
	
	user_group_elt_type.clear();
	grp_in_grp.clear();
	psm_in_grp.clear();
	psm_ctrls_in_grp.clear();
	
	state_array.clear();
	
//
// update Pool data structure
//	
	Pool_ns::MotorGroupPool &mgp = 
		pool_dev->get_motor_group_from_id(motor_group_id);
		
	// init_pool_element erases the pointer to the Proxy. We store it before and recover it after
	Tango::DeviceProxy *proxy = mgp.obj_proxy;		
	init_pool_element(&mgp);
	mgp.obj_proxy = proxy; 
		
	build_grp();
	
//
// Update missing pool data structure (only possible after a build_grp() )
// 
	mgp.mot_ids.clear();
	for (long i = 0;i < ind_elt_nb; i++)
		mgp.mot_ids.push_back(ind_elts[i]->id);
	
	build_grp_struct();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::pool_elem_changed
 *
 *	description: This method is called when the src object has changed
 *               and an event is generated 
 *
 * arg(s) : - evt [in]: The event that has occured
 *          - forward_evt [out]: the new internal event data to be sent
 *                               to all listeners
 */
//+------------------------------------------------------------------

void MotorGroup::pool_elem_changed(Pool_ns::PoolElemEventList &evt_lst, 
								   Pool_ns::PoolElementEvent &forward_evt)
{
	Pool_ns::PoolElementEvent *evt = evt_lst.back();
	Pool_ns::PoolElement *src = evt->src;
	
	forward_evt.priority = evt->priority;
	
//
// State change from a motor
//

	switch(evt->type)
	{
		case Pool_ns::StateChange:
		{
			Tango::DevState old_state = get_state();
			
			// Warning: This method needs a lock on the Controller. Therefore, the element which
			// invoked the change should only do it after releasing its own lock.
			
			IndMov &m = get_ind_mov_from_name(evt_lst.front()->src->name);
			{
				Tango::AutoTangoMonitor lo(this);
				update_state_from_ctrls(m.idx_in_grp, evt_lst.front()->new_state);
			}
			
			Tango::DevState new_state = get_state();
			
			if(old_state != new_state)
			{
				Tango::AutoTangoMonitor lo(this);
				Tango::MultiAttribute *dev_attrs = get_device_attr();
				Tango::Attribute &state_att = dev_attrs->get_attr_by_name("State");
				state_att.fire_change_event();
			}
			
			forward_evt.type = Pool_ns::StateChange;
			forward_evt.old_state = old_state;
			forward_evt.new_state = new_state;
		}
		break;

//
// Position change event from a motor
//
		case Pool_ns::PositionChange:
		{
			//Find motor/pseudo motor that changed
			try
			{
				IndMov &m = get_ind_mov_from_name(src->name);
			
				// Confirm that the motor is directly seen by the user
				assert(m.idx_in_usr >=0);
				
				Tango::MultiAttribute *attr_list = get_device_attr();
				Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");
	
				Tango::DevState mg_state = get_state();
				
	
				// Make sure the event is sent to all clients 
				if(true == evt->priority)
					attr.set_change_event(true,false);
				
				{			
					// get the tango synchronization monitor
					Tango::AutoTangoMonitor synch(this);
					
					attr_Position_read[m.idx_in_usr] = evt->new_position;
									
					// set the attribute value
					attr.set_value (attr_Position_read,pos_spectrum_dim_x);
					
					if (mg_state == Tango::MOVING)
						attr.set_quality(Tango::ATTR_CHANGING);
					else if (mg_state == Tango::ALARM)
		  				attr.set_quality(Tango::ATTR_ALARM);
					
					// push the event
					attr.fire_change_event();
				}
				
				if(true == evt->priority)
					attr.set_change_event(true,true);
			}
			catch(Tango::DevFailed &e)
			{
				try
				{
					PsmInGrp &psm = get_psm_from_name(src->name);
					
					Tango::MultiAttribute *attr_list = get_device_attr();
					Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");
					
					Tango::DevState mg_state = get_state();
				
					// Make sure the event is sent to all clients 
					if(true == evt->priority)
						attr.set_change_event(true,false);
					
					{			
						// get the tango synchronization monitor
						Tango::AutoTangoMonitor synch(this);						
						
						attr_Position_read[psm.idx_in_usr] = evt->new_position;
						
						// set the attribute value
						attr.set_value (attr_Position_read,pos_spectrum_dim_x);

						if (mg_state == Tango::MOVING)
							attr.set_quality(Tango::ATTR_CHANGING);
						else if (mg_state == Tango::ALARM)
			  				attr.set_quality(Tango::ATTR_ALARM);

						// push the event
						attr.fire_change_event();
					}
					
					if(true == evt->priority)
						attr.set_change_event(true,true);
				}
				catch(Tango::DevFailed &e)
				{
					TangoSys_OMemStream o;
					o << "No element with name " << src->name << " found in Motor group element list" << ends;
			
					Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
								  				   (const char *)"MotorGroup::pool_elem_changed");	
				}	
			}
			
			forward_evt.type = Pool_ns::PositionArrayChange;
			forward_evt.dim = usr_elt_nb;
			forward_evt.old_position_array = NULL;
			forward_evt.new_position_array = attr_Position_read;
		}
		break;

//
// Position array change event from a motor group
//
		case Pool_ns::PositionArrayChange:
		{
			GrpInGrp &grp = get_grp_from_id(src->id);
			
			assert(evt->dim == grp.pos_len);
			
			Tango::MultiAttribute *attr_list = get_device_attr();
			Tango::Attribute &attr           = attr_list->get_attr_by_name ("Position");
			
			Tango::DevState mg_state = get_state();
					
			// Make sure the event is sent to all clients 
			if(true == evt->priority)
				attr.set_change_event(true,false);
			
			{			
				// get the tango synchronization monitor
				Tango::AutoTangoMonitor synch(this);
				
				memcpy(&(attr_Position_read[grp.idx_in_usr]),evt->new_position_array,sizeof(double)*evt->dim);
				
				// set the attribute value
				attr.set_value (attr_Position_read,pos_spectrum_dim_x);

				if (mg_state == Tango::MOVING)
					attr.set_quality(Tango::ATTR_CHANGING);
				else if (mg_state == Tango::ALARM)
					attr.set_quality(Tango::ATTR_ALARM);			
				
				// push the event
				attr.fire_change_event();
			}
			
			if(true == evt->priority)
				attr.set_change_event(true,true);
			
			
			forward_evt.type = Pool_ns::PositionArrayChange;
			forward_evt.dim = pos_spectrum_dim_x;
			forward_evt.old_position_array = NULL;
			forward_evt.new_position_array = attr_Position_read;
		}
		break;

//
// Nothing to do. Just propagate the event.
//		
		case Pool_ns::MotionEnded:
		{
			
		}
		break;

//
// One of the motor groups which are member of this motor group changed its list of 
// elements.
//
		case Pool_ns::ElementListChange:
		{
			GrpInGrp &grp = get_grp_from_id(src->id);
			long diff_pos_len = grp.pool_grp.group->pos_spectrum_dim_x - grp.pos_len;
			bool added = diff_pos_len > 0;
			pos_spectrum_dim_x += diff_pos_len;
			
			// Rebuild the physical group list
			// This will not work in case the group has no elements!
			/*
			vector<string>::iterator ite_start = find_in_phys_group_lst(grp.pool_grp->phy_group_elt[0]);
			vector<string>::iterator ite_end = ite_start;
			advance(ite_end,grp.mot_nb);
			phy_group_elt.erase(ite_start,ite_end);
			phy_group_elt.insert(ite_start,grp.pool_grp->phy_group_elt);
			*/
			
			phys_group_elt.clear();
			for(unsigned long i = 0; i < user_group_elt.size(); i++)
			{
				Pool_ns::GrpEltType type = user_group_elt_type[i];
				
				if(type == Pool_ns::MOTOR)
				{
					phys_group_elt.push_back(user_group_elt[i]);
				}	
				else if(type == Pool_ns::GROUP)
				{
					Pool_ns::MotorGroupPool &grp = pool_dev->get_motor_group_from_name(user_group_elt[i]);
		  			for (unsigned long loop = 0;loop < grp.mot_ids.size();loop++)
		  			{
		  				Pool_ns::MotorPool &mot = pool_dev->get_motor_from_id(grp.mot_ids[loop]);
		  				phys_group_elt.push_back(mot.obj_alias_lower);		  				
		  			}					
				}	
				else if(type == Pool_ns::PSEUDO_MOTOR)
				{
		 			Pool_ns::PseudoMotorPool &pm = pool_dev->get_pseudo_motor_from_name(user_group_elt[i]);
		  			for (unsigned long loop = 0;loop < pm.mot_elts.size();loop++)
		  			{
		  				string tmp_mot_name(pm.mot_elts[loop]->name);
		  				transform(tmp_mot_name.begin(),tmp_mot_name.end(),tmp_mot_name.begin(),::tolower);
						
						if(find(phys_group_elt.begin(),phys_group_elt.end(),tmp_mot_name) == phys_group_elt.end())
							phys_group_elt.push_back(tmp_mot_name);									  									
					}
				}	
			}
			update_elements();	
		}
		break;
		
//
// The structure of the motors/controlllers has changed.
//
		case Pool_ns::ElementStructureChange:
		{
			long ctrl_grp_idx;
			Tango::AutoTangoMonitor atm(pool_dev);
			Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_ctrl_from_motor_id(src->id);
			Pool_ns::CtrlGrp &ctrl_grp = get_ctrl_grp_from_id(ctrl_ref.id, ctrl_grp_idx);
			Pool_ns::MotorGroupPool &mgp = pool_dev->get_motor_group_from_id(motor_group_id);
//					
// Update controller data
//
			ctrl_grp.ct = &ctrl_ref;
//
// Update motor data
//
			IndMov &m = get_ind_mov_from_id(src->id);
			Pool_ns::PoolElement *old_invalid_pe_ptr = m.pe; 
			m.pe = src;
			
//
// Update element data in the Pool structure
//
			for(unsigned long l = 0; l < mgp.group_elts.size(); l++)
			{
				if(mgp.group_elts[l] == old_invalid_pe_ptr)
				{
					mgp.group_elts[l] = src;
					break;
				}
			}
		}
		break;
		
		default: 
		{
			assert(false);
		}
		break;
	}
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::update_state_from_ctrls
// 
// description : 	Updates the state attribute
//
//-----------------------------------------------------------------------------

void MotorGroup::update_state_from_ctrls(long idx, Tango::DevState state)
{
	Tango::DevState old_state = get_state();
	
//
// Read all states
//

	vector<Tango::DevState> old_state_array(state_array);
		
	long loop;
	
	if(idx == -1)
	{
		state_array.clear();
		read_state_from_ctrls();
	}
	else
	{
		if (state_array.size() == 0)
			read_state_from_ctrls();
		state_array[idx] = state;
	}
	
	string &_status = get_status();
	_status.clear();
	
//
// If it is the ghost group and if the request comes from the polling
// thread, eventually forward state event on ind element devices
//

	int th_id = omni_thread::self()->id();
	
	if (get_id() == 0)
	{
//
// If it is the ghost group and if the request comes from the polling
// thread, eventually forward state event on ind element devices
//
		if(th_id == get_polling_th_id())
		{
			send_state_event(old_state_array,state_array);
		}
//
// If it is the ghost group but the request comes from a motor for which there
// was a client state request, then inform the listeners that the state has changed  
// thread, eventually forward state event on ind element devices.
// Note: the motor device is not locked in the code below because this code should
//       only be reached from a motor call from a client which already has the motor lock.
//
		else if (idx != -1)
		{			
			Tango::DevState old_state = old_state_array[idx];
			Tango::DevState state = state_array[idx];
			if (old_state != state)
			{
				// Push event on the element device
				Tango::Device_3Impl *dev = ind_elts[idx]->pe->get_device();
				Tango::Attribute &state_att = dev->get_device_attr()->get_attr_by_name("State");
				state_att.fire_change_event();
	
				// Notify listeners						
				Pool_ns::MotorPool &pe = pool_dev->get_motor_from_id(ind_elts[idx]->id);
				if(pe.has_listeners())
				{
					Pool_ns::PoolElementEvent evt(Pool_ns::StateChange, &pe);
					evt.old_state = old_state;
					evt.new_state = state;
					pe.fire_pool_elem_change(&evt);
				}
			}
		}
	}
	
		
//
// Are there any elements in FAULT
//

	long nb;
	vector<Tango::DevState>::iterator v_sta_start, v_sta_stop;
	vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
	
	if ((nb = count(state_array.begin(),state_array.end(),Tango::FAULT)) != 0)
	{
		set_state(Tango::FAULT);
		v_sta_start = state_array.begin();
		for (loop = 0;loop < nb;loop++)
		{
			v_sta_stop = find(v_sta_start,state_array.end(),Tango::FAULT);
			long dist = distance(state_array.begin(),v_sta_stop);
			vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
			advance(im_ite,dist);
			Pool_ns::IndEltGrp *ind = *im_ite; 
			if (loop != 0)
				_status = _status + '\n';
			_status = _status + ind->get_family() + " " + ind->get_alias() + " is in FAULT";
			v_sta_start = v_sta_stop;
			v_sta_start++;						
		}
	}

//
// Is there any motor(s) in UNKNOWN
//

	else if ((nb = count(state_array.begin(),state_array.end(),Tango::UNKNOWN)) != 0)
	{
		set_state(Tango::UNKNOWN);
		v_sta_start = state_array.begin();
		for (loop = 0;loop < nb;loop++)
		{
			v_sta_stop = find(v_sta_start,state_array.end(),Tango::UNKNOWN);
			long dist = distance(state_array.begin(),v_sta_stop);
			vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
			advance(im_ite,dist);
			Pool_ns::IndEltGrp *ind = *im_ite;
			if (loop != 0)
				_status = _status + '\n';
			_status = _status + ind->get_family() + " " + ind->get_alias() + " is in UNKNOWN state";
			v_sta_start = v_sta_stop;
			v_sta_start++;						
		}
	}
		
//
// Is there any motor(s) in ALARM
//

	else if ((nb = count(state_array.begin(),state_array.end(),Tango::ALARM)) != 0)
	{
		set_state(Tango::ALARM);
		v_sta_start = state_array.begin();
		for (loop = 0;loop < nb;loop++)
		{
			v_sta_stop = find(v_sta_start,state_array.end(),Tango::ALARM);
			long dist = distance(state_array.begin(),v_sta_stop);
			vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
			advance(im_ite,dist);
			Pool_ns::IndEltGrp *ind = *im_ite;
			if (loop != 0)
				_status = _status + '\n';
			_status = _status + ind->get_family() + " " + ind->get_alias() + " is in ALARM";
			v_sta_start = v_sta_stop;
			v_sta_start++;						
		}
	}
	
//
// Is there any motor(s) moving
//

	else if ((nb = count(state_array.begin(),state_array.end(),Tango::MOVING)) != 0)
	{
		set_state(Tango::MOVING);
		v_sta_start = state_array.begin();
		for (loop = 0;loop < nb;loop++)
		{
			v_sta_stop = find(v_sta_start,state_array.end(),Tango::MOVING);
			long dist = distance(state_array.begin(),v_sta_stop);
			vector<Pool_ns::IndEltGrp*>::iterator im_ite = ind_elts.begin();
			advance(im_ite,dist);
			Pool_ns::IndEltGrp *ind = *im_ite;
			if (loop != 0)
				_status = _status + '\n';
			_status = _status + ind->get_family() + " " + ind->get_alias() + " is MOVING";
			v_sta_start = v_sta_stop;
			v_sta_start++;						
		}
	}
	
//
// All motor's ON
//

	else
	{
		set_state(Tango::ON);

//
// There is a trick here for client getting position with polling mode
// The movment thread stores motor position in the polling buffer and
// the client is getting position from this polling buffer
// When the movment thread detects that the movment is over
// (state != MOVING), it invalidates data from the polling buffer and
// therefore all clients will get data from hardware access.
// What could happens, is that a client thread detects first the
// end of the movment (before the movment thread). If this thread
// immediately reads the position after it detects the movment end, it will
// get the last value written in the polling buffer because the mov thread has not
// yet invalidate it.
// Therefore, if the thread executing this code is not the mov thread and if the state
// changed from MOVING to ON, delay the state changes that it will be detected by the
// movment thread. This movment thread is doing a motor call every 10 mS
//

		int th_id = omni_thread::self()->id();
		if (mov_th_id != 0)
		{	
			if ((old_state == Tango::MOVING) && (th_id != mov_th_id) && (abort_cmd_executed == false))
				set_state(Tango::MOVING);
			else
				_status = StatusNotSet;
		}
		else
			_status = StatusNotSet;
	}	
}	

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_state
 *
 *	description:	method to execute "State"
 *	This command gets the device state (stored in its <i>device_state</i> data member) and returns it to the caller.
 *
 * @return	State Code
 */
//+------------------------------------------------------------------
Tango::DevState MotorGroup::dev_state()
{
	Pool_ns::PoolGroupBaseDev::dev_state();
	DEBUG_STREAM << "MotorGroup::dev_state(): entering... !" << endl;

	if (pool_init_cmd == true)
		set_state(Tango::UNKNOWN);
	else
		update_state_from_ctrls();
			
	return get_state();
}

Pool_ns::CtrlGrp *MotorGroup::build_mot_ctrl(Pool_ns::ControllerPool &ctrl_ref)
{
	return new Pool_ns::CtrlGrp(ctrl_ref);	
}

MotorGroup::IndMov *MotorGroup::build_motor(Pool_ns::MotorPool &m_ref)
{
	Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_ctrl_from_id(m_ref.ctrl_id);
	
	long ctrlgrp_idx;
	Pool_ns::CtrlGrp *ctrl_grp = NULL;
	try
	{
		ctrl_grp = &get_ctrl_grp_from_id(ctrl_ref.id, ctrlgrp_idx);
	}
	catch(Tango::DevFailed &e)
	{
		ctrl_grp = build_mot_ctrl(ctrl_ref);
		ctrlgrp_idx = implied_ctrls.size();
		implied_ctrls.push_back(ctrl_grp);
	}
	
	IndMov *im = new IndMov(m_ref,ctrl_grp, motor_group_id, this);
	im->idx_in_grp = ind_elts.size();
	im->idx_in_ctrl = m_ref.obj_idx;
	im->idx_in_ctrlgrp = ctrlgrp_idx; // not used (yet!)
	im->obj_proxy = new Tango::DeviceProxy(m_ref.obj_tango_name.c_str());
	im->obj_proxy->set_transparency_reconnection(true);
	
	return im;		
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::build_grp
 *
 *	description:	Build from the user_group_elt property
 * 					value, information describing which motor
 * 					in the group belongs to group or to pseudo-motor
 */
//+------------------------------------------------------------------

void MotorGroup::build_grp() 
{
	vector<long> mot_id_list;
	vector<long> mot_id_ctrl;
	
	mot_id_list.reserve(ind_elt_nb);
	mot_id_ctrl.reserve(ind_elt_nb);
	
	{
		Tango::AutoTangoMonitor atm(pool_dev);
		
		if(is_ghost())
		{
			list<Pool_ns::MotorPool> &m_list = pool_dev->get_mot_list();		
			for (list<Pool_ns::MotorPool>::iterator m_ite = m_list.begin();
			     m_ite != m_list.end(); ++m_ite)
			{
				ind_elts.push_back(build_motor(*m_ite));
			}
			
			return;
		}		
//
// Get all motor ID in a loop
//

		long i;
		list<Pool_ns::MotorPool> &m_list = pool_dev->get_mot_list();
		for (i = 0;i < ind_elt_nb;i++)
		{
			mot_id_list.push_back(pool_dev->get_motor_id_from_name(phys_group_elt[i]));
			mot_id_ctrl.push_back(pool_dev->get_motor_ctrl_idx(phys_group_elt[i].c_str()));
		}
		
//
// Get list of implied controller for this group
//
		for (i = 0;i < ind_elt_nb;i++)
		{
			Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_ctrl_from_motor_id(mot_id_list[i]);
			Pool_ns::MotorPool &mot_ref = pool_dev->get_motor_from_id(mot_id_list[i]);
						
			long ct_id = ctrl_ref.id;
		
			Pool_ns::CtrlGrp *ctrl_ptr = NULL;
			if (implied_ctrls.empty() == true)
			{
				ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref);	
				implied_ctrls.push_back(ctrl_ptr);
			}
			else
			{
				for (unsigned long l = 0;l < implied_ctrls.size();l++)
				{
					if (implied_ctrls[l]->ctrl_id == ct_id)
					{
						ctrl_ptr = implied_ctrls[l];
						break;
					}
				}
				if (ctrl_ptr == NULL)
				{
					ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref);
					implied_ctrls.push_back(ctrl_ptr);
				}
			}
		
//
// Build motor group info
//

			IndMov *im = new IndMov(mot_ref,ctrl_ptr, motor_group_id, this); 
			im->idx_in_grp = i;
			im->idx_in_ctrl = mot_id_ctrl[i];
			im->idx_in_ctrlgrp = -1; // not used (yet!)
			im->obj_proxy = new Tango::DeviceProxy(phys_group_elt[i].c_str());
			im->obj_proxy->set_transparency_reconnection(true);

			vector<string>::iterator ite = find(user_group_elt.begin(),user_group_elt.end(),im->get_alias());

//
// If it is a motor directly used by the motor group, determine its index in the user array
//	

			if(ite != user_group_elt.end())
				im->idx_in_usr = distance(user_group_elt.begin(),ite);
			else
				im->idx_in_usr = -1;		
		
			ind_elts.push_back(im);
		}
	}
	
//
// Allocate arrays to store motor pos.
//

	SAFE_DELETE_ARRAY(attr_Position_read);
	attr_Position_read = new double[pos_spectrum_dim_x];
	
	SAFE_DELETE_ARRAY(phys_mot_pos);
	phys_mot_pos = new double[ind_elt_nb];
	
	SAFE_DELETE_ARRAY(attr_Elements_read);
	attr_Elements_read = (usr_elt_nb > 0) ? new Tango::DevString[usr_elt_nb] : NULL;
	
	SAFE_DELETE_ARRAY(attr_Motors_read);
	attr_Motors_read = (motor_list.size() > 0) ? new Tango::DevString[motor_list.size()] : NULL;
	
	SAFE_DELETE_ARRAY(attr_MotorGroups_read);
	attr_MotorGroups_read = (motor_group_list.size() > 0) ? new Tango::DevString[motor_group_list.size()] : NULL;
	
	SAFE_DELETE_ARRAY(attr_PseudoMotors_read);
	attr_PseudoMotors_read = (pseudo_motor_list.size() > 0) ? new Tango::DevString[pseudo_motor_list.size()] : NULL;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::build_grp_struct
 *
 *	description:	Build from the user_group_elt property
 * 					value, information describing which motor
 * 					in the group belongs to group or to pseudo-motor
 */
//+------------------------------------------------------------------

void MotorGroup::build_grp_struct()
{
	DEBUG_STREAM << "MotorGroup::build_grp_struct(): entering... for " << name() << endl;
	long mot_idx = 0;
	long idx_in_usr = 0;
	
	unsigned long nb_u_elt = user_group_elt.size();
	for (unsigned long loop = 0;loop < nb_u_elt;loop++)
	{
		if (find(motor_list.begin(),motor_list.end(),user_group_elt[loop]) != motor_list.end())
		{
			IndMov *ind_mov = static_cast<IndMov*>(ind_elts[mot_idx]);
			ind_mov->idx_in_usr = idx_in_usr;
			mot_idx++; 
			idx_in_usr++;
			user_group_elt_type.push_back(Pool_ns::MOTOR);
			continue;
		}
		else if (find(motor_group_list.begin(),motor_group_list.end(),user_group_elt[loop]) != motor_group_list.end())
		{
  			Pool_ns::MotorGroupPool &grp = pool_dev->get_motor_group_from_name(user_group_elt[loop]);
  			GrpInGrp tmp_grp(grp);
  			tmp_grp.idx_in_usr = loop;
  			tmp_grp.start_idx = mot_idx;
  			mot_idx = mot_idx + tmp_grp.mot_nb;

			// Fix in the IndMov elements belonging to this motor group the idx_in_usr element
			for(long i = 0; i < tmp_grp.mot_nb; i++)
			{
				IndMov *ind_mov = static_cast<IndMov*>(ind_elts[i + tmp_grp.start_idx]);
				ind_mov->idx_in_usr = idx_in_usr;
				idx_in_usr++;
			}

  			grp_in_grp.push_back(tmp_grp);
  			user_group_elt_type.push_back(Pool_ns::GROUP);
  			
		}
		else
		{
 			Pool_ns::PseudoMotorPool &psm = pool_dev->get_pseudo_motor_from_name(user_group_elt[loop]);
  			PsmInGrp tmp_psm(psm);
  			tmp_psm.mot_nb = psm.mot_elts.size();
  			tmp_psm.idx_in_usr = idx_in_usr;
  			idx_in_usr++;

			// Find the index of the first motor
  			vector<string>::iterator m_ite = find_in_phys_group_lst(psm.mot_elts[0]->name);
  			assert(m_ite != phys_group_elt.end());
  			long local_idx = distance(phys_group_elt.begin(), m_ite);
  			tmp_psm.start_idx = local_idx;
 
 //		
 // If this is the first pseudo motor which uses motors then the index can safely
 // increment. Otherwise, if it is using some motors that are already been used by
 // other pseudo motor in the same pseudo motor system, the index is not changed
 //
 			if(local_idx == mot_idx)
 				mot_idx = mot_idx + tmp_psm.mot_nb;
 				
  			psm_in_grp.push_back(tmp_psm);
  			user_group_elt_type.push_back(Pool_ns::PSEUDO_MOTOR);
		}
	}
	
//
// Group pseudo motors by controller
//
	for(unsigned long psm_idx = 0; psm_idx < psm_in_grp.size(); psm_idx++)
	{
		PsmInGrp &psm = psm_in_grp[psm_idx];
		PseudoMotorController *curr_psm_ctrl = psm.pool_psm.pseudo_motor->get_pm_ctrl();
		
		long ctrl_idx = 0;
		for(; ctrl_idx < psm_ctrls_in_grp.size(); ctrl_idx++)
		{
			if(psm_ctrls_in_grp[ctrl_idx].pool_psm_ctrl == curr_psm_ctrl)
				break;	
		}

		// New pseudo motor controller
		if(ctrl_idx == psm_ctrls_in_grp.size())
		{
			PsmCtrlInGrp tmp_psm_ctrl(curr_psm_ctrl);
			Pool_ns::PseudoMotCtrlFiCa *fica = 
				psm.pool_psm.pseudo_motor->get_pm_fica_ptr();
			
			tmp_psm_ctrl.pm_count = fica->get_pseudo_motor_role_nb();
			tmp_psm_ctrl.mot_count = fica->get_motor_role_nb();
			// Fill the vector with -1	
			tmp_psm_ctrl.psm_in_grp_idx.insert(tmp_psm_ctrl.psm_in_grp_idx.begin(),
											   tmp_psm_ctrl.pm_count,-1);
			tmp_psm_ctrl.is_complete = true;
			tmp_psm_ctrl.mot_nb = psm.mot_nb;
			tmp_psm_ctrl.start_idx = psm.start_idx;
			
			psm_ctrls_in_grp.push_back(tmp_psm_ctrl);
		}
		
		long role = psm.pool_psm.pseudo_motor->get_controller_idx();
		
		psm_ctrls_in_grp[ctrl_idx].psm_in_grp_idx[role-1] = psm_idx;
		psm.psm_ctrl_idx = ctrl_idx;
	}
	
//
// Determine which pseudo motor controllers have all pseudo motors included in this motor group.
// This is done for efficiency reasons
//
	vector<PsmCtrlInGrp>::iterator psm_ctrl_ite = psm_ctrls_in_grp.begin();
	for(;psm_ctrl_ite != psm_ctrls_in_grp.end(); psm_ctrl_ite++)
	{
		vector<long> &psm_in_grp_idx = psm_ctrl_ite->psm_in_grp_idx;
		if( find(psm_in_grp_idx.begin(), psm_in_grp_idx.end(), -1) != psm_in_grp_idx.end() )
		{
			psm_ctrl_ite->is_complete = false;
		}
	}
	
	nb_psm_in_grp = psm_in_grp.size();
	nb_grp_in_grp = grp_in_grp.size();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::from_phys_2_grp
 *
 *	description:	Build the array of motor position returned to user
 * 					If some pseudo-motor are involved in this group,
 * 					compute their positions from the motor physical
 * 					one.
 */
//+------------------------------------------------------------------

void MotorGroup::from_phys_2_grp()
{
	unsigned long loop;

//
// If we don't have any pseudo-motor in this group,
// simply copy the motor position
//
	
	if (nb_psm_in_grp == 0)
	{
		for (loop = 0;loop < ind_elt_nb;loop++)
			attr_Position_read[loop] = phys_mot_pos[loop];
	}
	else
	{
//
// Calculate all necessary pseudo motor positions
//
		for(unsigned long ctrl_idx = 0; ctrl_idx < psm_ctrls_in_grp.size(); ctrl_idx++)
		{
			vector<double> phy_pos;
			PsmCtrlInGrp &psm_ctrl = psm_ctrls_in_grp[ctrl_idx];
			PseudoMotorController *ctrl = psm_ctrl.pool_psm_ctrl;
			long start_idx = psm_ctrl.start_idx;
			long mot_nb = psm_ctrl.mot_nb;
			PsmInGrp &first_psm = psm_in_grp[psm_ctrl.psm_in_grp_idx[0]];
			
//
// For each controller build the list of involved physical motor positions
//
			for(long mot_idx = start_idx; mot_idx < start_idx + mot_nb; mot_idx++)
			{
				phy_pos.push_back(phys_mot_pos[mot_idx]);
			}
			
//
// calculate the positions of all pseudo motors involved
//
			vector<double> pm_pos(psm_ctrl.pm_count);
			{
				Pool_ns::AutoPythonLock pl = Pool_ns::AutoPythonLock();
				ctrl->CalcAllPseudo(phy_pos, pm_pos);
			}

//
// store the calculated pseudo motor positions in the output buffer
//
			for(unsigned long psm_idx = 0; psm_idx < psm_ctrl.psm_in_grp_idx.size(); psm_idx++)
			{
				long psm_idx_in_grp = psm_ctrl.psm_in_grp_idx[psm_idx];

				if(psm_idx_in_grp == -1)
					continue;

				PsmInGrp &psm = psm_in_grp[psm_idx_in_grp];
				long psm_role = psm.pool_psm.pseudo_motor->get_controller_idx();
				attr_Position_read[psm.idx_in_usr] = pm_pos[psm_role-1];
				DEBUG_STREAM << "Storing in " << psm.pool_psm.name << "(idx = " << psm.idx_in_usr << ",role=" << psm_role << ") with value " << pm_pos[psm_role-1] << endl;
			}
		}
		
//
// store motor positions
//
		for(unsigned long m_idx = 0; m_idx < ind_elts.size(); m_idx++)
		{
			IndMov *m = static_cast<IndMov*>(ind_elts[m_idx]);
			if(m->idx_in_usr >=0)
			{
				DEBUG_STREAM << "Storing usr_idx=" << m->idx_in_usr << " from idx in physical=" << m->idx_in_grp << endl;
				attr_Position_read[m->idx_in_usr] = phys_mot_pos[m->idx_in_grp];
			}
		}
	}
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::from_grp_2_phys
 *
 *	description:	Build the array of motor physical position from
 * 					the information sent by the caller
 */
//+------------------------------------------------------------------

void MotorGroup::from_grp_2_phys(const Tango::DevDouble *user_pos)
{
	unsigned long loop;
	
//
// If we don't have any pseudo-motor in this group,
// simply copy the motor position
//
	
	if (nb_psm_in_grp == 0)
	{
		for (loop = 0;loop < ind_elt_nb;loop++)
			phys_mot_pos[loop] = user_pos[loop];
		
		if(nb_grp_in_grp > 0)
		{
			
//
// Get motor group positions
//

			for(unsigned long mg_idx = 0; mg_idx < grp_in_grp.size(); mg_idx++)
			{
				GrpInGrp &grp = grp_in_grp[mg_idx];
				for(long ll = 0;ll < grp.mot_nb;ll++)
				{
					phys_mot_pos[grp.start_idx + ll] = user_pos[grp.idx_in_usr + ll];
				}
			}
		}
	}
	else
	{
		
//
// We are going to use the pseudo motor device proxy below so we check if the pool
// has already initialized all the proxy information
//

		pool_dev->create_proxies();

//
//
// For each pseudo motor simulate a write to check if limits are exceded 
//
		
		DEBUG_STREAM << "checking pseudo motor limits" << endl;
		for(unsigned long psm_idx = 0; psm_idx < psm_in_grp.size(); psm_idx++)
		{
			PsmInGrp &psm = psm_in_grp[psm_idx];
			Pool_ns::PseudoMotorPool &psm_pool = psm.pool_psm;
			
			psm_pool.pseudo_motor->set_group_mov(true);
			double position = user_pos[psm.idx_in_usr];
			try
			{
				DEBUG_STREAM << "\tChecking psm " << psm_idx << " with pos=" << position << endl;
				Tango::DeviceAttribute attr("Position", position);
				psm_pool.obj_proxy->write_attribute(attr);
				psm_pool.pseudo_motor->set_group_mov(false);
			}
			catch(Tango::DevFailed e)
			{
				psm_pool.pseudo_motor->set_group_mov(false);
				throw e;
			}
		} 		
		
		DEBUG_STREAM << "from_grp_2_phys > starting to interate osm ctrls..." << endl;
		for(unsigned long ctrl_idx = 0; ctrl_idx < psm_ctrls_in_grp.size(); ctrl_idx++)
		{
			PsmCtrlInGrp &psm_ctrl = psm_ctrls_in_grp[ctrl_idx];
			PseudoMotorController *ctrl = psm_ctrl.pool_psm_ctrl;
			PsmInGrp &first_psm = psm_in_grp[psm_ctrl.psm_in_grp_idx[0]];
			
			vector<double> psm_pos(psm_ctrl.pm_count);
			
//
// For the pseudo controllers which we don't receive the pseudo motor positions from the user, 
// they have to be calculated before, based on the current values of the motors which are involved
//	
		
			if(psm_ctrl.is_complete == false)
			{
				DEBUG_STREAM << "psm ctrl in mg is not complete." << endl;
				
//
// Get the Motor group inside any of the pseudo motors in this controller and through it
// read the current physical motor positions of all motors involved
//

				DEBUG_STREAM << "read position for mg inside the psm" << endl;
				Tango::DeviceProxy *mg = first_psm.pool_psm.pseudo_motor->get_motor_group_info().mg_proxy;			
				
				vector<double> phy_pos;
				mg->read_attribute("Position") >> phy_pos;
				
//
// Calculate all pseudo positions
//	
			
				DEBUG_STREAM << "calculate all old pseudo motor positions for psm ctrl" << endl;
				{
					Pool_ns::AutoPythonLock pl = Pool_ns::AutoPythonLock();
					ctrl->CalcAllPseudo(phy_pos,psm_pos); 
				}
			}
			
//
// Fill the pseudo motor positions vector with the pseudo positions given by the user
//	
		
			DEBUG_STREAM << "prepare psm position vector to send to psm ctrl" << endl;
			
			for(unsigned long psm_ctrl_idx = 0; psm_ctrl_idx < psm_ctrl.psm_in_grp_idx.size(); psm_ctrl_idx++)
			{
				long idx = psm_ctrl.psm_in_grp_idx[psm_ctrl_idx];
				
				if(idx == -1)
					continue;
				
				PsmInGrp &psm = psm_in_grp[idx];
				Pool_ns::PseudoMotorPool &pmp = psm.pool_psm;
				long role = pmp.pseudo_motor->get_controller_idx();
				psm_pos[role-1] = user_pos[psm.idx_in_usr];
				DEBUG_STREAM << "\t user psm index=" << idx << ",role=" << role << " stored with value " << psm_pos[role-1] << endl;
			}
			
			DEBUG_STREAM << "calculate physical positions of motors that belong to the current psm controller" << endl;
			vector<double> phy_pos(psm_ctrl.mot_count);
			{
				Pool_ns::AutoPythonLock pl = Pool_ns::AutoPythonLock();
				ctrl->CalcAllPhysical(psm_pos,phy_pos); 
			}
			
//
// Finally distribute the obtained motor positions in the output vector
//

			DEBUG_STREAM << "place the calculated physical positions in the correct place" << endl;			
			for(long idx = 0; idx < psm_ctrl.mot_nb; idx++)
			{
				phys_mot_pos[psm_ctrl.start_idx + idx] = phy_pos[idx]; 
			}
		}
		
//
// Get motor positions
//
		DEBUG_STREAM << "fill physical positions (if any)" << endl;
		for(unsigned long m_idx = 0; m_idx < ind_elts.size(); m_idx++)
		{
			IndMov *m = static_cast<IndMov*>(ind_elts[m_idx]);
			if(m->idx_in_usr >=0)
			{
				DEBUG_STREAM << "\tplacing physical motor from user index=" << m->idx_in_usr << "to physical=" << m->idx_in_grp << " with value=" << user_pos[m->idx_in_usr];
				phys_mot_pos[m->idx_in_grp] = user_pos[m->idx_in_usr];
			}
		}
		
//
// Get motor group positions
//	
		DEBUG_STREAM << "fill motor group positions (if any)" << endl;
		for(unsigned long mg_idx = 0; mg_idx < grp_in_grp.size(); mg_idx++)
		{
			GrpInGrp &grp = grp_in_grp[mg_idx];
			for(long ll = 0;ll < grp.mot_nb;ll++)
			{
				DEBUG_STREAM << "\tplacing physical motor (from mg) from user index=" << grp.idx_in_usr + ll << "to physical=" << grp.start_idx + ll << " with value=" << user_pos[grp.idx_in_usr + ll];
				phys_mot_pos[grp.start_idx + ll] = user_pos[grp.idx_in_usr + ll];
			}
		}
	}
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::add_motor_to_ghost_group
 *
 *	description:	Add a new motor to a group
 * 
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::add_motor_to_ghost_group(long mot_id)
{
	DEBUG_STREAM << "MotorGroup::add_motor_to_group()"  << endl;
	
//
// Refuse to do anything if it is not for the ghost group
//

	if (!is_ghost())
	{
		Tango::Except::throw_exception((const char *)"Motor_ControllerFailed",
										(const char *)"This feature is available only for the ghost motor group",
										(const char *)"MotorGroup::add_motor_to_group");
	}
	
//
// Return if motor already in group
//

	vector<string>::iterator ite;
	Pool_ns::MotorPool &mot_ref = pool_dev->get_motor_from_id(mot_id);
	ite = find(phys_group_elt.begin(),phys_group_elt.end(),mot_ref.name);
	if (ite != phys_group_elt.end())
		return;

	ind_elt_nb++;
	
	{
		Tango::AutoTangoMonitor atm(pool_dev);
				
//
// Get motor controller for this motor and eventually add it to
// the list of implied controller
//

		Pool_ns::ControllerPool &ctrl_ref = pool_dev->get_ctrl_from_motor_id(mot_id);
						
		long ct_id = ctrl_ref.id;

		Pool_ns::CtrlGrp *ctrl_ptr = NULL;
		if (implied_ctrls.empty() == true)
		{
			ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref);	
			implied_ctrls.push_back(ctrl_ptr);
		}
		else
		{
			for (unsigned long l = 0;l < implied_ctrls.size();l++)
			{
				if (implied_ctrls[l]->ctrl_id == ct_id)
				{
					ctrl_ptr = implied_ctrls[l];
					break;
				}
			}
			if (ctrl_ptr == NULL)
			{
				ctrl_ptr = new Pool_ns::CtrlGrp(ctrl_ref);
				implied_ctrls.push_back(ctrl_ptr);
			}
		}
		
//
// Build motor info for group
//
		IndMov *im = new IndMov(mot_ref,ctrl_ptr, motor_group_id, this); 
		im->idx_in_grp = ind_elt_nb - 1;
		im->idx_in_ctrl = pool_dev->get_motor_ctrl_idx(mot_ref.name.c_str());
		im->obj_proxy = new Tango::DeviceProxy(mot_ref.name);
		im->obj_proxy->set_transparency_reconnection(true);

//
// Add motor to group in vector and its alias_name in phys_group_elt
//
		
		phys_group_elt.push_back(im->get_alias());
		ind_elts.push_back(im);
	}

//
// Add entry in the state array
//

	state_array.push_back(Tango::ON);
					
//
// Change arrays size to store motor pos.
//

	delete [] attr_Position_read;
	attr_Position_read = new double[pos_spectrum_dim_x];
	
	delete [] phys_mot_pos;
	phys_mot_pos = new double[ind_elt_nb];
	
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::remove_motor_from_ghost_group
 *
 *	description:	Remove a motor from a group
 * 
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::remove_motor_from_ghost_group(long del_mot_id)
{
	DEBUG_STREAM << "MotorGroup::remove_motor_from_group(), motor id = " << del_mot_id << endl;

//
// Refuse to do anything if it is not for the ghost group
//

	if (!is_ghost())
	{
		Tango::Except::throw_exception(
				(const char *)"Motor_CantRemoveMotor",
				(const char *)"This feature is available only for the ghost motor group",
				(const char *)"MotorGroup::remove_motor_from_group");
	}
	
	long idx_in_array = 0;
	
	{
		Tango::AutoTangoMonitor atm(pool_dev);
					
//
// Find motor in group
//

		vector<Pool_ns::IndEltGrp*>::iterator ite;
		for (ite = ind_elts.begin();ite != ind_elts.end();++ite,++idx_in_array)
			if ((*ite)->id == del_mot_id)
				break;
		if (ite == ind_elts.end())
		{
			TangoSys_OMemStream o;
			o << "Motor with id " << del_mot_id << " is not a member of this group" << ends;
		
			Tango::Except::throw_exception(
					(const char *)"Motor_CantRemoveMotor",
					o.str(),
					(const char *)"MotorGroup::remove_motor_from_group");
		}
		Pool_ns::IndEltGrp* elt = (*ite);
		Pool_ns::CtrlGrp *ctrl_grp = elt->ctrl_grp;
//
// Remove motor from group
//
		vector<string>::iterator v_ite;
		assert(elt->name == phys_group_elt[idx_in_array]);
		v_ite = phys_group_elt.begin();
		advance(v_ite, idx_in_array);
		phys_group_elt.erase(v_ite);

		ind_elt_nb--;
		unsigned long l;

//
// Remove from internal list 
//
		ind_elts.erase(ite);
		SAFE_DELETE(elt);
		
//
// If the internal controller object no longer controls any element of this
// group then remove it
//
		if (ctrl_grp->channels.size() == 0)
		{
			vector<Pool_ns::CtrlGrp*>::iterator ctrl_ite = 
				find(implied_ctrls.begin(), implied_ctrls.end(), ctrl_grp);
			implied_ctrls.erase(ctrl_ite);
			SAFE_DELETE(ctrl_grp);
		}
	}

//
// Remove entry in the state array
//

	if (state_array.size() != 0)
	{
		vector<Tango::DevState>::iterator state_ite = state_array.begin();
		advance(state_ite,idx_in_array);
		state_array.erase(state_ite);
	}
			
//
// Change arrays size to store motor pos.
//

	delete [] attr_Position_read;
	attr_Position_read = new double[pos_spectrum_dim_x];
	
	delete [] phys_mot_pos;
	phys_mot_pos = new double[ind_elt_nb];
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::update_motor_info
 *
 *	description:	Update motor info into the group
 * 
 *  arg(s) : In : mot_id : The motor identifier
 */
//+------------------------------------------------------------------

void MotorGroup::update_motor_info(long upd_mot_id)
{
	DEBUG_STREAM << "MotorGroup::update_motor_info()"  << endl;
	
//
// Refuse to do anything if it is not for the ghost group
//

	if (motor_group_id != 0)
	{
		Tango::Except::throw_exception((const char *)"Motor_CantUpdateMotor",
										(const char *)"This feature is available only for the ghost motor group",
										(const char *)"MotorGroup::update_motor_info");
	}
	
//
// Find motor in group
//

	vector<Pool_ns::IndEltGrp*>::iterator ite;
	for (ite = ind_elts.begin();ite != ind_elts.end();++ite)
	{
		Pool_ns::IndEltGrp *elt = *ite;
		if (elt->id == upd_mot_id)
			break;
	}
	if (ite == ind_elts.end())
	{
		TangoSys_OMemStream o;
		o << "Motor with id " << upd_mot_id << " is not a member of this group" << ends;
	
		Tango::Except::throw_exception((const char *)"Motor_CantUpdateMotor",
										o.str(),(const char *)"MotorGroup::update_motor_info");
	}

//
// Update its info
//
	unsigned long l;
	
	for(l = 0; l < ind_elts.size(); l++)
		delete ind_elts[l];
	ind_elts.clear();

	for(l = 0; l < implied_ctrls.size(); l++)
		delete implied_ctrls[l]; 
	implied_ctrls.clear();

	build_grp();
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::dev_status
 *
 *	description:	method to execute "Status"
 *	This command gets the device status (stored in its <i>device_status</i> data member) and returns it to the caller.
 *
 * @return	Status description
 *
 */
//+------------------------------------------------------------------
Tango::ConstDevString MotorGroup::dev_status()
{
	Tango::ConstDevString	argout = Pool_ns::PoolGroupBaseDev::dev_status();
	DEBUG_STREAM << "MotorGroup::dev_status(): entering... !" << endl;

	//	Add your own code to control device here
	tmp_status = argout;
	Tango::DevState sta = get_state();
	
//
// If the motor is in FAULT, it could be because the ctrl is not OK.
// Otherwise, checks if the controller send an error string
//

	if (sta == Tango::FAULT)
	{
		vector<Pool_ns::CtrlGrp*>::iterator impl_ctrl_ite;
		MotorController *mc;
		for (impl_ctrl_ite = implied_ctrls.begin();impl_ctrl_ite != implied_ctrls.end();++impl_ctrl_ite)
		{
			Pool_ns::ControllerPool *cp = (*impl_ctrl_ite)->ct;
			mc = static_cast<MotorController *>(cp->ctrl);
			if ((cp->ctrl_fica_built == false) || (mc == NULL))
			{
				tmp_status = tmp_status + "\nThe controller object (" + cp->name + ") used by some motor(s) in this group is not initialized";
			}
		}
	}
		
	argout = tmp_status.c_str();
	return argout;
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::State_all_ind
 *
 *	description:	Get each motor state
 */
//+------------------------------------------------------------------

void MotorGroup::State_all_ind(vector<Controller *> &failed_ctrls)
{
	vector<Controller *>::iterator pos;
	Controller *ctrl;
	
	for (long loop = 0;loop < ind_elt_nb;loop++)
	{
		IndMov *ind_mov = static_cast<IndMov*>(ind_elts[loop]);
		Pool_ns::MotorPool *mp = ind_mov->get_motor();
		Motor_ns::Motor *motor = mp->motor;
		
		if(motor->should_be_in_fault() == true)
		{
			mp->motor->set_state(Tango::FAULT);
		}
		else 
		{
			try
			{
				MotorController::MotorState mi;
				Pool_ns::ControllerPool *cp = ind_mov->ctrl_grp->ct;							
				ctrl = static_cast<MotorController *>(cp->ctrl);
				
				if (ctrl != NULL)
				{
					if (failed_ctrls.empty() != true)
					{
						pos = find(failed_ctrls.begin(),failed_ctrls.end(),ctrl);
						if (pos != failed_ctrls.end())
						{
							WARN_STREAM << "MotorGroup::State_all_ind: there are failed controllers for " << ind_mov->name << endl;
							mp->motor->set_state(Tango::UNKNOWN);
							state_array.push_back(Tango::UNKNOWN);
							continue;
						}
					}
					
					if (ind_mov->atm_ptr == NULL)
					{
						WARN_STREAM << "MotorGroup::State_all_ind: AutoTangoMonitor for " << ind_mov->name << " is NULL" << endl;
						mp->motor->set_state(Tango::UNKNOWN);
						state_array.push_back(Tango::UNKNOWN);
						continue;
					}
					ctrl->StateOne(ind_mov->idx_in_ctrl,&mi);
					mp->motor->set_motor_state_from_group(mi);
				}
				else
					mp->motor->set_state(Tango::FAULT);
			}
			catch (Tango::DevFailed &e)
			{
				mp->motor->set_state(Tango::UNKNOWN);
			}
		}
		state_array.push_back(mp->motor->get_state());
	}
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_ind_mov_from_id
 *
 *	description: Obtains the IndMov motor structure for the given 
 *               motor id
 *
 * @return A reference to an IndMov motor data structure for the 
 *         given motor id 
 */
//+------------------------------------------------------------------

MotorGroup::IndMov &MotorGroup::get_ind_mov_from_id(long id)
{
	return static_cast<IndMov&>(get_ind_elt_from_id(id));
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_ind_mov_from_name
 *
 *	description: Obtains the IndMov motor structure for the given 
 *               motor name
 *
 * @return A reference to an IndMov motor data structure for the 
 *         given motor name
 */
//+------------------------------------------------------------------

MotorGroup::IndMov &MotorGroup::get_ind_mov_from_name(string &name)
{
	return static_cast<IndMov&>(get_ind_elt_from_name(name));
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_psm_from_name
 *
 *	description: Obtains the PsmInGrp pseudo motor structure for 
 *               the given motor name
 *
 * @return A reference to an PsmInGrp pseudo motor data structure
 *         for the given pseudo motor name
 */
//+------------------------------------------------------------------

MotorGroup::PsmInGrp &MotorGroup::get_psm_from_name(string &name)
{
	vector<PsmInGrp>::iterator psm_ite = psm_in_grp.begin();
	for(; psm_ite != psm_in_grp.end(); psm_ite++)
	{
		if(psm_ite->psm_alias == name)
			break;
	}
	
	if (psm_ite == psm_in_grp.end())
	{
		TangoSys_OMemStream o;
		o << "No PsmInGrp with name " << name << " found in Motor group pseudo motor list" << ends;

		Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
					  				   (const char *)"MotorGroup::get_psm_from_name");	
	}	
	return *psm_ite;	
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_grp_from_id
 *
 *	description: Obtains the GrpInGrp group structure for the given 
 *               motor group id
 *
 * @return A reference to an GrpInGrp group data structure for the 
 *         given motor group id 
 */
//+------------------------------------------------------------------

MotorGroup::GrpInGrp &MotorGroup::get_grp_from_id(long id)
{
	vector<GrpInGrp>::iterator grp_ite = grp_in_grp.begin();
	for(; grp_ite != grp_in_grp.end(); grp_ite++)
	{
		if(grp_ite->grp_id == id)
			break;
	}
	
	if (grp_ite == grp_in_grp.end())
	{
		TangoSys_OMemStream o;
		o << "No GrpInGrp with ID " << id << " found in Motor group motor group list" << ends;

		Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
					  				   (const char *)"MotorGroup::get_grp_from_id");	
	}	
	return *grp_ite;	
}

//+------------------------------------------------------------------
/**
 *	method:	MotorGroup::get_grp_from_name
 *
 *	description: Obtains the GrpInGrp group structure for the given 
 *               group name
 *
 * @return A reference to an GrpInGrp group data structure for the 
 *         given group name
 */
//+------------------------------------------------------------------

MotorGroup::GrpInGrp &MotorGroup::get_grp_from_name(string &name)
{
	vector<GrpInGrp>::iterator grp_ite = grp_in_grp.begin();
	for(; grp_ite != grp_in_grp.end(); grp_ite++)
	{
		if(grp_ite->pool_grp.name == name)
			break;
	}
	
	if (grp_ite == grp_in_grp.end())
	{
		TangoSys_OMemStream o;
		o << "No GrpInGrp with name " << name << " found in Motor group motor group list" << ends;

		Tango::Except::throw_exception((const char *)"Pool_BadArgument",o.str(),
					  				   (const char *)"MotorGroup::get_grp_from_name");	
	}	
	return *grp_ite;	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::get_polling_th_id
// 
// description : 	gets the polling thread id  
//
// \return the polling thread id
//-----------------------------------------------------------------------------

int MotorGroup::get_polling_th_id() 
{ 
	return (static_cast<MotorGroupClass *>(device_class))->polling_th_id; 
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::get_pool_obj
// 
// description : 	gets Pool motor group object for this motor group
//
// \return the pool motor group
//-----------------------------------------------------------------------------

Pool_ns::PoolElement &MotorGroup::get_pool_obj()
{ 
	return pool_dev->get_motor_group_from_id(motor_group_id); 
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::handle_temporary_siblings
// 
// description : 	should be invoked by the ghost motor group periodically
//                  to manage the temporary siblings 
//
//-----------------------------------------------------------------------------

void MotorGroup::handle_temporary_siblings()
{
	pool_dev->handle_tmp_motor_groups();
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::find_in_user_group_lst
// 
// description : 	finds the element in the user_group_elt property
//
// \return the element position in the user_group_elt
//-----------------------------------------------------------------------------
vector<string>::iterator MotorGroup::find_in_user_group_lst(string &elt_name)
{
	string elt_name_lower(elt_name);
	transform(elt_name_lower.begin(),elt_name_lower.end(),elt_name_lower.begin(),::tolower);
	
	vector<string>::iterator ite = user_group_elt.begin();
	for(;ite != user_group_elt.end(); ite++)
	{
		string lower(*ite);
		transform(lower.begin(),lower.end(),lower.begin(),::tolower);
		if(lower == elt_name_lower)
			break;
	}
	return ite; 
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::find_in_phys_group_lst
// 
// description : 	finds the motor in the phys_group_elt property
//
// \return the motor position in the phys_group_elt
//-----------------------------------------------------------------------------
vector<string>::iterator MotorGroup::find_in_phys_group_lst(string &motor_name)
{
	string motor_name_lower(motor_name);
	transform(motor_name_lower.begin(),motor_name_lower.end(),motor_name_lower.begin(),::tolower);
	
	vector<string>::iterator ite = phys_group_elt.begin();
	for(;ite != phys_group_elt.end(); ite++)
	{
		string lower(*ite);
		transform(lower.begin(),lower.end(),lower.begin(),::tolower);
		if(lower == motor_name_lower)
			break;
	}
	return ite; 
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::find_in_motor_lst
// 
// description : 	finds the motor in the motor_list property
//
// \return the motor position in the motor_list
//-----------------------------------------------------------------------------
vector<string>::iterator MotorGroup::find_in_motor_lst(string &motor_name)
{
	string motor_name_lower(motor_name);
	transform(motor_name_lower.begin(),motor_name_lower.end(),motor_name_lower.begin(),::tolower);
	
	vector<string>::iterator ite = motor_list.begin();
	for(;ite != motor_list.end(); ite++)
	{
		string lower(*ite);
		transform(lower.begin(),lower.end(),lower.begin(),::tolower);
		if(lower == motor_name_lower)
			break;
	}
	return ite; 	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::find_in_motor_group_lst
// 
// description : 	finds the motor in the motor_group_list property
//
// \return the motor position in the motor_group_list
//-----------------------------------------------------------------------------
vector<string>::iterator MotorGroup::find_in_motor_group_lst(string &motor_group_name)
{
	string motor_group_name_lower(motor_group_name);
	transform(motor_group_name_lower.begin(),motor_group_name_lower.end(),motor_group_name_lower.begin(),::tolower);
	
	vector<string>::iterator ite = motor_group_list.begin();
	for(;ite != motor_group_list.end(); ite++)
	{
		string lower(*ite);
		transform(lower.begin(),lower.end(),lower.begin(),::tolower);
		if(lower == motor_group_name_lower)
			break;
	}
	return ite; 	
}

//+----------------------------------------------------------------------------
//
// method : 		MotorGroup::find_in_pseudo_motor_lst
// 
// description : 	finds the motor in the pseudo_motor_list property
//
// \return the motor position in the pseudo_motor_list
//-----------------------------------------------------------------------------
vector<string>::iterator MotorGroup::find_in_pseudo_motor_lst(string &pseudo_motor_name)
{
	string pseudo_motor_name_lower(pseudo_motor_name);
	transform(pseudo_motor_name_lower.begin(),pseudo_motor_name_lower.end(),pseudo_motor_name_lower.begin(),::tolower);
	
	vector<string>::iterator ite = pseudo_motor_list.begin();
	for(;ite != pseudo_motor_list.end(); ite++)
	{
		string lower(*ite);
		transform(lower.begin(),lower.end(),lower.begin(),::tolower);
		if(lower == pseudo_motor_name_lower)
			break;
	}
	return ite; 	
}

///////////////////////////////////////////////////
// E L E M E N T S
///////////////////////////////////////////////////

MotorGroup::IndMov::IndMov(Pool_ns::MotorPool &ref, Pool_ns::CtrlGrp *ctrl_ptr,
						   long grp, Tango::Device_3Impl *dev/* = NULL*/):
	Pool_ns::IndEltGrp(ref, ctrl_ptr, grp, dev), idx_in_grp(-1), 
	idx_in_usr(-1)
{}

Pool_ns::MotorPool *
MotorGroup::IndMov::get_motor()
{
	return static_cast<Pool_ns::MotorPool*>(pe);
}

MotorGroup::GrpInGrp::GrpInGrp(Pool_ns::MotorGroupPool &ref):
	grp_id(ref.id),pool_grp(ref)
{ 
	mot_nb=ref.mot_ids.size(); 
	usr_elts_nb = ref.group_elts.size(); 
	pos_len = ref.group->pos_spectrum_dim_x;
}

MotorGroup::GrpInGrp::GrpInGrp &
MotorGroup::GrpInGrp::operator=(const MotorGroup::GrpInGrp::GrpInGrp &rhs)
{ 
	grp_id=rhs.grp_id;
	pool_grp=rhs.pool_grp;
	mot_nb=rhs.mot_nb;
	usr_elts_nb = rhs.usr_elts_nb;
	pos_len = rhs.pos_len;
	start_idx=rhs.start_idx;
	idx_in_usr=rhs.idx_in_usr;
	return *this;
}

MotorGroup::PsmInGrp::PsmInGrp(Pool_ns::PseudoMotorPool &ref):
	pool_psm(ref),psm_alias(ref.name) 
{}

MotorGroup::PsmInGrp::PsmInGrp &
MotorGroup::PsmInGrp::operator=(const MotorGroup::PsmInGrp::PsmInGrp &rhs)
{
	mot_nb=rhs.mot_nb;
	start_idx=rhs.start_idx;
	idx_in_usr=rhs.idx_in_usr;
	psm_ctrl_idx=rhs.psm_ctrl_idx;
	pool_psm=rhs.pool_psm;
	psm_alias=rhs.psm_alias;
	return *this;
}
}	//	namespace
