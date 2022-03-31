'''
module name: gui.py
author:      Leon Diel
last update: 2022/03/30

info:
    This module allows the creation of a user interface to control the robot and cultivation system via the gui() function. 
    Through this UI, commands can be sent to the robot, timings and cultivation parameters can be adjusted and live graphs of measured data such as pH or temperature can be displayed.
'''

from tkinter import *
from tkinter import ttk
import time
import backend
from picamera import PiCamera
import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Array of Main Timecode
CH_S_H = [
    """
    CH_S_H:
        - data type: array 
        - data included: strings
        - info: 
            - includes the hours for the option menus for the start time of the user interface
            - 24 indices
    """
    '00', '01', '02', '03', '04', 
    '05', '06', '07', '08', '09', 
    '10', '11', '12', '13', '14', 
    '15', '16', '17', '18', '19', 
    '20', '21', '22', '23'
]

CH_E_H = [
    """
    CH_E_H:
        - data type: array 
        - data included: strings
        - info: 
            - includes the hours for the option menus for the stop time of the user interface
            - 24 indices
    """
    '00', '01', '02', '03', '04', 
    '05', '06', '07', '08', '09', 
    '10', '11', '12', '13', '14', 
    '15', '16', '17', '18', '19', 
    '20', '21', '22', '23'
]

CH_S_M = [
    """
    CH_S_M:
        - data type: array 
        - data included: strings
        - info: 
            - includes the minutes for the option menus for the start time of the user interface
            - 12 indices
    """
    '00', '05', '10', '15', 
    '20', '25', '30', '35', 
    '40', '45', '50', '55'
]

CH_E_M = [
    """
    CH_E_M:
        - data type: array 
        - data included: strings
        - info: 
            - includes the minutes for the option menus for the stop time of the user interface
            - 12 indices
    """
    '00', '05', '10', '15', 
    '20', '25', '30', '35', 
    '40', '45', '50', '55'
]

POSITIONS = [
    """
    POSITIONS:
        - data type: array 
        - data included: integers
        - info: 
            - includes the positions for the option menus for updating the booking system
            - 24 indices
    """
    0, 1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11,
    12, 13, 14, 15,
    16, 17, 18, 19,
    20, 21, 22, 23
]

POSITIONS2 = [
    """
    POSITIONS2:
        - data type: array 
        - data included: integers
        - info: 
            - includes the positions for the option menus for checking the booking system
            - 24 indices
    """
    0, 1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11,
    12, 13, 14, 15,
    16, 17, 18, 19,
    20, 21, 22, 23
]

BOOKING_STATE = [
    """
    BOOKING_STATE:
        - data type: array 
        - data included: boolean vars
        - info: 
            - includes the two states for the option menus for updating the booking system
            - 2 indices
    """
    True,
    False
]

SPECIES = [
    """
    SPECIES:
        - data type: array 
        - data included: strings
        - info: 
            - includes the available plant species for the option menus for updating the booking system
            - 8 indices
    """
           "None",
           "Arugula",
           "Basil",
           "Cress",
           "Crispilla Amarilla",
           "Field salat",
           "Grand Rapids",
           "Maravilla Verano"
]

# Darkmode #585858
# Lightmode #D8D8D8
# Hell #A4A4A4

#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.preview_window=(48, 105, 800, 720)
#camera.rotation = 180
#camera.framerate = 30

control_p = backend.Control_Parameters
control_robot = backend.Control_Robot
data_m = backend.Visualization
    
def capture():
    #camera.start_preview()
    print("Start cam.")

def exit_capture():
    #camera.stop_preview()
    print("Stop cam.")
    
def dig_time(curr_time):
    while True:
        return curr_time

