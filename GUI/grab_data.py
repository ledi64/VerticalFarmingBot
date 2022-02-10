'''

module name: grab_data.py
author:      Leon Diel

'''

from tkinter import *
import time
import con_window
import backend
import gui
import json

# Enthält Daten für Positionen
POSITION = [0,   # latest floor
            0,   # latest pos
            0,   # new floor
            0]   # new pos

# Array für Aktualisierung
POS = [
      [0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0]
]

# Array für Belegung:
# 0 = frei
# 1 = belegt
# 2 = nicht verfügbar
BOOKING = [
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0]
]

# Enthält Einstellungen für den Timecode
TIME_CODE = [0,   # latest light start h
             0,   # latest light start m
             0,   # latest light end h
             0,   # latest light end m
             0]   # value
# Funktion lädt letzte gespeicherte Position für die GUI
def load_pos():
    with open('pos.json', 'r') as file:
        POSI = json.loads(file.read())
        POSITION[0] = POSI[0]
        POSITION[1] = POSI[1]
        POSITION[2] = POSI[2]
        POSITION[3] = POSI[3]

def update_pos(new_floor, new_pos):
    # Update POS Array
    print("This is the call of 'update_pos'.")

# Anzeige GUI letzte Position
def floor_pos():
    floor = POSITION[0]
    pos = POSITION[1]
    pos_str = str(floor) + "-" + str(pos)
    return pos_str

# zu speichernder Positions-Array
def position(curr_floor, curr_pos, new_floor, new_pos):
    
    print("Current Position:", curr_floor, "floor, position", curr_pos)
    
    # Änderungen in Array schreiben
    POSITION[0] = curr_floor
    POSITION[1] = curr_pos
    POSITION[2] = new_floor
    POSITION[3] = new_pos
    print("I updated the position to:", new_floor, "floor, position", new_pos)
    
    # Position anfahren
    
    # Positionen speichern
    json.dump(POSITION, open('pos.json', 'w'))
    print("Positions were saved in 'pos.json'.")
    
def position_booking(floor, pos, booking_opt):
    status = 0
    if (booking_opt == "belegt"):
        status = 1
    elif (booking_opt == "n.v."):
        status = 2
    else:
        status = 0
    
    print("Your booking:")
    print("   Floor:    ", floor)
    print("   Position: ", pos)
    print("   Status:   ", booking_opt)
    
    # Array Updaten
    BOOKING[floor][(pos-1)] = status
    
    # Datei updaten
    json.dump(BOOKING, open('booking.json','w'))
    print("I saved your new booking settings in the file 'booking.json.")

# Holt sich Daten aus den Arrays der OptionMenues und aus dem Entryfeld der GUI unter Light Timecode und speichert die zuletzt gewählten Einstellungen in einer Datei.
def light_grab(start_hours, start_min, end_hours, end_min, value):
    
    value_pro = (value/4096)*100
    
    print("I got this from your Entry...")
    print("start time: ", start_hours, ":", start_min)
    print("end time:   ", end_hours, ":", end_min)
    print("intensity:  ", value, "/ 4095 (", round(value_pro, 2), "% )")
    
    # In array TIME_CODE schreiben
    TIME_CODE[0] = start_hours
    TIME_CODE[1] = start_min
    TIME_CODE[2] = end_hours
    TIME_CODE[3] = end_min
    TIME_CODE[4] = value
    
    # neu speichern
    json.dump(TIME_CODE, open('settings_tc.json','w'))
    print("I saved your new timecode settings in the file 'settings_tc.json.")
    
    # und anwenden (Backendfunktion aufrufen)
    # ...
    
    '''
    with open('settings_tc.json', 'r') as file:
        obj = json.loads(file.read())
        print(obj)
    ''' 
