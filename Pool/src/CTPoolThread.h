//=============================================================================
//
// file :        CTPoolThread.h
//
// description : Include for the CTPoolThread class.
//
// project :	Sardana Device pool
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.11  2007/08/30 12:40:39  tcoutinho
// - changes to support Pseudo counters.
//
// Revision 1.10  2007/07/24 07:11:06  tcoutinho
// fix bug: in data acquisition with a measurement it is necessary to check the state of the master channel in order to know when to stop all other channels
//
// Revision 1.9  2007/07/23 16:41:38  tcoutinho
// fix bug: Stop all channels when master stops during acquisition
//
// Revision 1.8  2007/02/16 10:01:26  tcoutinho
// - development checkin
//
// Revision 1.7  2007/02/13 14:39:43  tcoutinho
// - fix bug in motor group when a motor or controller are recreated due to an InitController command
//
// Revision 1.6  2007/02/08 16:18:14  tcoutinho
// - controller safety on PoolGroupBaseDev
//
// Revision 1.5  2007/02/08 10:49:28  etaurel
// - Some small changes after the merge
//
// Revision 1.4  2007/02/08 08:51:13  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.3  2007/02/07 16:53:06  tcoutinho
// safe guard commit
//
// Revision 1.2  2007/02/06 09:41:02  tcoutinho
// - added MeasurementGroup
//
// Revision 1.1  2007/01/16 14:28:30  etaurel
// - Initial revicion of the CT thread code
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//----------------------------------------------------------------------------------

#ifndef _CTPOOLTHREAD_H
#define _CTPOOLTHREAD_H

#include <Pool.h>
#include <CTExpChannel.h>
#include <MeasurementGroup.h>

namespace Pool_ns
{

struct CtrlInCount
{
	CtrlInCount(long id,ControllerPool &ref):ctrl_id(id),ct(ref),lock_ptr(NULL) {}
	CtrlInCount &operator=(const CtrlInCount &rhs) {ctrl_id=rhs.ctrl_id;ct=rhs.ct;return *this;}
	
	long			ctrl_id;
	ControllerPool	&ct;
	AutoPoolLock	*lock_ptr;
	
	void Lock()		{ lock_ptr = new AutoPoolLock(ct.get_ctrl_fica_mon()); }
	void Unlock()	{ if(lock_ptr != NULL) { delete lock_ptr; lock_ptr = NULL; } }
};

struct CtInCount
{
	CtInCount(long id,CTExpChannelPool &ref,ControllerPool &ct_ref):ct_id(id),ct_pool(ref),cp(ct_ref),
		state_att(ct_pool.ct_channel->get_device_attr()->get_attr_by_name("state")),
		val_att(ct_pool.ct_channel->get_device_attr()->get_attr_by_name("Value")),
		atm_ptr(NULL) 
	{}

	CtInCount &operator=(const CtInCount &rhs)
	{ct_id=rhs.ct_id;ct_pool=rhs.ct_pool;cp=rhs.cp;state_att=rhs.state_att,val_att=rhs.val_att;return *this;}
	
	long					ct_id;
	CTExpChannelPool		&ct_pool;
	ControllerPool			&cp;
	Tango::Attribute		&state_att;
	Tango::Attribute		&val_att;
	Tango::AutoTangoMonitor	*atm_ptr;
	
	void Lock()		{ atm_ptr = new Tango::AutoTangoMonitor(ct_pool.ct_channel); }
	void Unlock()	{ if(atm_ptr != NULL) { delete atm_ptr; atm_ptr = NULL; } }
	void set_mov_th_id(int th_id) { ct_pool.ct_channel->set_mov_th_id(th_id); }
};

struct GrpInCount
{
	GrpInCount(MeasurementGroupPool &ref):mgp(ref),grp(mgp.group),
		state_att(grp->get_device_attr()->get_attr_by_name("state")), atm_ptr(NULL)
	{
		grp_proxy = new Tango::DeviceProxy(grp->get_name());
	}
	
	GrpInCount &operator=(const GrpInCount &rhs) {grp=rhs.grp;grp_proxy=rhs.grp_proxy;state_att=rhs.state_att;}
	
