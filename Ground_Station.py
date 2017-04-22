# -*- coding: utf-8 -*-

""" WCP09 AR/VR Ground Staion Application (Python) """

""" Contains the header information and manages Ground_Station.py
    Ground_Station.py is the side of the code that perfroms most of the
	calculations and sends signals via dronekit.
""" 

__author__ = "Alexander Rando"
__copyright__ = "Copyright 2017, Binghamton University, State University of New York"
__credits__ = ["Alexander T. Rando", "Robert Valenti", "Brandon Okraszewski", "Clinton Hastings", "Ryan Empson",
                       "WCP09_ARVRDRONE", "Binghamton University", "Lockheed Martin Corp."]
__version__ = "1.0.1"
__maintainer__ = "Alexander Rando"
__email__ = "arando1@binghamton.edu"
__status__ = "Development"


""" General Imports """
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


# TODO: This is where you import the other classes!

"""  Enable this flag to prevent connecting with dronekit """

""" This is the server object that will be running """
class Ground_Station_TCP_Server():

    disable_dronekit = True
    ipad_port = 8082
    headset_port = 8081

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
        
        # Initialize DroneKit connection, and send connection string to servers
        if not self.disable_dronekit:
            self.drone = connect("com4", wait_ready=None, baud=57600)
            self.iPad_server.protocol.drone = self.drone
            self.headset_server.protocol.drone = self.drone

        # Send Dronekit flags to the servers
        self.iPad_server.protocol.disable_dronekit = self.disable_dronekit
        self.headset_server.protocol.disable_dronekit = self.disable_dronekit

    def start_server(self):
        reactor.listenTCP(self.ipad_port, self.iPad_server)
        reactor.listenTCP(self.headset_port, self.headset_server)
        print "The TCP sever has been initialized..."
        reactor.run()


""" Begin Code Execution """		
GndStation_Server = Ground_Station_TCP_Server()
GndStation_Server.start_server()