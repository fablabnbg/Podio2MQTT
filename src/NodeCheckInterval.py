'''
Created on 30.12.2020

@author: ian
'''

from homie.node.node_base import Node_Base
from homie.node.property.property_datetime import Property_DateTime
from homie.node.property.property_string import Property_String

from datetime import datetime, timedelta
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_enum import Property_Enum
from homie.node.property.property_boolean import Property_Boolean

class NodeCheckInterval(Node_Base):    
    '''
    classdocs
    '''
    def __init__(self, device, node_id, name, type_="next_check", retain=True, qos=1):        
        '''
        Constructor
        '''
        super().__init__(device, node_id, name, type_, retain, qos)
        self.add_property(Property_String(self, "checkobject", f"Zu prüfendes Objekt {node_id}"))
        self.add_property(Property_DateTime(self, "nextcheck", f"Nächste Prüfung ({node_id})")) ## TODO: make settable
        self.add_property(Property_String(self, "instruction", f"Wartungsanleitung {node_id}"))
        self.add_property(Property_Integer(self, 'prewarntime', f'Vorwarnzeit {node_id}', unit='hours', settable= False))
        self.add_property(Property_Enum(self, "expiration", f"Fälligkeit ({node_id})", settable=False, data_format="Valid,Expired,Due_Soon"))  # TODO: Clarify, if a state for failed check shall be added here
        self.add_property(Property_Boolean(self, "passed", f"Prüfung Bestanden ({node_id})", settable=False))
        #self.add_property(Property_Base(self, "nextcheck", "Nächste Prüfung", false, True, 1, unit, data_type, data_format, value, set_value, tags, meta))

    def updateNextCheck(self, nextcheck):        
        newtime = self.get_property('nextcheck')
        prewarn = self.get_property('prewarntime').value
        if prewarn is None: prewarn = 0
        nt = datetime.strptime(nextcheck, "%Y-%m-%d %H:%M:%S")                
        newtime.value = nt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")        
        time_now = datetime.now()        
        if (nt < time_now):
            newstate = "Expired"
        elif ( (nt - timedelta(hours=prewarn)) < time_now):
            newstate = "Due_Soon"
        else:
            newstate = "Valid"
        self.get_property('expiration').value = newstate
          
    def updateInstruction(self, instructions):
        inst = self.get_property('instruction')
        inst.value = instructions
    
    def updateDescription(self, description):
        desc = self.get_property('checkobject')
        desc.value = description
        
    def updatePreWarning(self, preWarnTime):
        preWarn = self.get_property('prewarntime')
        if (not preWarnTime): preWarnTime = 0
        preWarn.value = preWarnTime
    
    def updatePassed(self, passed):
        self.get_property('passed').value = passed
                