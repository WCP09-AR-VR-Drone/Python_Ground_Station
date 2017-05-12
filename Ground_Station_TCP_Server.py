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
from iPad_data_collector import iPad_data_collector,iPad_data_processor
from headset_data_collector import headset_data_collector, headset_data_processor


""" This is the server object that will be running """
class Ground_Station_TCP_Server():
    ipad_port = 8082
    headset_port = 8081
    disable_dronekit = True # Value of True allows testing without dronekit

    def __init__(self):
        # Setup the headset data collection server
        self.headset_server = Factory()  
        self.headset_server.protocol = headset_data_collector
        self.headset_server.protocol.connection_port = self.headset_port
        self.headset_server.clients = []
        # Create the headset interface object
        self.headset_obj = headset_data_processor()
        self.headset_server.protocol.headset_obj = self.headset_obj

        # Setup the iPad data collection server
        self.iPad_server = Factory( )
        self.iPad_server.protocol = iPad_data_collector
        self.iPad_server.protocol.connection_port = self.ipad_port
        self.iPad_server.clients = []
        # Create the iPad interface object
        self.iPad_obj = iPad_data_processor()
        self.iPad_server.protocol.iPad_obj = self.iPad_obj
        self.iPad_server.protocol.headset_obj = self.headset_obj

    """ Setup the server for first use """
    def init_gs_server(self, enable_headset, disable_dronekit):
        if enable_headset:
            gimbal_control = "headset"
        else:
            gimbal_control = "ipad"
        self.update_server_flags(gimbal_control, disable_dronekit)
        self.start_dronekit()
        # Associate tcp server with protocols
        reactor.listenTCP(self.ipad_port, self.iPad_server)
        reactor.listenTCP(self.headset_port, self.headset_server)

    """ Connect to DroneKit (if enabled), and start ground station server"""
    def start_dronekit(self):
        if self.disable_dronekit:
            print "DroneKit Disabled"
        else:
            print "DroneKit Enabled"
            self.drone = connect("com4", wait_ready=None, baud=57600)
            self.iPad_server.protocol.drone = self.drone
            self.iPad_obj.drone = self.drone
            self.headset_server.protocol.drone = self.drone
            self.headset_obj.drone = self.drone

    """ This method updates flags on all servers (so you only have to do it in one place) """
    def update_server_flags(self, gimbal_control, disable_dronekit):
        # update gimbal control flags on servers
        print "Gimbal Controls:", gimbal_control
        self.iPad_server.protocol.gimbal_control = gimbal_control
        self.iPad_obj.gimbal_control = gimbal_control        
        self.headset_server.protocol.gimbal_control = gimbal_control
        self.headset_obj.gimbal_control = gimbal_control
        
        # Update Dronekit flags on servers
        self.disable_dronekit = disable_dronekit
        self.iPad_server.protocol.disable_dronekit = disable_dronekit
        self.headset_server.protocol.disable_dronekit = disable_dronekit
        self.headset_obj.disable_dronekit = disable_dronekit
        self.iPad_obj.disable_dronekit = disable_dronekit