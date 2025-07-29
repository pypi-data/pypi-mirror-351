from .all_interfaces_class import all_interfacesClass
from time import sleep

class CommonActionsClass:
    def __init__(self,all_interfaces:all_interfacesClass):        
        self.all_interfaces = all_interfaces

    ### function to initilize both thermistor temperatures to 25    
    def initialize(self):
            therm1=self.all_interfaces.thermistor1
            therm2=self.all_interfaces.thermistor2            
            std_temp=25
            therm1.set_temperature(std_temp)
            therm2.set_temperature(std_temp)
            sleep(2)

    #### function to print given message in text log file and log window
    def print_in_file(self, message):
        self.all_interfaces.auto_test_interface.add_to_test_log(str(message))

    #### function to get any can signal data from the can interface
    def get_can_signal_data(self, signal_name):
        """Get a specific message by name"""
        sig=self.all_interfaces.can_interface.name + "__"+str(signal_name)
        val=self.all_interfaces.data_interface.get_data_value(sig)
        return val

    #### function to set thermistor values. ch_select ==99 for all
    def set_thermistor_temperature(self,ch_select,temperature):
        if(ch_select==1):
            self.all_interfaces.thermistor1.set_temperature(temperature)
        elif(ch_select==2): 
            self.all_interfaces.thermistor2.set_temperature(temperature)
        elif(ch_select==99):
            self.all_interfaces.thermistor1.set_temperature(temperature)
            self.all_interfaces.thermistor2.set_temperature(temperature)
    
    def get_relay_state(self):
        relay=self.all_interfaces.relay_read_interface
        state=relay.get_state()
        return state