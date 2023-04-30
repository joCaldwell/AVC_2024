'''
class for holding both motors and all functions to use them like arc turns, and move straight 
'''

import Config

class Motors(object):
    def __init__(self, left_pwm_pin, left_encoder_pin, right_pwm_pin, right_encoder_pin):
        self.left_pwm_pin =left_pwm_pin 
        self.left_encoder_pin = left_encoder_pin 
        self.right_pwm_pin = right_pwm_pin 
        self.right_encoder_pin = right_encoder_pin

    def move_straight(self, speed_mps):
        self.__set_left_motor_speed = speed_mps
        self.__set_right_motor_speed = speed_mps
    
    def arc_turn(self, radius_meters, outer_wheel_speed=Config.base_speed):
        radius = Config.robot_width/2
        if radius_meters == radius/2: # no divide by zero
            radius_meters = radius+0.1 # no divide by zero
        speed_ratio = (abs(radius_meters)+radius)/(abs(radius_meters)-radius) # always > 1
        if radius_meters > 0:
            self.__set_right_motor_speed(outer_wheel_speed)
            self.__set_left_motor_speed(outer_wheel_speed/speed_ratio) # left always slower than right
            print("turning left")
        elif radius_meters < 0:
            self.__set_left_motor_speed(outer_wheel_speed)
            self.__set_right_motor_speed(outer_wheel_speed/speed_ratio)
            print("turning right")
        else: # turnRadius == 0, stop (SHOULD NOT HAPPEN)
            pass

    ## PRIVATE METHODS
    def __set_right_motor_speed(self, speed_mps):
        pass

    def __set_left_motor_speed(self, speed_mps):
        pass