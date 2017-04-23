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
__version__ = "1.0.2"
__maintainer__ = "Alexander Rando"
__email__ = "arando1@binghamton.edu"
__status__ = "Development"


# General Imports
import threading
import time
import sys
import math
from serial import *

# TCP Server Imports
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

# Dronekit Imports
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions

# Custom Files
from iPad_data_collector import iPad_data_collector
from headset_data_collector import headset_data_collector


""" This is the server object that will be running """
class Ground_Station_TCP_Server():
    ipad_port = 8082
    headset_port = 8081
    disable_dronekit = True # Value of True allows testing without dronekit

    def __init__(self):
        # Setup the iPad data collection server
        self.iPad_server = Factory()
        self.iPad_server.protocol = iPad_data_collector
        self.iPad_server.protocol.connection_port = self.ipad_port
        self.iPad_server.clients = []

        # Setup the headset data collection server
        self.headset_server = Factory()  
        self.headset_server.protocol = headset_data_collector
        self.headset_server.protocol.connection_port = self.headset_port
        self.headset_server.clients = []
        
        use_drone = raw_input("Would you like to disable dronekit? (y/N): ")
        if "y" in use_drone.lower():
            print "DroneKit Disabled"
            self.disable_dronekit = True
        else:
            print "DroneKit Enabled"
            self.disable_dronekit = False

        # Initialize DroneKit connection, and send connection string to servers
        if not self.disable_dronekit:
            self.drone = connect("com4", wait_ready=None, baud=57600)
            self.iPad_server.protocol.drone = self.drone
            self.headset_server.protocol.drone = self.drone

        # Send Dronekit flags to the servers
        self.iPad_server.protocol.disable_dronekit = self.disable_dronekit
        self.headset_server.protocol.disable_dronekit = self.disable_dronekit

    def start_server(self):
        use_headset = raw_input("Would you like to use the headset for gimbal controls? (y/N): ")
        if "y" in use_headset.lower():
            print "Gimbal Controls: Headset"
            self.iPad_server.protocol.gimbal_control = "headset"
            self.headset_server.protocol.gimbal_control = "headset"
        else:
            print "Gimbal Controls: iPad"
            self.iPad_server.protocol.gimbal_control = "ipad"
            self.headset_server.protocol.gimbal_control = "ipad"  

        reactor.listenTCP(self.ipad_port, self.iPad_server)
        reactor.listenTCP(self.headset_port, self.headset_server)

        print "The TCP sever has been initialized..."
        reactor.run()


""" Begin Code Execution """		
GndStation_Server = Ground_Station_TCP_Server()
GndStation_Server.start_server()