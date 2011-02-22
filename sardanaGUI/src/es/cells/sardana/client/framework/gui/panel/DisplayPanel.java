/*
 * DisplayPanel.java
 *
 * Created on June 7, 2006, 10:15 AM
 */

package es.cells.sardana.client.framework.gui.panel;

import java.awt.CardLayout;

import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PseudoMotor;

/**
 *
 * @author  tcoutinho
 */
public class DisplayPanel extends javax.swing.JPanel {

	protected static final String EMPTY_PANEL = "Empty";
	protected static final String CTRL_PANEL = "Controller";
	protected static final String POOL_PANEL = "Pool";
	protected static final String MOTOR_PANEL = "Motor";
	protected static final String MOTOR_GROUP_PANEL = "Motor Group";
	protected static final String PSEUDO_MOTOR_PANEL = "Pseudo Motor";
	protected static final String SARDANA_PANEL = "Sardana";
	protected static final String GRAPH_PANEL = "Graph";
	
	/** Creates new form DisplayPanel */
	public DisplayPanel() {
		initComponents();
	}

	/** This method is called from within the constructor to
	 * initialize the form.
	 * WARNING: Do NOT modify this code. The content of this method is
	 * always regenerated by the Form Editor.
	 */
    // <editor-fold defaultstate="collapsed" desc=" Generated Code ">//GEN-BEGIN:initComponents
    private void initComponents() 
    {
        
    	sardanaPanel = new SardanaPanel();
    	emptyPanel = new EmptyPanel();
        devicePoolPanel = new DevicePoolPanel();
        motorGroupPanel = new MotorGroupPanel();
        motorPanel = new MotorPanel();
        controllerPanel = new ControllerPanel();
        pseudoMotorPanel = new PseudoMotorPanel();
        graphPanel = new GraphPanel();
        
        setLayout(new java.awt.CardLayout());

        add(sardanaPanel, SARDANA_PANEL);
        
        add(emptyPanel, EMPTY_PANEL);

        add(devicePoolPanel, POOL_PANEL);

        add(motorGroupPanel, MOTOR_GROUP_PANEL);

        add(motorPanel, MOTOR_PANEL);

        add(controllerPanel, CTRL_PANEL);

        add(pseudoMotorPanel, PSEUDO_MOTOR_PANEL);
        
        add(graphPanel, GRAPH_PANEL);
        
    }// </editor-fold>//GEN-END:initComponents

	public void showGraph(DevicePool pool)
	{
		graphPanel.setModel(pool);
		((CardLayout) getLayout()).show(this, GRAPH_PANEL);
	}

	public void showController(Controller controller, DevicePool pool)
	{
		controllerPanel.setModel(controller, pool);
		((CardLayout) getLayout()).show(this, CTRL_PANEL);
	}

	public void showMotor(Motor motor, DevicePool pool)
	{
		motorPanel.setModel(motor, pool);
		((CardLayout) getLayout()).show(this, MOTOR_PANEL);
	}

	public void showPseudoMotor(PseudoMotor pseudoMotor, DevicePool pool)
	{
		pseudoMotorPanel.setModel(pseudoMotor, pool);
		((CardLayout) getLayout()).show(this, PSEUDO_MOTOR_PANEL);
	}
	
	public void showMotorGroup(MotorGroup group, DevicePool pool)
	{
		motorGroupPanel.setModel(group, pool);
		((CardLayout) getLayout()).show(this, MOTOR_GROUP_PANEL);
	}

	public void showDevicePoolPanel(DevicePool pool, int index)
	{
		devicePoolPanel.setDevicePool(pool, index);
		((CardLayout) getLayout()).show(this, POOL_PANEL);
	}

	public void showEmptyPanel()
	{
		((CardLayout) getLayout()).show(this, EMPTY_PANEL);
	}

	public void showSardanaPanel()
	{
		((CardLayout) getLayout()).show(this, SARDANA_PANEL);
	}

    // Variables declaration - do not modify//GEN-BEGIN:variables
	private SardanaPanel sardanaPanel;
    private ControllerPanel controllerPanel;
    private DevicePoolPanel devicePoolPanel;
    private EmptyPanel emptyPanel;
    private MotorGroupPanel motorGroupPanel;
    private MotorPanel motorPanel;
    private PseudoMotorPanel pseudoMotorPanel;
    private GraphPanel graphPanel;
    // End of variables declaration//GEN-END:variables


}
