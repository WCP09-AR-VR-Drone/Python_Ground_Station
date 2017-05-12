# -*- coding: utf-8 -*-

""" WCP09 AR/VR Ground Staion Application (Python) """

""" 
    Ground_Station.py is main module for the Python side of the Ground Station.
    This module sets up a TCP server to allow communictaion with an iPad and headset software.
    This module also sets up the initial DroneKit connection to the drone.
""" 

__author__ = "Alexander Rando"
__copyright__ = "Copyright 2017, Binghamton University, State University of New York"
__credits__ = ["Alexander T. Rando", "Robert Valenti", "Brandon Okraszewski", "Clinton Hastings", "Ryan Empson",
                       "WCP09_ARVRDRONE", "Binghamton University", "Lockheed Martin Corp."]
__version__ = "1.2.0"
__status__ = "Development"

import Tkinter
from Tkinter import *
import numpy as np
import cv2
from PIL import Image, ImageTk
import sys
import random

from twisted.internet import tksupport, reactor

# Custom Files
from Ground_Station_TCP_Server import Ground_Station_TCP_Server
from iPad_data_collector import iPad_data_collector
from headset_data_collector import headset_data_collector
from Ground_Station_GUI import GroundStationDialog

def __main():
    root = Tkinter.Tk()
    tksupport.install(root)  # allows Tkinter and Twisted to run together
    root.wm_title("WCP09 Ground Station Application")
    gs_app = GroundStationDialog(root)  # Create the app object

    print "====WCP09 AR/VR Ground Station Application Dialog==="
    print "\nPlease leave open while the Ground Station application is running\n"

    # Set everything in motion
    reactor.run()
    try:
        print "The application has ended, it this window or others persist, please force quit"
        root.destroy()
        del gs_app
    except:
        print "except"
__main()