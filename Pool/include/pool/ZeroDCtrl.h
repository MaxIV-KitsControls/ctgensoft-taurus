#ifndef ZERODCTRL_H_
#define ZERODCTRL_H_

#include <pool/Ctrl.h>

/**
 * The 0D experiment channel controller base class
 */
class ZeroDController:public Controller
{
public:
	ZeroDController(const char *);
	virtual ~ZeroDController();
	
//
// Methods to read ExpChannel value
//

	virtual void PreReadAll() {}
	virtual void PreReadOne(long) {}
	virtual void ReadAll() {}
	virtual double ReadOne(long);
	
protected:
	double			ZeroD_NaN;
};

		
#endif /*COTICTRL_H_*/
