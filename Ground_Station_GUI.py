'''
WCP09 AR/VR Drone 
Ground Station Application GUI

This contains the class for the GUI side of the Ground 
Station Application. This feature was intended to be mostly
experimental and wasn't put into to the final code until late
into the project timeline. There may be some elements that are
still under developmemt
'''

#General Imports
import os
import sys
import random
import subprocess
import threading

#Imports for the GUI
import Tkinter
from Tkinter import *

#Imports for Image Processing
import numpy as np
import cv2
from PIL import Image, ImageTk

#Imports for internet protocol functions
from twisted.internet import tksupport, reactor
from Ground_Station_TCP_Server import Ground_Station_TCP_Server

#Project Imports
from headset_data_collector import headset_data_collector, headset_data_processor
from iPad_data_collector import iPad_data_collector

#Experimental Imports --Comment out as necesasry
import socket
import base64
import cStringIO

class GroundStationDialog(Tkinter.Frame, Ground_Station_TCP_Server):
    def __init__(self, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)   # Make the dialog a subclass of Tkinter Frame
        self.gs_server = Ground_Station_TCP_Server() 
        self.main_window_init()

    def main_window_init(self):
        self.grid()
        self.configure(background='#fffdd0')

	    # Initialize variable for the banners' text
        headerTextVar = Tkinter.StringVar()
        instructionsTextVar = Tkinter.StringVar()
        instructionsLineTwoTextVar = Tkinter.StringVar()
        instructionsLineThreeTextVar = Tkinter.StringVar()
        instructionsLineFourTextVar = Tkinter.StringVar()


        #Set the text to be displayed
        headerTextVar.set(u"WCP09 Ground Station")       
        instructionsTextVar.set(u"Set desired configuration with the checkboxes below.")  
        instructionsLineTwoTextVar.set(u"Click \"Begin\" to open video stream. Prepare to calibrate headset")  
        instructionsLineThreeTextVar.set(u"NOTE: Two windows will open. When the VR Goggles are comfortable, press \"Set Zero\".")  
        instructionsLineFourTextVar.set(u"Wait for the camera to center, then use head movements to control camera")  

        # Create the Tkinter Label for them
        headerLabel = Tkinter.Label(self,textvariable=headerTextVar, anchor="w",fg="white",bg="#003E23", font = "Verdana 12 bold")
        instructionsLabel = Tkinter.Label(self,textvariable=instructionsTextVar, anchor="w",fg="white",bg="#006A4D", font = "Verdana 10 bold")
        instructionsLineTwoLabel = Tkinter.Label(self,textvariable=instructionsLineTwoTextVar, anchor="w",fg="white",bg="#006A4D", font = "Verdana 10 bold")
        instructionsLineThreeLabel = Tkinter.Label(self,textvariable=instructionsLineThreeTextVar, anchor="w",fg="white",bg="#006A4D")
        instructionsLineFourLabel = Tkinter.Label(self,textvariable=instructionsLineFourTextVar, anchor="w",fg="white",bg="#006A4D")

        # Place the labels on the window
        headerLabel.grid(column=0,row=1,columnspan=5,sticky='EW')
        instructionsLabel.grid(column=0,row=2,columnspan=5,sticky='WE')
        instructionsLineTwoLabel.grid(column=0,row=3,columnspan=5,sticky='WE')
        instructionsLineThreeLabel.grid(column=0,row=4,columnspan=5,sticky='WE')
        instructionsLineFourLabel.grid(column=0,row=5,columnspan=5,sticky='WE')

        ## Create The Checkboxes ##
        # Variables to hold value of checkboxes (for Settings)
        self.use_headset = IntVar()
        self.disable_dronekit = IntVar()
        # Set text for checkboxes
        headset_checkbox_str = "Control gimbal with Vuzix headset (otherwise use iPad)"
        dronekit_checkbox_str = "Disable DroneKit: prevents communication with drone. use for debugging"
        # Place checkboxes onto the window
        Checkbutton(self, text=headset_checkbox_str, variable=self.use_headset).grid(row=6, sticky=W)
        Checkbutton(self, text=dronekit_checkbox_str, variable=self.disable_dronekit).grid(row=7, sticky=W)

        ### Create the buttons ###
        # Create Buttons on windowButton To Begin Camer Feed
        start_button = Tkinter.Button(self,text=u"Begin", command=self.OnButtonClick)
        #quit_button = Tkinter.Button(self,text=u"Quit", command=self.quit_program)
        # Place Buttons on window
        #quit_button.grid(row=8, column=1, sticky='W')		
        start_button.grid(row=8, sticky='W')

    """ Create the window that the camera feed is displayed in"""
    def init_webcam(self):
        self.cap = cv2.VideoCapture(0)  # Capture frames from camera 0

        self.window = Tkinter.Toplevel(self)  # create the camera stream window
        self.window.wm_title("Drone Camera Feed")
        self.window.config(background="#000000")
        self.window.state('zoomed') 

        # Specify geometry of modules
        self.imageFrame = Tkinter.Frame(self.window, width=160, height=150)
        #imageFrame.grid(row=0, column=1, padx=10, pady=2)
        self.imageFrame.pack( side = TOP )
        self.video_module = Tkinter.Label(self.imageFrame)
        self.video_module.grid(row=0, column=0)  #set video module location

    """ This method takes in video stream and overlays the telemetry text """
    def videostream_edit(self):
        stream_status, self.frame = self.cap.read()
        if stream_status:
            # Add text that we want to overlay to image
            text_font = cv2.FONT_HERSHEY_DUPLEX
            font_size = 1.0
            text_color_code = (0, 0, 0)

            if self.disable_dronekit:
                telemetry_string_1 = "No Telemetry Data,"
                battery_string = "Not connected to DroneKit"
            else:
                """
                    This is where we call the dronekit api get drone telemetry data
                    Previous versions used MavLink commands which took too long 
                    and created too much lag in video stream.

                    The following lines are commented out because they are part of an incomplete experiment 
                    whose use could result in unknown behavior such as application crashes.

                    #  airspeed = str(self.gs_server.drone.airspeed)
                    #  battery_status = str(self.gs_server.drone.battery)                             
                """
                
                telemetry_string_1 = "Yaw:" + str(random.random()) + "Pitch:" + str(self.gs_server.headset_obj.pitch_pos)
                battery_string = airspeed = str(self.gs_server.drone.airspeed) #self.gs_server.drone.battery  # "Elevation:   Speed: "

            # Print out the strings we just created
            cv2.putText(self.frame, telemetry_string_1,
                (10, 30), text_font, font_size, text_color_code, 1)
            cv2.putText(self.frame, battery_string,
                (10, 60), text_font, font_size, text_color_code, 1)

            # Start image manipulation
            cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_module.imgtk = imgtk #Shows frame for video module
            self.video_module.configure(image=imgtk)
            self.window.after(5, self.videostream_edit)
            
            """  
            WCP09: The following is from an experiment to send video to the iPad.
            It is left here with the intent to instpire futre development
          
            #buffer = cStringIO.StringIO()
            #img.save(buffer, format="JPEG")
            #img_str = base64.b64encode(buffer.getvalue())
            
            UDP_IP = "127.0.0.1"
            UDP_PORT = 5005
            MESSAGE = "WCP09 iPad Communication Test"
            print "UDP target IP:", UDP_IP
            print "UDP target port:", UDP_PORT
            print "message:", MESSAGE

            sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
            """

    """ This is the method to get rid of all of the windows. This is a test"""
    def quit_program(self):
        cv2.destroyAllWindows()

    """ This method calls the headset tracknig program via relative path """
    def start_headset_data_program(self):
        curr_dir = os.path.dirname(__file__)
        headset_prog_rel_path = str(curr_dir) + '\\..\\External Application\\HelloTracker3\\Release\\HelloTracker3.exe'
        subprocess.call([headset_prog_rel_path]) 

    def OnButtonClick(self):
        # Startup server
        self.gs_server.init_gs_server(self.use_headset.get(), self.disable_dronekit.get())
        self.init_webcam()
        self.videostream_edit()
        # WCP09: This was an attempt to automate the applications startup.
        headset_data_program_thread = threading.Thread(target=self.start_headset_data_program)
        headset_data_program_thread.start()