""" Ground Station TCP Connection Handlers"""

# TCP Server Imports
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

# Dronekit Imports
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions

class iPad_data_collector(Protocol):
    connection_port = 8080    # These first three variables are modified by the
    disable_dronekit = True   # Ground_Station_TCP_Server object in Ground_Station.py
    drone = "NONE"            # The values here are unused default values

    """ This function handles the connection to the iPad """
    def connectionMade(self):
        self.factory.clients.append(self)
        print "iPad connected on port", self.connection_port

    """ This function handles the iPad being disconnected """
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print "iPad has been disconnected"

    """ This function sends the flight instruction to the drone """
    def dataReceived(self, data):
        print "iPad Data:", data
        ### This is where the drone flight controlls are going to go.
        ### We've already connected to the drone, so all that we need here is the translation
        ### from iPad gyro data to movement commands. NOTE:: This functionality is probably dangerous
