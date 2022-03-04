'''

module name: backend.py
author:      Leon Diel

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

style.use('ggplot')

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(70)

state_boxes = array('I', [0, 0, 0, 0])

ON_OFF_TIME = [0, 0, 0, 0, 0]
ON_OFF_TIME_S = ['00:00:00', '00:00:00']
off_char = '00:00:00'

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


robot = serial.Serial('/dev/ttyACM0', 9600)
data = serial.Serial('/dev/ttyACM1', 115200, timeout=10)

class Config:
    
    def edit_positioning(position, booked, species):
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

    def get_state_boxes(eg, fst, snd, trd):
        state_boxes[0] = eg
        state_boxes[1] = fst
        state_boxes[2] = snd
        state_boxes[3] = trd
        print(state_boxes)
    
    def write_time_list(on_h, on_m, off_h, off_m, value):
        ON_OFF_TIME[0] = on_h
        ON_OFF_TIME[1] = on_m
        ON_OFF_TIME[2] = off_h
        ON_OFF_TIME[3] = off_m
        ON_OFF_TIME[4] = value
        
        ON_OFF_TIME_S[0] = str(on_h)+':'+str(on_m)+':00'
        ON_OFF_TIME_S[1] = str(off_h)+':'+str(off_m)+':00'
        
        print(ON_OFF_TIME_S)
    
    def change_val_lights(value):
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
        localtime = time.localtime(time.time())
        
        year = localtime.tm_year
        month = localtime.tm_mon
        day = localtime.tm_mday
        
        hour = '%0.2d' %(localtime.tm_hour)
        minute = '%0.2d' %(localtime.tm_min)
        second = '%0.2d' %(localtime.tm_sec)
        
        return hour+':'+minute+':'+second
        
    def check_time():
        
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
        pwm.set_pwm(pin, 0, val)
    
    def stop_circulation(pin):
        pwm.set_pwm(pin, 0, 0)
        
    
class Control_Robot(Config):
    
    def read_serial():
        robot.flush()
        while True:            
            while robot.in_waiting > 0:
               line=robot.readline().decode('utf-8').rstrip()
               print(line)

    
    def relocate(old, new):
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
    
f = Figure(figsize=(8,4), dpi=90)
a = f.add_subplot(111)

lev = Figure(figsize=(8,4), dpi=90)
lev_sub = lev.add_subplot(111)

pH_plot = Figure(figsize=(8,4), dpi=90)
pH_sub = pH_plot.add_subplot(111)
#pH_vol = pH_plot.add_subplot(111)

ec_plot = Figure(figsize=(8,4), dpi=90)
ec_sub = ec_plot.add_subplot(111)

header = False

class Visualization:
    
    def get_parameter(index):
        
        return str(VIAL_PARAMETERS[index])
    
    def get_vial_parameters():
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
        current_time = datetime.now()
        time = current_time.strftime("%m/%d/%Y; %H:%M:%S")
        if header == True:
            
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
        return f
    
    def plot_figure2():
        return lev
    
    def plot_figure_pH():
        return pH_plot
    
    def plot_figure_ec():
        return ec_plot
    
    def animate(i):
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
        ec_sub.plot(xList, yList_ec, label='EC')
        #ec_sub.set_ylim(0, 300)
        ec_sub.set_xlabel('Time')
        ec_sub.set_ylabel('TDS (ppm)')
        ec_sub.legend()

