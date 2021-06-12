#!/usr/bin/python3
'''
Created on 30.12.2020

@author: ian
'''
from PodioDevice import Device_Podio
from NodeCheckInterval import NodeCheckInterval
import time

from pypodio2 import api

from podioconfig import PODIO_CONFIG as cfg, MQTT_CONFIG as mqtt_cfg

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
        self.c = api.OAuthAppClient(cfg['CLIENT_ID'], cfg['CLIENT_KEY'], cfg['APP_ID'], cfg['APP_KEY'])        
        
    def create_pruefung_items(self):
        self.all_pruefungen = {}
        fitems = self.c.Item.filter_by_view(cfg['APP_ID'], cfg['VIEW_ID'])
        for pruef in fitems['items']:  # iterate over items
            nextp = None
            desc = None
            obj = None   
            preWarning = None
            result = None
            app_item_id = pruef['app_item_id']
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
                    
            node_id = f"pruefung{app_item_id:02d}"
            newp = Pruefung(node_id, nextp, obj, preWarning, result, desc)
            self.all_pruefungen[node_id] = newp

if __name__ == '__main__':
    
    pdevice = Device_Podio(mqtt_settings=mqtt_cfg)
    
    app = PodioPruefungApp()
    app.create_pruefung_items()
    print(app.all_pruefungen)
        
    for pruef_id in app.all_pruefungen:        
        pdevice.add_node(NodeCheckInterval(pdevice, pruef_id, pruef_id))
        
    pdevice.start()
    
    while True:
        remove_nodes = []
        for node_id in pdevice.nodes:
            print(node_id)            
            try:
                pdevice.nodes[node_id].updatePreWarning(app.all_pruefungen[node_id].prew)
            except KeyError:
                print(f"Prüfung {node_id} deleted.")
                remove_nodes.append(node_id)
                continue
            pdevice.nodes[node_id].updateNextCheck(app.all_pruefungen[node_id].next_date)
            pdevice.nodes[node_id].updateDescription(app.all_pruefungen[node_id].desc)
            pdevice.nodes[node_id].updateInstruction(app.all_pruefungen[node_id].inst)
            pdevice.nodes[node_id].updatePassed(app.all_pruefungen[node_id].res)
        
        for node_id in remove_nodes: pdevice.remove_node(node_id)
        time.sleep(600)
        app.create_pruefung_items()
        for pruef_id in app.all_pruefungen:
            if not pruef_id in pdevice.nodes:
                print(f"Prüfung {pruef_id} added")
                pdevice.add_node(NodeCheckInterval(pdevice, pruef_id, pruef_id)
)
                
        