def gui():
    """
    gui():
        - function for creating the user interface
        - called in the farmer.py as a thread
        - UI is interacting with the backend
    """
    
    
    root = Tk()
    root.wm_title("Vertical-Farming-Bot")
    root.config(bg="#FFFFFF")
    #root.geometry("1920x1000")
    win_icon = PhotoImage(file="Icons/tea-plant-leaf-icon.png")
    root.iconphoto(False, win_icon)
    
    # other Vars
    var_scale_irrigation = IntVar()
    var_scale_lights = IntVar()
    var_scale_nutrients = IntVar()
    
    state_light_raisin = IntVar()
    state_light_second = IntVar()
    state_light_first = IntVar()
    state_light_eg = IntVar()
    
    # Var Optionmenu
    Light_start_h = StringVar(root)
    Light_start_h.set(CH_S_H[0])
    Light_start_m = StringVar(root)
    Light_start_m.set(CH_S_M[0])
    Light_end_h = StringVar(root)
    Light_end_h.set(CH_E_H[0])
    Light_end_m = StringVar(root)
    Light_end_m.set(CH_E_M[0])
    
    Position_list = IntVar(root)
    Position_list.set(POSITIONS[0])
    
    Position_list_show = IntVar(root)
    Position_list_show.set(POSITIONS2[0])
    
    Booking_state_list = BooleanVar(root)
    Booking_state_list.set(BOOKING_STATE[0])
    
    Species_list = StringVar(root)
    Species_list.set(SPECIES[0])
    
    #light_box_var = IntVar()
    #floor_box_var = IntVar(root)
    #floor_box_var.set(FLOORS[0])
    
    #floor_booking_var = IntVar(root)
    #floor_booking_var.set(FLOOR_BOOKING[0])
    #pos_booking_var = IntVar(root)
    #pos_booking_var.set(POS_BOOKING[0])
    #state_booking_var = StringVar(root)
    #state_booking_var.set(STATE_BOOKING[0])
    
# REIHE 1
    # header - Bildimport
    header = Frame(root, background="#D8D8D8")
    header.grid(row=0, column=0)
    
    #header_img = PhotoImage(file="gui_header.png")
    #button_frame = Frame(header).grid(row=0, column=0, padx = 10, pady = 10)
    
    exit_img = PhotoImage(file="Icons/Programming-Delete-Sign-icon32p.png")
    settings_img = PhotoImage(file="Icons/Programming-Settings-3-icon32p.png")
    timecode_img = PhotoImage(file="Icons/Programming-Watch-icon32p.png")
    camera_img = PhotoImage(file="Icons/Photo-Video-Slr-Camera2-Filled-icon32p.png")
    #help_img = PhotoImage(file="Icons/Programming-Help-icon32p.png")
    reset_img = PhotoImage(file="Icons/Reload-2-2-icon32p.png")
    
    shutdown_b = Button(header, image=exit_img, height=32, width=32, background = "#D8D8D8", highlightthickness = 0, bd = 0, command=lambda:[print("Program will shut down..."),
                                                                                                                                             root.destroy()]).grid(row=0, column=0, pady=5, padx=5)
    settings_b = Button(header, image=settings_img, height=32, width=32, background = "#D8D8D8", highlightthickness = 0, bd = 0).grid(row=0, column=1, pady=5, padx=5)
    camera_b = Button(header, image=camera_img, height=32, width=32, background = "#D8D8D8", highlightthickness = 0, bd = 0, command=capture).grid(row=0, column=2, pady=5, padx=5)
    camera_exit_b = Button(header, image=camera_img, height=32, width=32, background = "#A30000", highlightthickness = 0, bd = 0, command=exit_capture).grid(row=0, column=3, pady=5, padx=5)
    reset_channels_b = Button(header, image=reset_img, height=32, width=32, background = "#D8D8D8", highlightthickness = 0, bd = 0, command=lambda:[control_p.reset_pwm_channels()]).grid(row=0, column=4, pady=5, padx=5)
    
    # Spacer
    spacer_header1 = Frame(header, height=100, width=357, background = "#D8D8D8")
    spacer_header1.grid(row=0, column=5)
    spacer_header2 = Frame(header, height=100, width=357, background = "#D8D8D8")
    spacer_header2.grid(row=0, column=6)
    spacer_header3 = Frame(header, height=100, width=356, background = "#D8D8D8")
    spacer_header3.grid(row=0, column=7)
    #spacer_header4 = Frame(header, height=100, width=312, background = "#D8D8D8")
    #spacer_header4.grid(row=0, column=8)
    
    frame_state = Frame(header, height=100, width=350, background = "#D8D8D8")
    frame_state.grid(row=0, column=9, padx=8)
    status_fix = Label(frame_state, text="Systemstatus: ", bg = "#D8D8D8", font=('Helvetica', 15, 'bold'))
    status_fix.grid(row=0, column=1)

    # Bereit mit "#40FF00"
    #status_ready = Label(frame_state, height=2, width=10, text="Bereit", bg="#40FF00", font=('Helvetica', 10))
    #status_ready.grid(row=1, column = 0, padx=2, pady=5)
    # In Aktion mit "#FACC2E"
    #status_wait = Label(frame_state, height=2, width=10, text="In Aktion", bg="#FACC2E", font=('Helvetica', 10))
    #status_wait.grid(row=1, column = 1, padx=2, pady=5)
    # Störung mit "#FF0000"
    #status_var = Label(frame_state, height=2, width=10, text="Störung", bg="#FF0000", font=('Helvetica', 10))
    #status_var.grid(row=1, column = 2, padx=2, pady=5)
    
