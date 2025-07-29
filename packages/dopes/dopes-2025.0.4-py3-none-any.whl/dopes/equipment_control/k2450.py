import dopes.equipment_control.equipment as equipment
class k2450(equipment.equipment):
    
    """Class to control k2450 SMU"""
    model="K2400 or K2450"
    company="Keithley"
    url="https://www.tek.com/en/products/keithley/digital-multimeter/dmm7510"


    def initialize(self, source_mode,measurement_mode, compliance, autozero=True, nplc=1,digits=6,continuous_trigger=False,disp_enable=True):
        
        """ Function to initialize the K2400 SMU  with the desired settings
        
            args:
               \n\t- source_mode (string) : source mode of the SMU ("current" or "voltage")
               \n\t- measurement_mode (string) : measurement mode of the SMU ("current", "voltage" or "resistance")
               \n\t- compliance (scalar) : compliance of the source
               \n\t- autozero (boolean) : if true, enable autozero of the SMU
               \n\t- nplc (scalar) : set NPLC to set the integration time for the measurement. For a NPLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec
               \n\t- digits (int) : display resolution in number of bits
               \n\t- continuous_trigger (boolean) : if true, the display of the equipment does not freeze after a measurement. When disabled, the instrument operates at a higher speed
               \n\t- disp_enable (boolean) : if true, enable the front panel display circuitry. When disabled, the instrument operates at a higher speed
        """
        mode_name={"voltage":"VOLT", "current":"CURR", "resistance":"RES"}        
        self.output_state="OFF"
        self.pyvisa_resource.write("*RST")
        self.source_mode=source_mode
        self.continuous_trigger=continuous_trigger
        
        if source_mode=="voltage":
            self.pyvisa_resource.write(":SOUR:FUNC VOLT")   
            self.pyvisa_resource.write(":SOUR:VOLT:ILIM %E"%compliance)     # set compliance

        if source_mode=="current":
            self.pyvisa_resource.write(":SOUR:FUNC CURR")   
            self.pyvisa_resource.write(":SOUR:CURR:VLIM %E"%compliance)     # set compliance


        if measurement_mode=="voltage":
            self.pyvisa_resource.write(":SENS:FUNC 'VOLT'")   
            self.pyvisa_resource.write(":SENS:VOLT:RANG:AUTO ON")     # set automatic range

        elif measurement_mode=="current":
            self.pyvisa_resource.write(":SENS:FUNC 'CURR'")   
            self.pyvisa_resource.write(":SENS:CURR:RANG:AUTO ON")     # set automatic range

        elif measurement_mode=="resistance":
            self.pyvisa_resource.write(":SENS:FUNC 'RES'") 
            self.pyvisa_resource.write(":SENS:RES:RANG:AUTO ON")     # set automatic range

            
        self.pyvisa_resource.write(":DISP:%s:DIG %d"%(mode_name[measurement_mode],digits))   
        self.pyvisa_resource.write(":SENS:%s:NPLC %d"%(mode_name[measurement_mode],nplc))           # set NPLC. For a PLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec

        if disp_enable:
            self.pyvisa_resource.write(":DISP:LIGHT:STAT ON100")     # This command is used to enable and disable the front panel display circuitry. When disabled, the instrument operates at a higher speed.
        else:
             self.pyvisa_resource.write(":DISP:LIGHT:STAT OFF")     # This command is used to enable and disable the front panel display circuitry. When disabled, the instrument operates at a higher speed.
             
        if autozero:
            self.pyvisa_resource.write(":SENS:%s:AZER ON"%mode_name[measurement_mode])          # enable auto-zero
        else:
            self.pyvisa_resource.write(":SENS:%s:AZER OFF"%mode_name[measurement_mode])



        if continuous_trigger:
            self.pyvisa_resource.write(":TRIG:LOAD 'LoopUntilEvent', DISP, 0")     # able continuous triggering

        else:
            self.pyvisa_resource.write("TRIG:CONT OFF")


          
    def read_single(self):
        """ Function to read a single measurement data. The output is turn off at the end of the measurement only if continuous_trigger and output_state have been initialized as false and off
        
            return:
               \n\t- data (float) : float with the value of the measurement
        """
        self.pyvisa_resource.write(":OUTP ON")

        if self.continuous_trigger:
            self.pyvisa_resource.write(":ABORt")    
            data=float(self.pyvisa_resource.query("MEAS?"))
            self.pyvisa_resource.write(":TRIG:LOAD 'LoopUntilEvent', DISP, 0")     # able continuous triggering
            self.pyvisa_resource.write(":INIT")     
        else:
            data=float(self.pyvisa_resource.query("MEAS?"))
            self.pyvisa_resource.write(":OUTP %s"%self.output_state)

        return data
    
    def set_source(self,value):
        """ Function to set the source bias
        
            args:
               \n\t- value (scalar) : value of the bias point
        """
        if self.source_mode=="current":
            self.pyvisa_resource.write(":SOUR:CURR %E"%value)           #set output current
        elif self.source_mode=="voltage":
            self.pyvisa_resource.write(":SOUR:VOLT %E"%value)           #set output voltage


    def set_output(self,output_state="ON"):
        """ Function to set the state of the outpute 
        
            args:
               \n\t- output_state (string) : "ON" and "OFF" to turn the output on or off
        """
        self.output_state=output_state
        self.pyvisa_resource.write(":OUTP %s"%output_state)
        if self.continuous_trigger:
            self.pyvisa_resource.write(":INIT")

        
        
