//=============================================================================
//
// file :        ZeroDthread.h
//
// description : Include for the ZeroDThread class.
//
// project :	Sardana's device pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.2  2007/05/11 08:43:56  tcoutinho
// - fixed bugs
//
// Revision 1.1  2007/02/08 07:56:49  etaurel
// - Changes after compilation -Wall. Added the CumulatedValue attribute and
// everything to implement it (thread....)
//
//
// copyleft :   CELLS/ALBA
//		Edifici Ciences Nord
//		Campus Universitari de Bellaterra
//		Universitat Autonoma de Barcelona
//		08193 Bellaterra, Barcelona, SPAIN
//

#ifndef _ZERODTHREADL_H
#define _ZERODTHREAD_H

#include <tango.h>
#include <ZeroDExpChannel.h>

namespace ZeroDExpChannel_ns
{

class ZeroDExpChannel;

/**
 * A thread class specific for 0D experiment channel data acquisition
 */
class ZeroDThread: public omni_thread, public Tango::LogAdapter
{
public:
	ZeroDThread(ZeroDExpChannel *dev,omni_mutex &mut,ZeroDExpChannel::ShData &dat):
	omni_thread(),Tango::LogAdapter(dev),the_mutex(mut),the_shared_data(dat),the_dev(dev)
	{start_undetached();}

	virtual ~ZeroDThread() {}

	void *run_undetached(void *);
	void th_exit(Tango::Attribute &,bool);
	bool is_enough_time(long,struct timeval &,long &);

private:
	omni_mutex 					&the_mutex;
	ZeroDExpChannel::ShData		&the_shared_data;
	
	bool						local_th_exit;
	bool						local_cont_error;
	bool						local_stop_time;
	long						local_cum_time;
	long						local_cum_type;
	long						local_nb_read_event;
	struct timespec				local_sleep_time;
	struct timeval				start_th_time;
	ZeroDExpChannel				*the_dev;
	
};

}  // namespace

#endif // _ZERODTHREAD_H
