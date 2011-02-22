#ifndef MOTORGROUPUTIL_H_
#define MOTORGROUPUTIL_H_

#include <PoolBaseUtil.h>

/**
 * @author	$Author$
 * @version	$Revision$
 */

namespace Pool_ns
{
struct PoolElement;
}

namespace MotorGroup_ns
{

/**
 * The MotorGroup utility class
 */
class MotorGroupUtil : public Pool_ns::PoolBaseUtil
{
public:
	MotorGroupUtil(Pool_ns::Pool *p_ptr):Pool_ns::PoolBaseUtil(p_ptr) {}
	virtual ~MotorGroupUtil() {}
	
	virtual void remove_object(Tango::Device_3Impl *dev);
	virtual long get_static_attr_nb(Tango::DeviceClass *);
	virtual void add_2_full_name(Pool_ns::PoolElement *);
};

}	// namespace_ns

#endif /*MOTORGROUPUTIL_H_*/
