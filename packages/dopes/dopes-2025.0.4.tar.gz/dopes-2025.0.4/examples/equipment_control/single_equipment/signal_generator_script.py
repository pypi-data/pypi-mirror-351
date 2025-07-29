# =============================================================================
# 1. Import classes and modules
# =============================================================================

# =============================================================================
# # If local installation of dopes instead of using PyPI (https://pypi.org/project/dopes/)
# import sys
# sys.path.insert(1, 'D:/Roisin/Documents/dopes/dopes')
# =============================================================================

import dopes.equipment_control.equipment as eq
import dopes.equipment_control.signal_generator as signal_generator
import time

# =============================================================================
# 2. List  available connections (chopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
mygenerator=signal_generator.signal_generator("USB0::0x0699::0x0349::C012340::INSTR",timeout=5e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
waveform="sin"
freq=1e3 
amplitude=1 
offset=0.5

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mygenerator.initialize(waveform=waveform, freq=freq, amp=amplitude, offset=offset)

# =============================================================================
# 6. Measurement script
# =============================================================================
mygenerator.set_output("ON")
time.sleep(10)

# =============================================================================
# 7. Close connection
# =============================================================================
mygenerator.close_connection()
