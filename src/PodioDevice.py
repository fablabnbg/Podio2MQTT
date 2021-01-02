'''
Created on 30.12.2020

@author: ian
'''
from homie.device_base import Device_Base

class Device_Podio(Device_Base):
    '''
    classdocs
    '''


    def __init__(self, device_id=None, name=None, homie_settings=None, mqtt_settings=None):
        '''
        Constructor
        '''
        if homie_settings == None:
            pass
        
        if mqtt_settings == None:
            mqtt_settings = {
                "MQTT_BROKER": "ia216",
            }
            
        super().__init__("flnpodio", "FLN Podio Integration", homie_settings, mqtt_settings)        
        
        