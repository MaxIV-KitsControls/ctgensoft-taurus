package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.SardanaDevice;

public abstract class ElementListTreeNode extends SardanaTreeNode
{
	protected String name;
	
	public ElementListTreeNode(String name, DevicePool pool)
	{
		super(pool);
		this.name = name;
	}
	
	@Override
	public String toString()
	{
		return name;
	}
	
	public DevicePool getModel()
	{
		return (DevicePool) getUserObject();
	}
	
	public abstract void updateChilds();
	
	public void updateChilds(List<?> elems)
	{
		// The list changed.
		// If this method is invoked then the invoker should be the DevicePool object.
		// If this is the case then the DevicePool object contains already the new internal updated list
		removeAllChildren();

		for(Object elem : elems)
			add(new SardanaTreeNode(elem));
	}
	
	public SardanaTreeNode getChildByDeviceName(String deviceName)
	{
		if(children == null || children.size() == 0)
			return null;
		
		for(Object node : children)
		{
			SardanaTreeNode snode = (SardanaTreeNode) node;
			SardanaDevice elem = (SardanaDevice) snode.getUserObject();
			
			if(elem.getDeviceName().equalsIgnoreCase(deviceName))
				return snode;
		}
		return null;
	}
}
