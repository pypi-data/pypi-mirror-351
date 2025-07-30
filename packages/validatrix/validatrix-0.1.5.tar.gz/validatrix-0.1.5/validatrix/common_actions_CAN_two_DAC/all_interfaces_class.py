
from ..data_collection import DataCollectionInterface
from ..can_interface import CANInterface    
from ..thermistor_emulation import ThermistorEmulationInterface
from ..DAC_interface import DACInterface
from ..automated_test_interface import AutomatedTestInterface
from ..digital_read_interface import DigitalReadInterface


class all_interfacesClass:
    def __init__(self,data_interface:DataCollectionInterface=None,can_interface:CANInterface=None,
                 thermistor1:ThermistorEmulationInterface=None,thermistor2:ThermistorEmulationInterface=None,
                 relay_read_interface:DigitalReadInterface=None,auto_test_interface:AutomatedTestInterface=None):
        
        self.data_interface=data_interface
        self.can_interface=can_interface
        self.thermistor1=thermistor1
        self.thermistor2=thermistor2
        self.relay_read_interface=relay_read_interface
        self.auto_test_interface=auto_test_interface
    
    def add_data_interface(self,data_interface:DataCollectionInterface):
        self.data_interface=data_interface
    
    def add_can_interface(self,can_interface:CANInterface):
        self.can_interface=can_interface    

    def add_thermistor1(self,thermistor1:ThermistorEmulationInterface):
        self.thermistor1=thermistor1
    
    def add_thermistor2(self,thermistor2:ThermistorEmulationInterface):
        self.thermistor2=thermistor2
    
    def add_relay_read_interface(self,relay_read_interface:DigitalReadInterface):
        self.relay_read_interface=relay_read_interface

    def add_auto_test_interface(self,auto_test_interface:AutomatedTestInterface):
        self.auto_test_interface=auto_test_interface
