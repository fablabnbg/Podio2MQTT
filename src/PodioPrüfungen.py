#!/usr/bin/python3
'''
Created on 30.12.2020

@author: ian
'''
from PodioDevice import Device_Podio
from NodeCheckInterval import NodeCheckInterval
import time

CLIENT_ID = 'openhab-integration'
CLIENT_KEY = 'HI0yfWHlhUB2wENHvNlg4O3tFsPcOBtM1LzIrm3pgIzwveC6PURDfi75gVEWH40Z'

# # Test (Beta-Workspace)
APP_ID = 25603856
APP_KEY = '1734fc9680f24e664f5f58f4b1e80b8f' 

# VIEW_ID = 48228122 # alle Items
VIEW_ID = 48229153  # nur "akltive" (nicht archivierte) Items 

# # Prod (Base-Workspace)
# APP_ID =  7394305
# APP_KEY = '805b82c497684cff9b5eb9de0950c2d5'
# VIEW_ID = 22148662

from pypodio2 import api

from podioconfig import PODIO_CONFIG as cfg

class Pruefung:

    def __init__(self, item_id, next_date, description, prewarning, result, instructions=''):
        self.id = item_id
        self.next_date = next_date
        self.desc = description
        self.prew = prewarning
        self.res  = result
        self.inst = instructions

    def __repr__(self):
        return "ID:\t{}\nObject:\t{}\nNext Date:\t{}\nInstructions:\t ...({} bytes)\n".format(self.id, self.desc, self.next_date, len(self.inst))


class PodioPruefungApp:

    def __init__(self): 
        print(cfg)
        #self.c = api.OAuthAppClient(CLIENT_ID, CLIENT_KEY, APP_ID, APP_KEY)
        self.c = api.OAuthAppClient(cfg['CLIENT_ID'], cfg['CLIENT_KEY'], cfg['APP_ID'], cfg['APP_KEY'])        
        
    def create_pruefung_items(self):
        self.all_pruefungen = {}
        fitems = self.c.Item.filter_by_view(APP_ID, VIEW_ID)
        count = 0
        for pruef in fitems['items']:  # iterate over items
            nextp = None
            desc = None
            obj = None   
            preWarning = None
            result = None
            for pruef_field in pruef['fields']:
                flabel = pruef_field['label']
                if (flabel == 'Beschreibung'):
                    desc = pruef_field['values'][0]['value']
                elif (flabel == 'Nächste Prüfung (berechnet)'):
                    nextp = pruef_field['values'][0]['start']
                elif (flabel == 'Prüfobjekt'):
                    obj = pruef_field['values'][0]['value']
                elif (flabel == 'Vorwarnzeit'):
                    preWarning = int(pruef_field['values'][0]['value'] / (60 * 60))
                elif (flabel == 'Ergebnis'):
                    resultstr = pruef_field['values'][0]['value']['text'] 
                    print("Prüfergebnis: " + resultstr)
                    result = (resultstr == 'in Ordnung')
#                 elif (flabel == "Status"):        # not necessary, if view is used that contains active only elements
#                     print(pruef_field['values'][0]['value'])
#                     if (pruef_field['values'][0]['value']['text'] == "Archiviert"):
#                         print("INAKTIV!!!")
                else:
                    print('Unused flabel' + flabel)
                    
            node_id = "pruefung" + str(count)
            newp = Pruefung(node_id, nextp, obj, preWarning, result, desc)
            print(preWarning)            
            self.all_pruefungen[node_id] = newp
            count += 1  


if __name__ == '__main__':
    
    pdevice = Device_Podio()
    
    app = PodioPruefungApp()
    app.create_pruefung_items()
    print(app.all_pruefungen)
        
    for pruef_id in app.all_pruefungen:
        pnode = NodeCheckInterval(pdevice, pruef_id, pruef_id)
        pdevice.add_node(pnode)
        
    pdevice.start()
    
    while True:
        for node_id in pdevice.nodes:
            print(node_id)            
            pdevice.nodes[node_id].updatePreWarning(app.all_pruefungen[node_id].prew)
            pdevice.nodes[node_id].updateNextCheck(app.all_pruefungen[node_id].next_date)
            pdevice.nodes[node_id].updateDescription(app.all_pruefungen[node_id].desc)
            pdevice.nodes[node_id].updateInstruction(app.all_pruefungen[node_id].inst)
            pdevice.nodes[node_id].updatePassed(app.all_pruefungen[node_id].res)
        time.sleep(600)
        app.create_pruefung_items()
        
