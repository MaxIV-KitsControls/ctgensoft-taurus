//=============================================================================
//
// file :        ZeroDExpChannel.h
//
// description : Include for the ZeroDExpChannel class.
//
// project :	ZeroDimensionExperimentChannel
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.9  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.8  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.7  2007/07/26 07:05:42  tcoutinho
// fix bug 10 : Change all tango commands from Stop to Abort
//
// Revision 1.6  2007/05/25 13:34:18  tcoutinho
// - fixes to state event propagation to the ghost group
//
// Revision 1.5  2007/05/22 13:43:09  tcoutinho
// - added new method
//
// Revision 1.4  2007/05/11 08:43:56  tcoutinho
// - fixed bugs
//
// Revision 1.3  2007/05/10 09:32:34  etaurel
// - Small changes for better 64 bits portability
//
// Revision 1.2  2007/02/08 07:56:49  etaurel
// - Changes after compilation -Wall. Added the CumulatedValue attribute and
// everything to implement it (thread....)
//
// Revision 1.1  2007/01/26 08:35:02  etaurel
// - We now have a first release of ZeroDController
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//=============================================================================
#ifndef _ZERODEXPCHANNEL_H
#define _ZERODEXPCHANNEL_H

#include <PoolIndBaseDev.h>

//using namespace Tango;

/**
 * @author	$Author$
 * @version	$Revision$
 */

 //	Add your own constants definitions here.
 //-----------------------------------------------


namespace ZeroDExpChannel_ns
{

class	ZeroDThread;

/**
 * Class Description:
 * Zero Dimension Experiment device used by the Sardana project device pool
 */

/*
 *	Device States Description:
*  Tango::ON :       The experiment channel is ON
*  Tango::FAULT :    A fault has been reported by the device controller
*  Tango::UNKNOWN :  Impossible to communicate with the device controller
*  Tango::MOVING :   An acquisition is running
 */


//class ZeroDExpChannel: public Tango::Device_3Impl
class ZeroDExpChannel: public Pool_ns::PoolIndBaseDev
{
public :
	//	Add your own data members here
	//-----------------------------------------


