#!/usr/bin/python3

'''
module name: farmer.py
author:      Leon Diel
last update: 2022/03/30

info:
    This module contains classes for executing threads. 
    User interface, serial communication between the microcontrollers as well as monitoring for time switching are started as parallel processes.
'''

import threading
import time
import gui
import backend

import serial

class GuiThread(threading.Thread):
    
    """
    class GuiThread inherits from the threading.Thread class and enables the GUI as a thread
        - __init__
        - run
    """

    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        print("Starting GUI...\nThread-ID: ", self.iD)
        gui.gui()
        
class ConsoleThread(threading.Thread):
    
    """
    class ConsoleThread inherits from the threading.Thread class and enables the serial backend operations as a thread
        - __init__
        - run
    """
    
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        read = backend.Control_Robot
        print("Reading Serial...\nThread-ID: ", self.iD)
        read.read_serial()
        

class BackEndThread(threading.Thread):   
    
    """
    class BackEndThread inherits from the threading.Thread class and enables the time coding as a thread
        - __init__
        - run
    """
    
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        print("Starting BackEnd...\nThread-ID: ", self.iD)
        backend_t = backend.Control_Parameters
        backend_t.check_time()
       
class MonitoringThread(threading.Thread):
    
    """
    class MonitoringThread inherits from the threading.Thread class and enables continuous collection of data as a thread
        - __init__
        - run
    """
    
    def __init__(self, iD, name):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name

    def run(self):
        parameters = backend.Visualization
        print("Reading parameters: ")
        parameters.get_vial_parameters()

def main():
    """
    main()
        - creating objects of the classes listed above
        - starting the threads
    """
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
