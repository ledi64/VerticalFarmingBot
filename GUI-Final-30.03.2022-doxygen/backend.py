'''
module name: backend.py
author:      Leon Diel
last update: 2022/03/30

info:
    This module includes classes for controlling the robot, communicating with microcontrollers, visualizing live graphs, and controlling cultivation parameters.
'''

#from tkinter import *
import time
from datetime import datetime
import Adafruit_PCA9685
from array import array
import serial

import csv
import json

import matplotlib
import matplotlib.animation as animation
from matplotlib import style
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

""" activate style for live plots """
style.use('ggplot')

""" 
    create instance of the class
    set pwm frequency to 70 Hz
"""
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(70)

""" array for the light control checkboxes """
state_boxes = array('I', [0, 0, 0, 0])

""" 
    array for saving the inputs collected from the option menues 
    index 0: on time hour
    index 1: on time minute
    index 2: off time hour
    index 3: off time minute
    index 4: value
"""
ON_OFF_TIME = [0, 0, 0, 0, 0]

""" 
    array for saving the inputs from the option menues as a time-shaped string
    index 0: on time
    index 1: off time
"""
ON_OFF_TIME_S = ['00:00:00', '00:00:00']
off_char = '00:00:00'

""" array for saving the data sent by the monitoring arduino """

VIAL_PARAMETERS = [0,  # index 0: temp air
                   0,  # index 1: watertemp tank
                   0,  # index 2: waterlevel tank
                   0,  # index 3: waterlevel floor 1
                   0,  # index 4: waterlevel floor 2
                   0,  # index 5: humidity floor 1
                   0,  # index 6: humidity floor 2
                   0,  # index 7: humidity raisin
                   0,  # index 8: pH tank
                   0,  # index 9: ec tank
                   0]  # index 10: time

""" 
    creating the instances for the serial communication
    robot >> robot arduino
    data >> monitoring arduino
"""
robot = serial.Serial('/dev/ttyACM0', 9600)
data = serial.Serial('/dev/ttyACM1', 115200, timeout=10)


class Config:
    
    """ 
    class Config contains functions for working with the booking system
        - edit_positioning
        - switch_position
        - check_booking
        - return_booking_state
    """
    
    def edit_positioning(position, booked, species):
        """
        edit_positioning(position, booked, species)
            - edits the different parameters of the 'positioning.json' file
        transfer parameters:
            position:   int, position in the cultivation system
            booked:     boolean, state of booking (True or False)
            species:    string, species of the cultivated plant
        """
        print("Editing data")
        
        if (species == "None"):
            species = None
        
        #Edit data
        new_data = []

        with open('positioning.json', 'r') as file:
            data_temp = json.load(file)
        i=0
        for edit in data_temp:
            if (i == int(position)):
                position_ = edit["position"]
                booked_ = edit["booked"]
                species_ = edit["species"]

                print(f"Current Position : {position_}")
                print(f"Current booking state : {booked_}")
                print(f"Current species : {species_}")
                new_data.append({"position": position, "booked": booked, "species": species})
                i=i+1
            else:
                new_data.append(edit)
                i=i+1

        with open('positioning.json', 'w') as file:
            json.dump(new_data, file, indent=4)
        
        print("File 'positioning.json' successfully updated.")
    
    
    def switch_position(old, new):
        """
        switch_position(old, new)
            - exchanges the information in case of displacement of a planting
            - information of the initial position is moved to the target position and then reset
        transfer parameters:
            old: int, initial position
            new: int, target position
        """
        
        data_old = [0, 0, 0]
        data_reset = [old, False, None]
        
        # Check and save old data
        i=0
        with open('positioning.json', 'r') as file:
            data = json.load(file)
        
        for view in data:
            if (i == int(old)):
                data_old[0] = view["position"]
                data_old[1] = view["booked"]
                data_old[2] = view["species"]
                i=i+1
            else:
                i=i+1
        print(data_old)
        
        # Overwrite new position
        Config.edit_positioning(new, data_old[1], data_old[2])
        
        # Clear old position
        Config.edit_positioning(data_reset[0], data_reset[1], data_reset[2])
        
        print("Editing File successful.")
        print("Old data: ")
        print(data_old)
        print("\n")
        print("Cleared old data: ")
        print(data_reset)
        print("\n")
        print("New data: ")
    
    
    def check_booking(pos):
        """
        check_booking(pos)
            - checks the booking of a position
            - provides the stored information about booking status and plant type
        transfer parameters:
            pos: int, position to be checked
        return parameter:
            label_string: string, Label string for printing the information on the UI
        """
        
        print(f"Checking Booking position: {pos}")
        i=0
        with open('positioning.json', 'r') as file:
            data = json.load(file)
        
        for view in data:
            if (i == int(pos)):
                position = view["position"]
                booked = view["booked"]
                species = view["species"]
                
                if (species == None):
                    label_string = "Requested position: " + str(position) + ",\n" + "booking state: " + str(booked) + ",\n" + "no cultivated species"
                    print(label_string)
                    return label_string
                else:
                    label_string = "Requested position: " + str(position) + ",\n" + "booking state: " + str(booked) + ",\n" + "cultivated species: " + str(species)
                    print(label_string)
                    return label_string
            else:
                i=i+1
    
    
    def return_booking_state(pos):
        """
        return_booking_state(pos)
            - checks the booking status of a position and returns it
            - is called in the course of a relocation
        transfer parameters:
            pos: int, position to be checked
        return parameter:
            booked: boolean, state of booking
        """
        
        print(f"Checking Booking position: {pos}")
        i=0
        with open('positioning.json', 'r') as file:
            data = json.load(file)
        
        for view in data:
            if (i == int(pos)):
                #position = view["position"]
                booked = view["booked"]
                #species = view["species"]
                return booked
            else:
                i=i+1


