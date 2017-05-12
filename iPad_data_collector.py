""" Ground Station TCP Connection Handlers"""

# TCP Server Imports
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

# Dronekit Imports
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
from headset_data_collector import headset_data_collector, headset_data_processor

class iPad_data_collector(Protocol):

    connection_port = 8080    # These first four variables are modified by the
    disable_dronekit = True   # Ground_Station_TCP_Server object in Ground_Station.py
    drone = "NONE"            # The values here are unused default values
    gimbal_control = "ipad"
    ipad_control_gimbal = 1
    headset_obj = "empty"
    iPad_obj = "empty"
    loop_ctr = 0    # raising this lowers the frequcy of sending dronekit commands    

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
        self.loop_ctr += 1 # track iteration
        movement_data = data.split(":")
        self.ipad_control_gimbal = int(movement_data[2])
        if self.ipad_control_gimbal:     
            self.headset_obj.gimbal_control = "ipad"
            if not self.disable_dronekit:  # Send ipad Gyroscope Data to Dronekit            
                if len(movement_data) >= 3:  # Ensure that all data is there and that we don't overload gimbal
                    yaw_pos = int(movement_data[1])
                    pitch_pos = int(movement_data[0])
                    self.iPad_obj.pitch_control(pitch_pos)  # Send new positions to gimbal
                    self.iPad_obj.yaw_control(yaw_pos)
                
            elif len(movement_data) >= 3: # If we are in the debug mode
                self.loop_ctr = 0
                # Extract movement data from stream
                yaw_pos = int(movement_data[1])
                pitch_pos = int(movement_data[0])
                ipad_control_gimbal = int(movement_data[2])
                print "iPad data:", yaw_pos, "Pitch:", pitch_pos, "Gimbal:", ipad_control_gimbal
        else:
            self.headset_obj.gimbal_control = "headset"
            self.iPad_obj.gimbal_control = "headset"

class iPad_data_processor():

    disable_dronekit = True   # Ground_Station_TCP_Server object in Ground_Station.py
    drone = "NONE"            # The values here are unused default values
    pwm_min = 1000
    pwm_max = 2000
    yaw_center_pwm = 1450
    pitch_center_pwm = 1480
    sensitivity = .2
    
    """ Translate and Send iPad's YAW movement data to gimbal  """    
    def yaw_control(self,raw_ipad_data):
    
          
        pwm_value = self.yaw_center_pwm + (raw_ipad_data * self.sensitivity)
        self.yaw_center_pwm = pwm_value

        if (pwm_value > self.pwm_max):   # Constrain the bounds
            pwm_value = self.pwm_max
        if (pwm_value < self.pwm_min):
            pwm_value = self.pwm_min 

        print "Yaw | Position:", raw_ipad_data, " | PWM Value:", pwm_value

        yaw_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    6,  # servo number for yaw
                    pwm_value,  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used 
        self.drone.send_mavlink(yaw_cmd)


           
    """ Translate and send ipad PITCH movement data to gimbal  """
    def pitch_control(self, raw_ipad_data):  # Send control signals for the gimbal's pitch
        pwm_value = self.pitch_center_pwm + (raw_ipad_data * self.sensitivity)
        self.pitch_center_pwm = pwm_value
        if (pwm_value > self.pwm_max):   # Constrain the bounds
            pwm_value = self.pwm_max
        if (pwm_value < self.pwm_min):
            pwm_value = self.pwm_min

        print "Pitch | Position:", raw_ipad_data, " | PWM Value:", pwm_value
       
        pitch_cmd = self.drone.message_factory.command_long_encode(
                    0, 0,  # target_system, target_component
                    mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
                    0,  #confirmation
                    5,  # servo number for pitch
                    pwm_value,  # servo position between 1000 and 2000
                    0, 0, 0, 0, 0 ) # param 3 ~ 7 not used
        self.drone.send_mavlink(pitch_cmd)    
 