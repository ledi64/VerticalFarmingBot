#!/usr/bin/python3

'''
module name: farmer.py
author:      Leon Diel
date:        2021/09/21
'''

import threading
#from tkinter import *
import RPi.GPIO
import time
import gui
import backend

import serial

dig_time = ''

class GuiThread(threading.Thread):
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        print("Starting GUI...\nThread-ID: ", self.iD)
        gui.gui()
        
class ConsoleThread(threading.Thread):
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        read = backend.Control_Robot
        print("Reading Serial...\nThread-ID: ", self.iD)
        read.read_serial()
        

class BackEndThread(threading.Thread):   
    
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        print("Starting BackEnd...\nThread-ID: ", self.iD)
        backend_t = backend.Control_Parameters
        backend_t.check_time()
       
class MonitoringThread(threading.Thread):
    
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        parameters = backend.Visualization
        print("Reading parameters: ")
        parameters.get_vial_parameters()
#         global dig_time
#         newtime = time.strftime('%H:%M:%S')
#         if newtime != dig_time:
#             dig_time = newtime
#             gui.dig_time(newtime)
#             print(newtime)

def main():
    
    console_thread = ConsoleThread(1, "Console Thread")  
    gui_thread = GuiThread(2, "Gui Thread")
    backend_thread = BackEndThread(3, "BackEnd Thread")
    monitoring = MonitoringThread(4, "Monitoring Thread")
    
    console_thread.start()
    gui_thread.start()
    backend_thread.start()
    monitoring.start()

if __name__ == '__main__':
    main()
