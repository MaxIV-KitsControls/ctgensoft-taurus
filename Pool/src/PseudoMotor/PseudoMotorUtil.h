//=============================================================================
//
// file :        MotorUtil.h
//
// description : Include for the PoolBaseDev class.
//
// project :	Sardana Device Pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2007/08/23 10:33:42  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.1  2007/08/17 13:11:25  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.1  2007/01/16 14:26:02  etaurel
// - First release with the PoolBaseDev base class
//
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#ifndef _PSEUDOMOTORUTIL_H
#define _PSEUDOMOTORUTIL_H

#include <PoolBaseUtil.h>

/**
 * @author	$Author$
 * @version	$Revision$
 */

namespace PseudoMotor_ns
{

/**
 * The PseudoMotor utility class
 */
class PseudoMotorUtil:public Pool_ns::PoolBaseUtil
{
public:
	PseudoMotorUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolBaseUtil(p_ptr) {}
	virtual ~PseudoMotorUtil() {}
	
	virtual void remove_object(Tango::Device_3Impl *dev);
	virtual long get_static_attr_nb(Tango::DeviceClass *);
	virtual void add_2_full_name(Pool_ns::PoolElement *);
};

}	// namespace_ns

#endif	// _PSEUDOMOTORUTIL_H