class Control_Parameters:
    """ 
    class Control_Parameters contains functions for editing cultivation parameters
        - get_state_boxes
        - write_time_list
        - change_val_lights
        - change_val_pump
        - change_val_nutrients
        - reset_pwm_channels
        - get_current_time
        - check_time
        - start_circulation
        - stop_circulation
    """
    
    def get_state_boxes(eg, fst, snd, trd): 
        """
        get_state_boxes(eg, fst, snd, trd)
            - updates the state_boxes array
            - prints the array
        transfer parameters:
            eg:  int, state for the ground floor box
            fst: int, state for the first floor box
            snd: int, state for the second floor box
            trd: int, state for the third floor box
        """
        state_boxes[0] = eg
        state_boxes[1] = fst
        state_boxes[2] = snd
        state_boxes[3] = trd
        print(state_boxes)
    
    
    def write_time_list(on_h, on_m, off_h, off_m, value):
        """
        write_time_list(on_h, on_m, off_h, off_m, value)
            - updates the ON_OFF_TIME and ON_OFF_TIME_S arrays with the parameters chosen from the option menues
            - print the ON_OFF_TIME_S array
        transfer parameters:
            on_h:   int, on time hour
            on_m:   int, on time minute
            off_h:  int, off time hour
            off_m:  int, off time minute
            value:  int, pwm value between 0 and 4095
        """
        ON_OFF_TIME[0] = on_h
        ON_OFF_TIME[1] = on_m
        ON_OFF_TIME[2] = off_h
        ON_OFF_TIME[3] = off_m
        ON_OFF_TIME[4] = value
        
        ON_OFF_TIME_S[0] = str(on_h)+':'+str(on_m)+':00'
        ON_OFF_TIME_S[1] = str(off_h)+':'+str(off_m)+':00'
        
        print(ON_OFF_TIME_S)
    
    
    def change_val_lights(value):
        """
        change_val_lights(value)
            - changes the pwm value for the lights depending on the state of the checkboxes
        transfer parameters:
            value: int, pwm value between 0 and 4095
        """
        
        print(value)
        if (value == 0):
            real_eg = 0
            real_fst = 0
            real_snd = 0
            real_trd = 0
        else:
            dez_val = (1 / value) * 100
            print(dez_val)
            
            real_eg = (4095 / dez_val)
            real_fst = (4095 / dez_val)
            real_snd = (4095 / dez_val)
            real_trd = (4095 / dez_val)
        
        if (state_boxes[0] == 1):
            pwm.set_pwm(1, 0, int(real_eg))
            print("PWM Setted (EG). Value: ")
            print(int(real_eg))
            
        if (state_boxes[1] == 1):
            pwm.set_pwm(4, 0, int(real_fst))
            print("PWM Setted (1). Value: ")
            print(int(real_fst))
        
        if (state_boxes[2] == 1):
            pwm.set_pwm(5, 0, int(real_snd))
            print("PWM Setted (2). Value: ")
            print(int(real_snd))
            
        if (state_boxes[3] == 1):
            pwm.set_pwm(8, 0, int(real_trd))
            print("PWM Setted (3). Value: ")
            print(int(real_trd))

    
    def change_val_pump(value):
        """
        change_val_pump(value)
            - changes the pwm value of the water-pump
        transfer parameters:
            value: int, pwm value between 0 and 4095
        """
        
        print(value)
        if (value == 0):
            pwm.set_pwm(9, 0, value)
        else:
            dez_val = (1 / value) * 100
            print(dez_val)
            real_val = (4095 / dez_val)
            pwm.set_pwm(9, 0, int(real_val))
            print("PWM Setted (9). Value: ")
            print(int(real_val))
    
    def change_val_nutrients(value):
        """
        change_val_nutrients(value)
            - changes the pwm value of the nutrients pump
        transfer parameters:
            value: int, pwm value between 0 and 4095
        """
        
        print(value)
        if (value == 0):
            pwm.set_pwm(1, 0, value)
        else:
            dez_val = (1 / value) * 100
            print(dez_val)
            real_val = (4095 / dez_val)
            pwm.set_pwm(1, 0, int(real_val))
            print("PWM Setted (1). Value: ")
            print(int(real_val))
    
    def reset_pwm_channels():
        """
        reset_pwm_channels
            - resets all pwm channels
        """
        
        channel = 0
        print("Resetting PWM Channels...")
        time.sleep(.25)

        while channel < 16:
            print("Channel:", channel)
            pwm.set_pwm(channel, 0, 0)
            channel = channel + 1
            time.sleep(.1)

        print("PWM-Channels resetted.")
        time.sleep(1)
    
    def get_current_time():
        """
        get_current_time()
            - requests the current system time and returns it as a string
        return parameter:
            hour+':'+minute+':'+second : string, composite time
        """
        
        localtime = time.localtime(time.time())
        
        year = localtime.tm_year
        month = localtime.tm_mon
        day = localtime.tm_mday
        
        hour = '%0.2d' %(localtime.tm_hour)
        minute = '%0.2d' %(localtime.tm_min)
        second = '%0.2d' %(localtime.tm_sec)
        
        return hour+':'+minute+':'+second

    def check_time():
        """
        check_time()
            - checks the current time and compares it with the ON_OFF_TIME_S Array
            - if the value matches with the on time, the lights will turned on
            - if the value matches with the off time, the lights will turned off
        """
        
        while True:
            time_ = Control_Parameters
            time_now = time_.get_current_time()
            
            if time_now == ON_OFF_TIME_S[0] :
                #cmd = get_on_off(ON_OFF_TIME_S.index(time_now))
                #print(str(cmd))
                print("LIGHTS ON")
                time_.change_val_lights(ON_OFF_TIME[4])
            
            if time_now == ON_OFF_TIME_S[1]:    
                print("LIGHTS ON")
                time_.change_val_lights(0)
            
            if ((ON_OFF_TIME_S[0] == off_char) and (ON_OFF_TIME_S[1] == off_char)):
                #print("00:00:00 - Manuelle Steuerung");
                time_.change_val_lights(ON_OFF_TIME[4])
            
            #print(time_now)
            time.sleep(1)

    def start_circulation(pin, val):
        """
        start_circulation(pin, val)
            - starts a circulation fan independend from the time
        transfer parameters:
            pin: int, input pin
            val: int, pwm value between 0 and 4095
        """
        
        pwm.set_pwm(pin, 0, val)
    
    def stop_circulation(pin):
        """
        stop_circulation(pin)
            - stops a circulation fan independend from the time
        transfer parameters:
            pin: int, input pin
        """
        
        pwm.set_pwm(pin, 0, 0)

