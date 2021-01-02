# Podio2MQTT

This python program is intented to be run as service.

It then frequently (every 10 Minutes) polls the Podio API and publish the result on MQTT.

MQTT messages follow the [Homie Convention](https://homieiot.github.io/), so the available items are automatically detected by OpenHAB.

## Supported Podio Views

For now, only the "Prüfungen" App is supported. 

### Prüfungen

The following information is read from Podio:

* Name of "Prüfung" (String)
* Next Date (DateTime)
* Pre-warn time (Integer)
* Instructions (String (HTML))

Based on this a state ("Valid", "Expired", or "Due_Soon") is send as string

## Installation

Copy contents of src directoy to a directory of your choice and run it with python3.

## Configuration

Rename `podioconfig_example.py` to `podioconfig.py` and change data.
Podio App authentication is used, so you need no password, but an APP_ID and APP_KEY.
VIEW_ID is the Podio ID of the view of the items.

## systemd Service

To run as service, use the file in doc/systemd-service-example.

