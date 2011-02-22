//=============================================================================
//
// file :        CommunicationChannelUtil.h
//
// description : Include for the CommunicationChannelUtil class.
//
// project :	Sardana Device Pool
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//
//=============================================================================

#ifndef _COMMUNICATIONCHANNELUTIL_H
#define _COMMUNICATIONCHANNELUTIL_H

#include <PoolBaseUtil.h>

/**
 * @author	$Author$
 * @version	$Revision$
 */

/**
 * The namespace for the pool tango class
 */
namespace Pool_ns
{
	struct PoolElement;
}

namespace CommunicationChannel_ns
{

/**
 * The CommunicationChannel utility class
 */
class CommunicationChannelUtil:public Pool_ns::PoolBaseUtil
{
public:
	CommunicationChannelUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolBaseUtil(p_ptr) {}
	virtual ~CommunicationChannelUtil() {}
	
	virtual void remove_object(Tango::Device_3Impl *dev);
	virtual long get_static_attr_nb(Tango::DeviceClass *);
};

}	// namespace_ns

#endif	// _COMMUNICATIONCHANNELUTIL_H