	~GrpInCount() 
	{
		SAFE_DELETE(grp_proxy); 
		ct_value_att.clear(); 
	}
	
	void set_channels(vector<long> ct_channel_id, vector<long> virt_pc_ids)
	{
		map<long,MeasurementGroup_ns::MeasurementGroup::SingleValChInGrp *> pseudo_elts;
		
		for(unsigned long l = 0; l < ct_channel_id.size(); l++)
		{
			MeasurementGroup_ns::MeasurementGroup::SingleValChInGrp *elt = 
				static_cast<MeasurementGroup_ns::MeasurementGroup::SingleValChInGrp *>
				(&(grp->get_channel_from_id(ct_channel_id[l])));
			
			string att_name = elt->name + DYN_ATTR_SUFIX;
			Tango::Attribute &attr = grp->get_device_attr()->get_attr_by_name(att_name.c_str()); 
			ct_value_att.push_back(&attr);
			
			for(unsigned long i = 0; i < elt->used_by.size(); i++)
				pseudo_elts[elt->used_by[i]->id] = elt->used_by[i];
		}
		map<long,MeasurementGroup_ns::MeasurementGroup::SingleValChInGrp *>::iterator ite;
		for(ite = pseudo_elts.begin(); ite != pseudo_elts.end(); ite++)
		{
			string att_name = ite->second->name + DYN_ATTR_SUFIX;
			Tango::Attribute &attr = grp->get_device_attr()->get_attr_by_name(att_name.c_str());
			pc_value_att.push_back(&attr);
		}
		
		for(unsigned long ul = 0; ul < virt_pc_ids.size(); ++ul)
		{
			MeasurementGroup_ns::MeasurementGroup::PseudoCoInGrp *elt = 
				static_cast<MeasurementGroup_ns::MeasurementGroup::PseudoCoInGrp *>
				(&(grp->get_channel_from_id(virt_pc_ids[ul])));
			string att_name = elt->name + DYN_ATTR_SUFIX;
			Tango::Attribute &attr = grp->get_device_attr()->get_attr_by_name(att_name.c_str());
			pc_value_att.push_back(&attr);
		}
	}
	
	MeasurementGroupPool					&mgp;
	MeasurementGroup_ns::MeasurementGroup	*grp;
	Tango::Attribute						&state_att;
	vector<Tango::Attribute*>				ct_value_att;
	vector<Tango::Attribute*>				pc_value_att;
	Tango::DeviceProxy						*grp_proxy;
	Tango::AutoTangoMonitor					*atm_ptr;
	
};

struct AquisitionInfo
{
	long				master_id;
	double				master_value;
	AquisitionMode 		mode;
	long 				master_idx_in_cts;
	long				master_idx_in_grp;
	vector<long>		ct_ids;
	vector<long>		virt_pc_ids;		///< list of pseudo counters that are not dependent on a physical counter
	
	AquisitionInfo &operator=(const AquisitionInfo &ref)
	{ master_id = ref.master_id; master_value = ref.master_value; 
	  mode = ref.mode; master_idx_in_cts = ref.master_idx_in_cts; 
	  master_idx_in_grp = ref.master_idx_in_grp; ct_ids = ref.ct_ids;
	  virt_pc_ids = ref.virt_pc_ids; }
};

class CTPoolThread: public omni_thread
{
public :

	CTPoolThread(AquisitionInfo &info,Pool *p_dev,Tango::TangoMonitor *mon,long gr=-1)
	:aq_info(info),pool_dev(p_dev),mon_ptr(mon),group_id(gr) {}
	
	void run(void *);
	void manage_thread_exception(Tango::DevFailed &,vector<CtrlInCount> &,
								 vector<CtInCount> &,auto_ptr<GrpInCount> &,
								 string &,bool,long);
	
	Tango::TangoMonitor						*mon_ptr;
	CTExpChannel_ns::CTExpChannel			*failed_channel;
	MeasurementGroup_ns::MeasurementGroup	*failed_group;
	long									group_id;
	
protected:
	AquisitionInfo				aq_info;
	Pool 						*pool_dev;
	
};

}	// namespace_ns

#endif	// _POOLTHREAD_H
