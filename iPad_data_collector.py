""" Ground Station TCP Connection Handlers"""

# TCP Server Imports
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

# Dronekit Imports
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions

class iPad_data_collector(Protocol):
    connection_port = 8080    # These first four variables are modified by the
    disable_dronekit = True   # Ground_Station_TCP_Server object in Ground_Station.py
    drone = "NONE"            # The values here are unused default values
    gimbal_control = "ipad"
    loop_ctr = 0    # raising this lowers the frequcy of sending dronekit commands

    """ This function handles the connection to the iPad """
    def connectionMade(self):
        self.factory.clients.append(self)
        print "iPad connected on port", self.connection_port

    """ This function handles the iPad being disconnected """
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        print "iPad has been disconnected"

    """ Translate iPad's YAW movement data to gimbal pwm instruction  """
    def calculate_yaw_pwm(raw_ipad_data):
       if raw_ipad_data < 0:  
           percent_movement = float(abs(raw_ipad_data)) / abs(self.yaw_max)
           return self.yaw_center_pwm - (percent_movement*(self.yaw_center_pwm - 1000))
       else:
           percent_movement = abs(raw_ipad_data) / float(abs(self.yaw_min))
           return self.yaw_center_pwm + (percent_movement*(2000 - self.yaw_center_pwm))
    
    """ Translate and Send iPad's YAW movement data to gimbal  """    
    def yaw_control(raw_gyro_data):
       if (raw_gyro_data > self.yaw_max): # Constrain the bounds of movement
          raw_gyro_data = self.yaw_max
       if (raw_gyro_data < self.yaw_min):
          raw_gyro_data = self.yaw_min
          
       pwm_value = self.calculate_yaw_pwm(raw_gyro_data)
       print "Yaw | Position:", raw_ipad_data, " | Percent:", percent_movement, " | PWM Value:", pwm_value

       yaw_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    6,  # servo number for yaw
                    pwm_value,  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used 
       self.drone.send_mavlink(yaw_cmd)

    """ Translate iPad's PITCH movement data to gimbal pwm instruction  """
    def calculate_pitch_pwm(raw_ipad_data):
      if raw_ipad_data < 0:
           percent_movement = abs(raw_ipad_data) / float(self.pitch_max)
           pwm_value = self.pitch_center_pwm + (percent_movement*(2000 - self.pitch_center_pwm))
      else:
           percent_movement = float(raw_ipad_data) / abs(self.pitch_min)
           pwm_value = self.pitch_center_pwm - (percent_movement*(self.pitch_center_pwm - 1000))
           
    """ Translate and send ipad PITCH movement data to gimbal  """
    def pitch_control( position ):  # Send control signals for the gimbal's pitch
       if (position > self.pitch_max):   # Constrain the bounds
          position = self.pitch_max
       if (position < self.pitch_min):
          position = self.pitch_min
    
       pwm_value = self.calculate_pitch_pwm(position)
       print "Pitch | Position:", position, " | Percent:", percent_movement, " | PWM Value:", pwm_value
       
       pitch_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    5,  # servo number for pitch
                    pwm_value,  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used
       self.drone.send_mavlink(pitch_cmd)    
   

    """ This function sends the flight instruction to the drone """
    def dataReceived(self, data):
        print "iPad Data:", data
            ### This is where the drone flight controlls are going to go.
            ### We've already connected to the drone, so all that we need here is the translation
            ### from iPad gyro data to movement commands. NOTE:: This functionality is probably dangerous
        if (self.gimbal_control == "ipad"):
            print "Gimbal Controls:", data
            self.loop_ctr += 1 # track iteration
            movement_data = data.split(":")
            if not self.disable_dronekit:  # Send ipad Gyroscope Data to Dronekit            
                if len(movement_data) >= 3 and self.loop_ctr >= 25:  # Ensure that all data is there and that we don't overload gimbal
                    yaw_pos = int(movement_data[1])
                    pitch_pos = int(movement_data[3])
                    self.pitch_control(pitch_pos)  # Send new positions to gimbal
                    self.yaw_control(yaw_pos)
                
            elif len(movement_data) >= 3 and self.loop_ctr >= 10: # If we are in the debug mode
                self.loop_ctr = 0
                # Extract movement data from stream
                yaw_pos = int(movement_data[1])
                pitch_pos = int(movement_data[3])
                print "iPad data:", yaw_pos, pitch_pos