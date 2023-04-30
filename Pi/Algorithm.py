'''
How the robot should run:
press the start button, it finds the first bucket and then drives directly towards it.
When it gets to the first bucket it uses the second argument of the instruction to go around the bucket.
If the robot sees the next bucket while going around it will lock on and start going directly towards it and continue.
If not it will start to search for it, if it finds it before some amount of time it will go towards it and continue, if not the robot will turn itself off.

States: searching, locked on, at instruction, diverting 
searching -> locked on -> at instruction -> searching (diverting if/when needed)

self.motors.arc_turn(x) -> {x > 0 => turns left, x < 0 => turns right}
'''

from time import sleep, time
import math

from Data import Data
from MotorControls import Motors
import Config

class Algorithm(object):
    def __init__(self):
        self.tick_time = None
        
        self.data = Data()
        self.motors = Motors(None, None, None, None)
        self.instructions = [["blue", 110], ["yellow", 40], ["blue", 110]]
        self.prev_instructions = []

        self.state = "searching"
        self.states = ["Searching", "locked_on", "at_instruction"]

        ## Searching Variables
        self.searching_initialized = False
        self.num_times_seen = 0
        self.searching_found = False
        
        ## Locked on variables
        self.locke_on_initialized = False
        
        ## At instruction variables
        self.at_instruction_initialized = False

        ## Diverting variables
        self.diverting_initialized = False

        

    def start(self):
        self.tick_time = time()
        while (True):
            if time() - self.tick_time > 0.05:
                self.tick()
                self.tick_time = time()

    def tick(self):
        self.data.get_data()
        if self.state == "searching":
            self.searching()
        if self.state == "locked_on":
            self.locked_on()
        if self.state == "at_instruction":
            self.at_instruction()
        if self.state == "diverting":
            self.diverting()

    def searching(self):
        if not self.searching_found:
            sees_obj = False
            for region in self.data.cam:
                if sees_obj == True:
                    break
                ## No objects in the region
                elif region == []:
                    continue

                for obj in region:
                    if obj[1] == self.instructions[0][0]:
                        sees_obj = True
                        self.num_times_seen += 1
                        print(self.num_times_seen)
                        break
            if sees_obj == False:
                self.num_times_seen = 0
            if self.num_times_seen > 10:
                self.searching_found = True

        # probably found the object with camera
        elif self.searching_found:
            for region_num, region in enumerate(self.data.cam):
                ## No objects in the region
                if region == []:
                    continue

                for obj in region:
                    if not obj[1] == self.instructions[0][0]:
                        continue
                    
                    elif region_num < math.floor(Config.num_regions/2):
                        self.motors.arc_turn(0.1)
                    elif region_num > math.floor(Config.num_regions/2):
                        self.motors.arc_turn(-0.1)
                    else:
                        print("Locked on: " + str(region_num))
             

    def locked_on(self):
        pass
    
    def at_instruction(self):
        pass

    def diverting(self):
        pass
    