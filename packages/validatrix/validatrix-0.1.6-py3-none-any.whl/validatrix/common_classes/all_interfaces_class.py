
from ..data_collection import DataCollectionInterface
from ..can_interface import CANInterface    
from ..thermistor_emulation import ThermistorEmulationInterface
from ..DAC_interface import DACInterface
from ..automated_test_interface import AutomatedTestInterface
from ..digital_read_interface import DigitalReadInterface
from ..RS485_slave_interface import RS485_slave_class,RS485_slave_server_class


class all_interfacesClass:
    def __init__(self):
        
        self.data_interface=None        
        self.auto_test_interface=None
        self.internal_can_interface_list=[]
        self.internal_thermistor_emulation_list=[]
        self.internal_relay_read_interface_list=[]  
        self.internal_RS485_slave_list=[]

    def add_interface(self,interface_name,interface_object):
        if interface_name == 'data_interface':
            if not isinstance(interface_object, DataCollectionInterface):
                raise TypeError("Expected a DataCollectionInterface object")
            self.data_interface =interface_object
        elif interface_name == 'auto_test_interface':
            if not isinstance(interface_object, AutomatedTestInterface):
                raise TypeError("Expected an AutomatedTestInterface object")
            self.auto_test_interface = interface_object
        elif 'int_can' in interface_name:
            if not isinstance(interface_object, CANInterface):
                raise TypeError("Expected a CANInterface object")
            self.internal_can_interface_list.append(interface_object)
        elif 'int_thermistor' in interface_name:
            if not isinstance(interface_object, ThermistorEmulationInterface):
                raise TypeError("Expected a ThermistorEmulationInterface object")
            self.internal_thermistor_emulation_list.append(interface_object)
        elif 'int_relay_read' in interface_name:
            if not isinstance(interface_object, DigitalReadInterface):
                raise TypeError("Expected a DigitalReadInterface object")
            self.internal_relay_read_interface_list.append(interface_object)
        elif 'int_RS485_slave' in interface_name:
            if not isinstance(interface_object, (RS485_slave_class)):
                raise TypeError("Expected a RS485_slave_class or RS485_slave_server_class object")
            self.internal_RS485_slave_list.append(interface_object)
        else:
            raise ValueError(f"Unknown interface name: {interface_name}")
    
   