# REIHE 2
    spacer_2_1 = Frame(root, background="#FFFFFF", pady=20, height=50)
    spacer_2_1.grid(row=1, column=0)
    
# REIHE 3
    row_3 = Frame(root, background="#FFFFFF")
    row_3.grid(row=2, column=0)
    
    # Monitoring
    monitoring_f = Frame(row_3, background="#FFFFFF")
    monitoring_f.grid(row=0, column=0, padx=10, pady=10)
    
    monitoring_frame_label = Label(monitoring_f, text="MONITORING", font=('Helvetica', 12), background="#FFFFFF")
    monitoring_frame_label.grid(row=0, column=0)
    
    # Data Frames Monitoring
    
    #container_frame = Canvas(monitoring_f)
    #container_frame.grid(row=0, column=1)
    
    #scrollbar = Scrollbar(container_frame, orient="vertical", command=canvas.yview)
    #scrollbar.grid(row=0, column=0)
    
    #scrolled_frame = Canvas(monitoring_f)
    #scrolled_frame.grid(row=0, column=0)
    
    #scrollable_frame.bind()
    
    data_frame = Frame(monitoring_f)
    data_frame.grid(row=1, column=0)
    
    space_frame1 = Frame(monitoring_f, height=10, background="#FFFFFF")
    space_frame1.grid(row=2, column=0)
    
    #data_frame2 = Frame(scrolled_frame)
    #data_frame2.grid(row=2, column=0)
    
    data_frame3 = Frame(monitoring_f)
    data_frame3.grid(row=3, column=0)
    
    #space_frame1 = Frame(scrolled_frame, height=10, background="#FFFFFF")
    #space_frame1.grid(row=4, column=0)
    
    #data_frame4 = Frame(scrolled_frame)
    #data_frame4.grid(row=5, column=0)
    
    # Canvas Frames
    
    monitoring = backend.Visualization
    
    plot_frame_tmp = Canvas(data_frame)
    plot_frame_tmp.grid(row=0, column=0)
    
    temp_canvas = FigureCanvasTkAgg(monitoring.plot_figure(), master=plot_frame_tmp)
    temp_canvas.draw()
    temp_canvas.get_tk_widget().grid(row=0, column=0)
    
    #plot_frame_waterlevel = Canvas(data_frame2)
    #plot_frame_waterlevel.grid(row=0, column=0)
    
    #waterlevel_canvas = FigureCanvasTkAgg(backend.Visualization.plot_figure2(), master=plot_frame_waterlevel)
    #waterlevel_canvas.draw()
    #waterlevel_canvas.get_tk_widget().grid(row=0, column=0)
    
    plot_frame_pH = Canvas(data_frame3)
    plot_frame_pH.grid(row=0, column=0)
    
    ph_canvas = FigureCanvasTkAgg(backend.Visualization.plot_figure_pH(), master=plot_frame_pH)
    ph_canvas.draw()
    ph_canvas.get_tk_widget().grid(row=0, column=0)
    
    #plot_frame_ec = Canvas(data_frame4)
    #plot_frame_ec.grid(row=0, column=0)
    
    #ec_canvas = FigureCanvasTkAgg(backend.Visualization.plot_figure_ec(), master=plot_frame_ec)
    #ec_canvas.draw()
    #ec_canvas.get_tk_widget().grid(row=0, column=0)
    
    
    # Position Management
    posman_f = Frame(row_3, background="#FFFFFF")
    posman_f.grid(row=0, column=1, padx=20, pady=10)
    
    posman_label = Label(posman_f, bg="#FFFFFF", text="POSITION MANAGEMENT", font=('Helvetica', 12))
    posman_label.grid(row=0, column=0, padx=10, pady=10)
    
    
    # control
    
    control_frame = Frame(posman_f, background="#FFFFFF")
    control_frame.grid(row=1, column=0, padx=10, pady=10)
    
    control_frame_label = Label(control_frame, bg="#FFFFFF", text="MOVE", font=('Helvetica', 12))
    control_frame_label.grid(row=0, column=0, padx=10, pady=10)
    
    control_frame_spacer = Frame(control_frame, bg="#FFFFFF")
    control_frame_spacer.grid(row=1, column=0)
    
    text_label_old = Label(control_frame_spacer, text="from:", bg="#FFFFFF")
    text_label_old.grid(row=0, column=0, padx=10, pady=5)
    
    text_label_new = Label(control_frame_spacer, text="to:    ", bg="#FFFFFF")
    text_label_new.grid(row=1, column=0, padx=10, pady=5)
    
    command_text_old = Entry(control_frame_spacer, width=10)
    command_text_old.grid(row=0, column=1, padx=10, pady=5)
    command_text_new = Entry(control_frame_spacer, width=10)
    command_text_new.grid(row=1, column=1, padx=10, pady=5)
    
    command_text_button = Button(control_frame_spacer, bg="#84E752", width=6, text="Apply", highlightthickness = 0, bd = 0, command=lambda:[control_robot.relocate(command_text_old.get(),
                                                                                                                                            command_text_new.get())])
    command_text_button.grid(row=2, column=1, padx = 10, pady=10)
    
    # Position Management
    positions_frame = Frame(posman_f, background="#FFFFFF")
    positions_frame.grid(row=2, column=0, padx=10, pady=10)
    
    positions_frame_label = Label(positions_frame, bg="#FFFFFF", text="PLANT MANAGEMENT", font=('Helvetica', 12))
    positions_frame_label.grid(row=0, column=0, padx=10, pady=10)
    
    positions_frame_spacer = Frame(positions_frame, bg="#FFFFFF")
    positions_frame_spacer.grid(row=1, column=0)
    
    text_label_position = Label(positions_frame_spacer, text="position:", bg="#FFFFFF")
    text_label_position.grid(row=0, column=0, padx=10, pady=5)
    
    text_label_booking_state = Label(positions_frame_spacer, text="booked?  ", bg="#FFFFFF")
    text_label_booking_state.grid(row=1, column=0, padx=10, pady=5)
    
    text_label_species = Label(positions_frame_spacer, text="species: ", bg="#FFFFFF")
    text_label_species.grid(row=2, column=0, padx=10, pady=5)
    
    position_box = OptionMenu(positions_frame_spacer, Position_list, *POSITIONS)
    position_box.grid(row=0, column=1, padx=10, pady=5)
    booking_box = OptionMenu(positions_frame_spacer, Booking_state_list, *BOOKING_STATE)
    booking_box.grid(row=1, column=1, padx=10, pady=5)
    species_box = OptionMenu(positions_frame_spacer, Species_list, *SPECIES)
    species_box.grid(row=2, column=1, padx=10, pady=5)
    
    config_update_button = Button(positions_frame_spacer, bg="#84E752", width=6, text="Update", highlightthickness = 0, bd = 0, command=lambda:[backend.Config.edit_positioning(Position_list.get(),
                                                                                                                                                                                Booking_state_list.get(),
                                                                                                                                                                                Species_list.get())])
    config_update_button.grid(row=3, column=1, padx = 10, pady=10)
    
    #spacer_labels = Label(positions_frame_spacer, bg="#FFFFFF", height=10)
    #spacer_labels.grid(row=4, column=0, padx=10, pady=10)
    
    ctl_labels_frame1 = Frame(positions_frame, bg="#FFFDDD", width=200)
    ctl_labels_frame1.grid(row=2, column=0, padx=10)
    ctl_labels_frame2= Frame(positions_frame, bg="#FFFDDD", width=200)
    ctl_labels_frame2.grid(row=3, column=0, padx=10)
    
    ctl_pos = Label(ctl_labels_frame2, bg="#FFFDDD", text="-\n-\n-")
    ctl_pos.grid(row=2, column=0, padx=10, pady=10)
    
    pos_box_show = OptionMenu(ctl_labels_frame1, Position_list_show, *POSITIONS2)
    pos_box_show.grid(row=0, column=0, padx=10, pady=10)
    
    show_booking_button = Button(ctl_labels_frame1, bg="#FFC300", width=6, text="Check", highlightthickness = 0, bd = 0, command=lambda:[ctl_pos.config(text=backend.Config.check_booking(Position_list_show.get()))])
    show_booking_button.grid(row=0, column=1, padx=10, pady=10)
    
    #ctl_book = Label(ctl_labels_frame, bg="#FFFDDD")
    #ctl_book.grid(row=1, column=0, padx=10, pady=10)
    #ctl_spec = Label(ctl_labels_frame, bg="#FFFDDD")
    #ctl_spec.grid(row=2, column=0, padx=10, pady=10)
    
    #spacer_posman = Frame(posman_f, background="#FFFFFF", width=150, height=120)
    #spacer_posman.grid(row=3, column=0, padx=10, pady=10)
    
    # Control
    control_f = Frame(row_3, background="#FFFFFF")
    control_f.grid(row=0, column=2, padx=10, pady=10)
    #control_f.grid_columnconfigure(1, weight=1)
    
    water_plants = PhotoImage(file="Icons/Plants-Watering-Can-icon32.png")
    light_plants = PhotoImage(file="Icons/Diy-Plant-Under-Sun-icon32p.png")
    cloudy_plants = PhotoImage(file="Icons/Programming-Cloudflare-icon32.png")
   
    irrigation_frame = Frame(control_f, background="#FFFFFF")
    irrigation_frame.grid(row=0, column=0, padx=10, pady=10)
    
    nutrients_frame = Frame(control_f, background="#FFFFFF")
    nutrients_frame.grid(row=1, column=0, padx=10, pady=10)
    
    circulation_frame = Frame(control_f, background="#FFFFFF")
    circulation_frame.grid(row=2, column=0, padx=10, pady=10)
    
    
    
    # irrigation
    irrigation_frame_label = Label(irrigation_frame, bg="#FFFFFF", text="IRRIGATION", font=('Helvetica', 12))
    irrigation_frame_label.grid(row=0, column=0, padx=10, pady=5)
    
    irrigation_scale = Scale(irrigation_frame, activebackground="#84E752", bg="#FFFFFF", bd=0, highlightbackground="#FFFFFF", highlightcolor="#84E752", sliderrelief=FLAT, sliderlength=15, orient='horizontal', length=300, from_=0, to=100, variable=var_scale_irrigation)
    irrigation_scale.grid(row=1, column=0, padx=5, pady=5)
    
    irrigation_apply = Button(irrigation_frame, bg="#84E752", width=6, text="Apply", highlightthickness = 0, bd = 0, command=lambda:[control_p.change_val_pump(var_scale_irrigation.get()),
                                                                                                                                     print("Values changed.")])
    irrigation_apply.grid(row=2, column=0, padx=5, pady=5)
    
    # nutrientspump
    
    nutrients_frame_label = Label(nutrients_frame, bg="#FFFFFF", text="NUTRIENTS", font=('Helvetica', 12))
    nutrients_frame_label.grid(row=0, column=0, padx=10, pady=5)
    
    nutrients_scale = Scale(nutrients_frame, activebackground="#84E752", bg="#FFFFFF", bd=0, highlightbackground="#FFFFFF", highlightcolor="#84E752", sliderrelief=FLAT, sliderlength=15, orient='horizontal', length=300, from_=0, to=100, variable=var_scale_nutrients)
    nutrients_scale.grid(row=1, column=0, padx=5, pady=5)
    
    nutrients_apply = Button(nutrients_frame, bg="#84E752", width=6, text="Apply", highlightthickness = 0, bd = 0, command=lambda:[control_p.change_val_nutrients(var_scale_nutrients.get()),
                                                                                                                                     print("Values changed.")])
    nutrients_apply.grid(row=2, column=0, padx=5, pady=5)
    
    # circulation
    circulation_frame_label = Label(circulation_frame, bg="#FFFFFF", text="CIRCULATION", font=('Helvetica', 12))
    circulation_frame_label.grid(row=0, column=0, padx=10, pady=5)
    
    circulation_fan_frame = Frame(circulation_frame, bg="#FFFFFF")
    circulation_fan_frame.grid(row=1, column=0, padx=5, pady=5)
    
    fan_button_label_on = Label(circulation_fan_frame, bg="#FFFFFF", text="on", font=('Helvetica', 8))
    fan_button_label_on.grid(row=0, column=1, padx=2)
    fan_button_label_off = Label(circulation_fan_frame, bg="#FFFFFF", text="off", font=('Helvetica', 8))
    fan_button_label_off.grid(row=0, column=2, padx=2)
    
    circulation_fan_raisin = Label(circulation_fan_frame, bg="#FFFFFF", text="Fan", font=('Helvetica', 10))
    circulation_fan_raisin.grid(row=1, column=0, padx=5, pady=2)
    #circulation_fan_growing = Label(circulation_fan_frame, bg="#FFFFFF", text="Fans Growing Floors", font=('Helvetica', 10))
    #circulation_fan_growing.grid(row=2, column=0, padx=5, pady=2)
    fan_raisin_button_on = Button(circulation_fan_frame, height=1, width=1, background = "#84E752", highlightthickness = 0, bd = 0, command=lambda:[print("Starting vents..."),
                                                                                                                                                    control_p.start_circulation(12, 2500),
                                                                                                                                                    control_p.start_circulation(13, 2500),
                                                                                                                                                    control_p.start_circulation(10, 2500)
                                                                                                                                                    ])
    fan_raisin_button_on.grid(row=1, column = 1, padx=5, pady=2)
    fan_raisin_button_off = Button(circulation_fan_frame, height=1, width=1, background = "#E75252", highlightthickness = 0, bd = 0, command=lambda:[print("Stopping vents..."),
                                                                                                                                                     control_p.stop_circulation(12),
                                                                                                                                                     control_p.stop_circulation(13),
                                                                                                                                                     control_p.stop_circulation(10)
                                                                                                                                                     ])
    fan_raisin_button_off.grid(row=1, column = 2, padx=5, pady=2)
    
    # Light
    light_f = Frame(control_f, background="#FFFFFF")
    light_f.grid(row=4, column=0, padx=5, pady=5)
    
    lights_label = Label(light_f, background="#FFFFFF", text="LIGHTS", font=('Helvetica', 12))
    lights_label.grid(row=0, column=0, padx=5, pady=5)
    
    check_boxes_frame = Frame(light_f, background="#FFFFFF")
    check_boxes_frame.grid(row=1, column=0, padx=5, pady=5)
    
    trd_box = Checkbutton(check_boxes_frame, text="raisin", bg="#FFFFFF", bd=0, relief=FLAT, width=6, variable=state_light_raisin, font=('Helvetica', 10))
    trd_box.grid(row=0, column=0, padx=10, pady=5)
    snd_box = Checkbutton(check_boxes_frame, text="first-RB", bg="#FFFFFF", bd=0, relief=FLAT, width=6, variable=state_light_second, font=('Helvetica', 10))
    snd_box.grid(row=0, column=1, padx=10, pady=5)
    fst_box = Checkbutton(check_boxes_frame, text="first-White", bg="#FFFFFF", bd=0, relief=FLAT, width=6, variable=state_light_first, font=('Helvetica', 10))
    fst_box.grid(row=0, column=2, padx=10, pady=5)
    eg_box = Checkbutton(check_boxes_frame, text="zero", bg="#FFFFFF", bd=0, relief=FLAT, width=6, variable=state_light_eg, font=('Helvetica', 10))
    eg_box.grid(row=0, column=3, padx=10, pady=5)
    
    light_frame = Frame(light_f, background="#FFFFFF")
    light_frame.grid(row=2, column=0, padx=5, pady=5)
    
    control_lights = Frame(light_frame, bg="#FFFFFF")
    control_lights.grid(row=1, column=0, padx=5, pady=5)
    
    lights_time_frame = Frame(control_lights, bg="#FFFFFF")
    lights_time_frame.grid(row=0, column=0, padx=5, pady=5)
    
    lights_start_h = OptionMenu(lights_time_frame, Light_start_h, *CH_S_H)
    lights_start_h.grid(row=0, column=0, padx=1)
    lights_dp_start = Label(lights_time_frame, bg="#FFFFFF", text=":", font=('Helvetica', 8))
    lights_dp_start.grid(row=0, column=1)
    lights_start_m = OptionMenu(lights_time_frame, Light_start_m, *CH_S_M)
    lights_start_m.grid(row=0, column=2, padx=1)
    lights_space = Label(lights_time_frame, bg="#FFFFFF", text=" - ", font=('Helvetica', 8))
    lights_space.grid(row=0, column=3)
    lights_end_h = OptionMenu(lights_time_frame, Light_end_h, *CH_E_H)
    lights_end_h.grid(row=0, column=4, padx=1)
    lights_dp_end = Label(lights_time_frame, bg="#FFFFFF", text=":", font=('Helvetica', 8))
    lights_dp_end.grid(row=0, column=5)
    lights_end_m = OptionMenu(lights_time_frame, Light_end_m, *CH_E_M)
    lights_end_m.grid(row=0, column=6, padx=1)
    
    lights_apply = Button(lights_time_frame, bg="#84E752", width=6, text="Apply", highlightthickness = 0, bd = 0, command=lambda:[print("Getting state of the checkboxes..."),
                                                                                                                                  control_p.get_state_boxes(state_light_eg.get(), state_light_first.get(), state_light_second.get(), state_light_raisin.get()),
                                                                                                                                  print("Success!"),
                                                                                                                                  control_p.write_time_list(Light_start_h.get(), Light_start_m.get(), Light_end_h.get(), Light_end_m.get(), var_scale_lights.get()), 
                                                                                                                                  print("Values changed.")
                                                                                                                                  ])
    lights_apply.grid(row=0, column=7, padx=10, pady=2)
    
    light_val_scale = Scale(control_lights, activebackground="#84E752", bg="#FFFFFF", bd=0, highlightbackground="#FFFFFF", highlightcolor="#84E752", sliderrelief=FLAT, sliderlength=15, orient='horizontal', length=350, from_=0, to=100, label = "intensity [%]", variable=var_scale_lights)
    light_val_scale.grid(row=1, column=0, padx=5, pady=5)
    
    ani = backend.animation.FuncAnimation(monitoring.plot_figure(), backend.Visualization.animate, interval=5000)
    #ani2 = backend.animation.FuncAnimation(monitoring.plot_figure2(), backend.Visualization.animate2, interval=5000)
    ani3 = backend.animation.FuncAnimation(monitoring.plot_figure_pH(), backend.Visualization.animate_pH, interval=10000)
    #ani4 = backend.animation.FuncAnimation(monitoring.plot_figure_ec(), backend.Visualization.animate_ec, interval=5000)
    
    root.mainloop()
    
#if __name__ == '__main__':
#    gui()