'''

module name: con_window.py
author:      Leon Diel

'''

from tkinter import *
import time
import gui

def window():
    
    console_window = Tk()
    console_window.wm_title("Konsole")
    console_window.config(background="#A4A4A4", height=300, width = 500)
    
    console_window.mainloop()