class Control_Robot(Config):
    """ 
    class Control_Robot(Config) contains the functions to interact with the robot via serial
        - read_serial
        - relocate
    """
    
    def read_serial():
        """
        read_serial()
            - reads the serial buffer
            - prints the delivered messages
        """
        
        robot.flush()
        while True:            
            while robot.in_waiting > 0:
               line=robot.readline().decode('utf-8').rstrip()
               print(line)

    def relocate(old, new):
        """
        relocate(old, new)
            - checks whether a relocation is possible with the transferring positions. 
                - if yes:
                    - sends the relocation command with initial and target positions to the robot
                    - calls the switch_position function for changing the booking system
                - if not:
                    - print out the error message including the detected problem
        transfer parameters:
            old: int, initial position
            new: new, target position
        """
        
        robot.flush()
        
        if ((Config.return_booking_state(old) == True) and (Config.return_booking_state(new) == False)):
            print("Relocate")
            print(old + 'T' + new)
            
            command = old + 'T' + new
            end_line = "\n"
            
            msg = command.encode()
            
            print("Sending message to the robot...")
            print(msg)
            robot.write(msg)
            robot.write(end_line.encode())
            
            while robot.in_waiting != 0:
                line=robot.readline().decode('utf-8').rstrip()
                print(line)
                
                if (line=="Success"):
                    print("Success. You can now send a new command.")
                    robot.flush()
                #    return
            robot.flush()
            
            Config.switch_position(old, new)
            
            print("Finished.")
            #return 0
        elif (Config.return_booking_state(old) == False):
            print("Position " + old + " currently has no plant.")
            print("Please check or update the position booking.")
            
        elif((Config.return_booking_state(old) == False) and (Config.return_booking_state(new) == True)):
            print("There is currently a plant in position " + new)
            print("Please check or update the position booking.")
            
        elif((Config.return_booking_state(old) == True) and (Config.return_booking_state(new) == True)):
            print("There are currently plants in both positions.")
            print("Please check or update the position booking.")
        else:
            print("Something failed by calling the relocate function.")
            print("Please check your intype or update the position booking.")