	//	Here is the Start of the automatic code generation part
	//-------------------------------------------------------------	
/**
 *	@name attributes
 *	Attributs member data.
 */
//@{
		Tango::DevDouble	*attr_Value_read;
		Tango::DevBoolean	*attr_SimulationMode_read;
		Tango::DevLong	*attr_CumulationType_read;
		Tango::DevLong	attr_CumulationType_write;
		Tango::DevDouble	*attr_CumulatedValue_read;
		Tango::DevLong	*attr_CumulatedPointsNumber_read;
		Tango::DevLong	*attr_CumulatedPointsError_read;
		Tango::DevDouble	*attr_CumulationTime_read;
		Tango::DevDouble	attr_CumulationTime_write;
		Tango::DevDouble	*attr_ValueBuffer_read;
		Tango::DevDouble	*attr_TimeBuffer_read;
//@}

/**
 *	@name Device properties
 *	Device properties member data.
 */
//@{
/**
 *	The experiment channel identifier
 */
	Tango::DevLong	channel_id;
/**
 *	Stop cumulate data if there is not enough time to get one more point
 *	before the  timer expires
 */
	Tango::DevBoolean	stopIfNoTime;
/**
 *	Continue cumulating data even if an error occurs during data reading
 */
	Tango::DevBoolean	continueOnError;
//@}

/**@name Constructors
 * Miscellaneous constructors */
//@{
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device Name
 */
	ZeroDExpChannel(Tango::DeviceClass *cl,string &s);
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device Name
 */
	ZeroDExpChannel(Tango::DeviceClass *cl,const char *s);
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device name
 *	@param d	Device description.
 */
	ZeroDExpChannel(Tango::DeviceClass *cl,const char *s,const char *d);
//@}

/**@name Destructor
 * Only one desctructor is defined for this class */
//@{
/**
 * The object desctructor.
 */	
	~ZeroDExpChannel() {delete_device();};
/**
 *	will be called at device destruction or at init command.
 */
	void delete_device();
//@}

	
/**@name Miscellaneous methods */
//@{
/**
 *	Initialize the device
 */
	virtual void init_device();
/**
 *	Always executed method befor execution command method.
 */
	virtual void always_executed_hook();

//@}

/**
 * @name ZeroDExpChannel methods prototypes
 */

//@{
/**
 *	Hardware acquisition for attributes.
 */
	virtual void read_attr_hardware(vector<long> &attr_list);
/**
 *	Extract real attribute values for Value acquisition result.
 */
	virtual void read_Value(Tango::Attribute &attr);
/**
 *	Extract real attribute values for SimulationMode acquisition result.
 */
	virtual void read_SimulationMode(Tango::Attribute &attr);
/**
 *	Extract real attribute values for CumulationType acquisition result.
 */
	virtual void read_CumulationType(Tango::Attribute &attr);
/**
 *	Write CumulationType attribute values to hardware.
 */
	virtual void write_CumulationType(Tango::WAttribute &attr);
/**
 *	Extract real attribute values for CumulatedValue acquisition result.
 */
	virtual void read_CumulatedValue(Tango::Attribute &attr);
/**
 *	Extract real attribute values for CumulatedPointsNumber acquisition result.
 */
	virtual void read_CumulatedPointsNumber(Tango::Attribute &attr);
/**
 *	Extract real attribute values for CumulatedPointsError acquisition result.
 */
	virtual void read_CumulatedPointsError(Tango::Attribute &attr);
/**
 *	Extract real attribute values for CumulationTime acquisition result.
 */
	virtual void read_CumulationTime(Tango::Attribute &attr);
/**
 *	Write CumulationTime attribute values to hardware.
 */
	virtual void write_CumulationTime(Tango::WAttribute &attr);
/**
 *	Extract real attribute values for ValueBuffer acquisition result.
 */
	virtual void read_ValueBuffer(Tango::Attribute &attr);
/**
 *	Extract real attribute values for TimeBuffer acquisition result.
 */
	virtual void read_TimeBuffer(Tango::Attribute &attr);
/**
 *	Read/Write allowed for Value attribute.
 */
	virtual bool is_Value_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for SimulationMode attribute.
 */
	virtual bool is_SimulationMode_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for CumulationType attribute.
 */
	virtual bool is_CumulationType_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for CumulatedValue attribute.
 */
	virtual bool is_CumulatedValue_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for CumulatedPointsNumber attribute.
 */
	virtual bool is_CumulatedPointsNumber_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for CumulatedPointsError attribute.
 */
	virtual bool is_CumulatedPointsError_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for CumulationTime attribute.
 */
	virtual bool is_CumulationTime_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for ValueBuffer attribute.
 */
	virtual bool is_ValueBuffer_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for TimeBuffer attribute.
 */
	virtual bool is_TimeBuffer_allowed(Tango::AttReqType type);
/**
 *	Execution allowed for Start command.
 */
	virtual bool is_Start_allowed(const CORBA::Any &any);
/**
 *	Execution allowed for Abort command.
 */
	virtual bool is_Abort_allowed(const CORBA::Any &any);
/**
 * This command gets the device status (stored in its <i>device_status</i> data member) and returns it to the caller.
 *	@return	Status description
 *	@exception DevFailed
 */
	virtual Tango::ConstDevString	dev_status();
/**
 * Start acquiring data
 *	@exception DevFailed
 */
	void	start();
/**
 * Stop acquiring data
 *	@exception DevFailed
 */
	void	abort();

/**
 *	Read the device properties from database
 */
	 void get_device_property();
//@}

	//	Here is the end of the automatic code generation part
	//-------------------------------------------------------------	



protected :	
	//	Add your own data members here
	//-----------------------------------------
	
public:
	typedef struct ShData
	{
		bool							th_exit;
		bool							i_am_dead;
		long							error_nb;
		bool							cont_error;
		bool							stop_if_no_time;
		long							cum_time;
		long							cum_type;
		vector<double>					read_values;
		vector<double>					acq_dates;
		Tango::DevErrorList				errors;
		long							fire_event;
		struct timespec					sleep_time;
	};
	
protected:	
	double			read_value;
	double			cum_read_value;
	Tango::DevLong	cum_nb;
	Tango::DevLong	cum_err;
	
	ZeroDThread		*th;	
	omni_mutex		the_mutex;
	ShData			the_shared_data;
	
	typedef struct Simu_data
	{	
		double				simu_time;
		long				simu_type;
		ZeroDExpChannel		*channel;
		
		Simu_data(ZeroDExpChannel *);
		~Simu_data();
	};
	
	Simu_data			*save_atts;

	// Warning: the following method should only be executed
	// when the running thread has a lock on the Pool
	Pool_ns::PoolElement &get_pool_obj();

	void inform_ghost(Tango::DevState,Tango::DevState);
	
public:	
	virtual long get_id() { return channel_id; }
	virtual void base_abort(bool);
	virtual void init_pool_element(Pool_ns::PoolElement *);
	void save_att_values() {save_atts = new Simu_data(this);}
	void restore_att_values() {if (save_atts!=NULL){delete save_atts;save_atts=NULL;}}
	
};

}	// namespace_ns

#endif	// _ZERODEXPCHANNEL_H
