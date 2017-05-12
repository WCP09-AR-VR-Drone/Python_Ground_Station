""" Headset Server Functionality """

"""
    This file containes two classes:  headset_data_collector and  headset_data_processor.
    These classes manage the recieving and processing of the headset data which is recieved
    on the specified port.

    headset_data_collector is used as the Twisted TCP server protocol.
    headset_data_processor is an object that can perfrom functions specific to the headset.

"""


# TCP Server Imports
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

# Dronekit Imports
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions


# This Class handles the connection to, and the data coming from the headset

# This Class containes a nested class 
class headset_data_collector(Protocol):
    connection_port = 8080
    headset_obj = "empty"
    gimbal_control = "headset"
    disable_dronekit = True
    
    loop_ctr = 0    # raising this lowers the frequcy of sending dronekit commands

    """ handle the incomming connection to the client """
    def connectionMade(self):
        self.factory.clients.append(self)
        print "Headset client connected to port", self.connection_port
        
    """ handles the client being disconnected"""
    def connectionLost(self, reason): 
        self.factory.clients.remove(self)
        print "Headset client disconnected"

    def dataReceived(self, data): 
        self.gimbal_control = self.headset_obj.gimbal_control
        self.loop_ctr += 1 # track iteration
        movement_data = data.split(":")
        if not self.disable_dronekit:  # Send Headset Gyroscope Data to Dronekit            
            if len(movement_data) >= 3 and self.loop_ctr >= 25:  # Ensure that all data is there and that we don't overload gimbal
                # Extract data from stream
                yaw_pos = int(movement_data[1])
                pitch_pos = int(movement_data[3])
                # Translate and send movement data to the drone
                print self.headset_obj, yaw_pos, pitch_pos
                self.headset_obj.pitch_control(pitch_pos)  # Send new positions to gimbal
                self.headset_obj.yaw_control(yaw_pos)                
        elif len(movement_data) >= 3 and self.loop_ctr >= 10:
            self.loop_ctr = 0
            # Extract movement data from stream, but don't send to dronekit
            yaw_pos = int(movement_data[1])
            pitch_pos = int(movement_data[3])
            print yaw_pos, pitch_pos, self.gimbal_control

""" This is the class for the object to track headset data"""
class headset_data_processor():

    """ Default control variables """
    # These are modified by Ground_Station_TCP_Server
    connection_port = 8080
    disable_dronekit = True
    drone = "NONE"
    gimbal_control = "headset"
    

    """ Specify headset parameters; These pwm values specify important gimbal angles """
    yaw_min = -14000
    yaw_max = 19500
    yaw_center_pwm = 1450
    pitch_min = -12000
    pitch_max = 12000
    pitch_center_pwm = 1480

    yaw_pos = 1
    pitch_pos = 1
        
    """ Translate headset's YAW movement data to gimbal pwm instruction  """
    def calculate_yaw_pwm(self, raw_headset_data):
       if raw_headset_data < 0:  
           percent_movement = float(abs(raw_headset_data)) / abs(self.yaw_max)
           return self.yaw_center_pwm - (percent_movement*(self.yaw_center_pwm - 1000))
       else:
           percent_movement = abs(raw_headset_data) / float(abs(self.yaw_min))
           return self.yaw_center_pwm + (percent_movement*(2000 - self.yaw_center_pwm))
    
    """ Translate and Send headset's YAW movement data to gimbal  """    
    def yaw_control(self, raw_headset_data):
       print "raw:", raw_headset_data
       if self.gimbal_control is "ipad":
            return
       if (raw_headset_data > self.yaw_max): # Constrain the bounds of movement
          raw_headset_data = self.yaw_max
       if (raw_headset_data < self.yaw_min):
          raw_headset_data = self.yaw_min
          
       pwm_value = self.calculate_yaw_pwm(raw_headset_data)
       print pwm_value
      # print "Yaw | Position:", raw_headset_data, " | Percent:", percent_movement, " | PWM Value:", pwm_value

       yaw_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    6,  # servo number for yaw
                    float(pwm_value),  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used 
       self.drone.send_mavlink(yaw_cmd)

    """ Translate headset's PITCH movement data to gimbal pwm instruction  """
    def calculate_pitch_pwm(self, raw_headset_data):
      if raw_headset_data < 0:
           percent_movement = abs(raw_headset_data) / float(self.pitch_max)
           return self.pitch_center_pwm + (percent_movement*(2000 - self.pitch_center_pwm))
      else:
           percent_movement = float(raw_headset_data) / abs(self.pitch_min)
           return self.pitch_center_pwm - (percent_movement*(self.pitch_center_pwm - 1000))
           
    """ Translate and send headset PITCH movement data to gimbal  """
    def pitch_control(self, position ):  # Send control signals for the gimbal's pitch
       print "raw:", position
       if self.gimbal_control is "ipad":
            return
       if (position > self.pitch_max):   # Constrain the bounds
          position = self.pitch_max
       if (position < self.pitch_min):
          position = self.pitch_min
           
       pwm_value = self.calculate_pitch_pwm(position)

       #print "Pitch | Position:", position, " | Percent:", percent_movement, " | PWM Value:", pwm_value
       
       pitch_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    5,  # servo number for pitch
                    float(pwm_value),  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used
       self.drone.send_mavlink(pitch_cmd)    