""" 
    Creating figures and subplots to online visualize the data
        - f and a to plot the temperature
        - lev and lev_sub to plot the waterlevel
        - pH_plot and pH_sub to plot the pH
        - ec_plot and ec_sub to plot the TDS value (called it ec because it was planned to monitor ec first)
"""
f = Figure(figsize=(8,4), dpi=90)
a = f.add_subplot(111)

lev = Figure(figsize=(8,4), dpi=90)
lev_sub = lev.add_subplot(111)

pH_plot = Figure(figsize=(8,4), dpi=90)
pH_sub = pH_plot.add_subplot(111)
#pH_vol = pH_plot.add_subplot(111)

ec_plot = Figure(figsize=(8,4), dpi=90)
ec_sub = ec_plot.add_subplot(111)

""" boolean var for saving the data to an csv file but do not overwrite the first line """
header = False


class Visualization:
    """ 
    class Visualization contains the functions to get, write and visualize data
        - get_parameter
        - get_vial_parameters
        - save_log_file
        - save_data
        - plot_figure
        - plot_figure2
        - plot_figure_pH
        - plot_figure_ec
        - animate
        - animate2
        - animate_pH
        - animate_ec
    """
    
    def get_parameter(index):
        """
        get_parameter(index)
            - returns the data saved in the VIAL_PARAMETERS array as a string on position on the requested index
        transfer parameter:
            index: int, index for the VIAL_PARAMETERS array
        return parameter:
            str(VIAL_PARAMETERS[index]): int converted to a string, vial parameter saved on the index
        """
        return str(VIAL_PARAMETERS[index])
    
    def get_vial_parameters():
        """
        get_vial_parameters()
            - receives the measured data from the monitoring arduino
            - saves the data into the respective text file bond to the current time by calling the save_data function
        """
        
        data.flush()
        while True:
            msg = ''
            while data.in_waiting > 0:
                i = 0
                time.sleep(0.2)
                while i < 10:
                    line = data.readline().decode('utf-8').rstrip()
                    VIAL_PARAMETERS[i] = round(float(line), 2)
                    time.sleep(0.1)
                    i = i + 1
                VIAL_PARAMETERS[10] = Control_Parameters.get_current_time()
                data.flush()
                i = 0
                
                Visualization.save_data(0, 'air_tmp.txt')
                Visualization.save_data(1, 'water_tmp.txt')
                Visualization.save_data(2, 'level_T.txt')
                Visualization.save_data(3, 'level_1.txt')
                Visualization.save_data(4, 'level_2.txt')
                Visualization.save_data(7, 'pH_voltage.txt')
                Visualization.save_data(8, 'pH.txt')
                Visualization.save_data(9, 'EC.txt')
                #Visualization.save_log_file()
    
    def save_log_file():
        """
        save_log_file()
            - saves the VIAL_PARAMETERS data to a csv file for long-term monitoring
        """
        
        current_time = datetime.now()
        time = current_time.strftime("%m/%d/%Y; %H:%M:%S")
        if header == False:
            
            with open('monitoringlog.csv', 'w', newline='') as write_obj:
                write_obj = csv.writer(write_obj, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                write_obj.writerow(["date; time", "air temperature", "water temperature", "level tank", "level 1", "level 2", "humidity", "pH voltage", "pH", "tds"])
                header == True
            
        with open('monitoringlog.csv', 'a+', newline='') as write_obj:
            write_obj = csv.writer(write_obj, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            write_obj.writerow([time,
                                VIAL_PARAMETERS[0],
                                VIAL_PARAMETERS[1],
                                VIAL_PARAMETERS[2],
                                VIAL_PARAMETERS[3],
                                VIAL_PARAMETERS[4],
                                VIAL_PARAMETERS[5],
                                VIAL_PARAMETERS[7],
                                VIAL_PARAMETERS[8],
                                VIAL_PARAMETERS[9] ])
        print(time)
        print("Monitoring log-file updated.")

    def save_data(index, filename):
        """
        save_data(index, filename)
            - saves the measured value from the VIAL_PARAMETERS array at the position index into the respective text file
            - if there are more than 8 values the first will be overwritten by the second value, the last
              value will be attached at the end
        transfer parameters:
            index:    int, index for the VIAL_PARAMETERS array
            filename: string, name of the specific text file to store the data
        """
        
        num_lines = sum(1 for line in open(filename))
        
        if num_lines >= 8:
            outfile = open(filename, 'r+')
            lines = outfile.readlines()
            outfile.seek(0)
            outfile.truncate()
            outfile.writelines(lines[1:])
            outfile.close()
            
        outfile = open(filename, 'a')
        outfile.write(str(VIAL_PARAMETERS[10]))
        outfile.write(";")
        outfile.write(str(VIAL_PARAMETERS[index]) + '\n')
        
        outfile.close()
    
    def plot_figure():
        """
        plot_figure() returns the plot of the temperature
        return parameter:
            f: object, plot
        """
        
        return f
    
    def plot_figure2():
        """
        plot_figure2() returns the plot of the waterlevel
        return parameter:
            lev: object, plot
        """
        
        return lev
    
    def plot_figure_pH():
        """
        plot_figure_pH() returns the plot of the pH
        return parameter:
            pH_plot: object, plot
        """
        
        return pH_plot
    
    def plot_figure_ec():
        """
        plot_figure_ec() returns the plot of the TDS
        return parameter:
            ec_plot: object, plot
        """
        
        return ec_plot
    
    def animate(i):
        """
        animate(i)
            - animates the temperature plot
            - updates the plot by get called in the gui
        transfer parameters:
            i: ?
        """
        
        data_watertmp = open('water_tmp.txt', 'r').read()
        data_airtmp = open('air_tmp.txt', 'r').read()
        dataList_watertmp = data_watertmp.split('\n')
        dataList_airtmp = data_airtmp.split('\n')
        
        xList1 = []
        xList2 = []
        yList_watertmp = []
        yList_airtmp = []
        
        for eachLine in dataList_watertmp:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList1.append(str(x))
                yList_watertmp.append(round(float(y), 1))
        
        for eachLine in dataList_airtmp:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList2.append(str(x))
                yList_airtmp.append(round(float(y), 1))
        
        a.clear()
        a.plot(xList1, yList_watertmp, label='water temperature tank')
        a.plot(xList2, yList_airtmp, label='air temperature')
        a.set_ylim(15, 25)
        a.set_xlabel('Time')
        a.set_ylabel('Degree (°C)')
        a.legend()
    
    def animate2(i):
        """
        animate2(i)
            - animates the waterlevel plot
            - updates the plot by get called in the gui
        transfer parameters:
            i: ?
        """
        
        data_waterlevelT = open('level_T.txt', 'r').read()
        data_waterlevel1 = open('level_1.txt', 'r').read()
        data_waterlevel2 = open('level_2.txt', 'r').read()
        
        dataList_levelT = data_waterlevelT.split('\n')
        dataList_level1 = data_waterlevel1.split('\n')
        dataList_level2 = data_waterlevel2.split('\n')
        
        xList1 = []
        xList2 = []
        xList3 = []
        yList_T = []
        yList_1 = []
        yList_2 = []
        
        for eachLine in dataList_levelT:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList1.append(str(x))
                yList_T.append(float(y))
        
        for eachLine in dataList_level1:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList2.append(str(x))
                yList_1.append(float(y))
        
        for eachLine in dataList_level2:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList3.append(str(x))
                yList_2.append(float(y))
        
        lev_sub.clear()
        lev_sub.plot(xList1, yList_T, label='level tank')
        lev_sub.plot(xList2, yList_1, label='level floor 1')
        lev_sub.plot(xList3, yList_2, label='level floor 2')
        #lev_sub.set_ylim(0, 300)
        lev_sub.set_xlabel('Time')
        lev_sub.set_ylabel('Waterlevel')
        lev_sub.legend()
    
    def animate_pH(i):
        """
        animate_pH(i)
            - animates the pH plot
            - updates the plot by get called in the gui
        transfer parameters:
            i: ?
        """
        
        data_ph = open('pH.txt', 'r').read()
        dataList_ph = data_ph.split('\n')
        
        #data_voltage = open('pH_voltage.txt', 'r').read()
        #dataList_voltage = data_voltage.split('\n')
        
        xList1 = []
        #xList2 = []
        yList_ph = []
        #yList_voltage = []
        
        for eachLine in dataList_ph:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList1.append(str(x))
                yList_ph.append(float(y))
        
        #for eachLine in dataList_voltage:
         #   if len(eachLine) > 1:
          #      x, y = eachLine.split(';')
           #     xList2.append(str(x))
            #    yList_voltage.append(float(y))
        
        pH_sub.clear()
        pH_sub.plot(xList1, yList_ph, label='pH')
        pH_sub.set_ylim(5, 8.5)
        pH_sub.set_xlabel('Time')
        pH_sub.set_ylabel('pH-Value')
        pH_sub.legend()
        
        #pH_vol = pH_sub.twinx()
        #pH_vol.clear()
        #pH_vol.plot(xList2, yList_voltage, label='voltage')
        #pH_vol.set_ylabel('voltage (mV)')
        #pH_vol.legend()
    
    def animate_ec(i):
        """
        animate_ec(i)
            - animates the TDS plot
            - updates the plot by get called in the gui
        transfer parameters:
            i: ?
        """
        
        data_ec = open('EC.txt', 'r').read()
        dataList_ec = data_ec.split('\n')
        
        xList = []
        yList_ec = []
        
        for eachLine in dataList_ec:
            if len(eachLine) > 1:
                x, y = eachLine.split(';')
                xList.append(str(x))
                yList_ec.append(float(y))
        
        ec_sub.clear()
        ec_sub.plot(xList, yList_ec, label='TDS')
        #ec_sub.set_ylim(0, 300)
        ec_sub.set_xlabel('Time')
        ec_sub.set_ylabel('TDS (ppm)')
        ec_sub.legend()

