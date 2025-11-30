import time
from pymycobot import MyCobot
from pymycobot.genre import Coord
from typing import *
import logging
# from core.logger import get_logger
from connect4_engine.utils.logger import logger
from pymycobot import MyCobotSocket

# logger = get_logger(__name__)

class ArmInterface:
    def __init__(self, port: str, baudrate: int):
        # Define arm speeds
        self.ARM_SPEED = 100
        self.ARM_SPEED_PRECISE = 50
        self.DISC_LEVEL = 145
        self.ENTRY_PLANE = 256
        self.STACK_ENTRY = 125
        self.BOARD_PLANE = 312
        self.MOVE_TIMEOUT = 1
        self.port = port
       

        # Define solonoides and LED controlling card pins and constants
        self.SR_St_Pin = 21 # 74HC565 shift register strob pin (12) - active high (low/hig/low pulse shift Sr vector to outputs)make sure set low during "push"data in
        self.SR_Data_Pin = 23 # 74HC565 Data in pin (14)
        self.SR_Clk_Pin = 22 # 74HC565 shift clock pin (11) - active high (low/hig/low pulse shift data in) make sure initaly set to low
        #self.En_Pin = 19 # 74HC565 out put enable pin (13) - active low active low (not need to be used, pull Down resistor on board)
        
        self.LED_ON_TIME = 0.1 # sec 
        self.LED_OFF_TIME = 0.1 # sec
        self.LED_BLINK_NUMBER = 10 #
        self.SOLENOIDE_ON_TIME = 0.5 # sec 
        self.SOLENOIDE_SPACE_TIME = 1 # sec, the time between on each soleoide 

        self.NUMBER_OF_SOLENOIDS = 7
        self.LED_SWITCH = 0x07 # switch led is the last output - most right on PCB, far from input connector
        self.current_state = 0x00 # used to remember and keep current outputs when change only part of the IOs 

        # Define of start button pins
        self.LED_pin = 21
        self.button_pin = 18 #used to get input from the user to start the game

        # Define Pump operations constants and M5 controller ("Basic") IO pins
        self.pump_pin = 5
        self.valve_pin = 2
        self.VACCUM_BUILD_TIME = 0.1 #seconds
        self.VACCUM_DROP_TIME = 0.2 #seconds
        
        # Define angle tables for different positions
        self.angle_table = {
            "recovery": [-20, 105, -145, 145, -90, 0],
            "prepare": [0, 105, -145, 35, 0, 0],
            "observe": [0, 105, -145, 145, -90, 0],
            "stack-apro-L": [120, 4, 302, -90, 0, -90],
            "stack-hover-L": [115, 4, 302, -90, 0, -90],
            "stack-apro-R": [120, -51, 303, -90, 0, -90],
            "stack-hover-R": [115, -51, 303, -90, 0, -90],
            "handover-window": [-113.4, -198.7, self.ENTRY_PLANE,0, 0, -90],
            "in-window": [-130, -194, self.BOARD_PLANE-8 ,0, 0, -90],
        }

        # Define chess table for different positions
        self.chess_table = [None for _ in range(7)]
        self.chess_table[6] = [-180, -143, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[5] = [-180, -92, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[4] = [-180, -45, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[3] = [-180, 0, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[2] = [-180, 52, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[1] = [-180, 90, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        self.chess_table[0] = [-180, 143, self.ENTRY_PLANE, 0.11, 0.34, -91.23]
        
        # Define drop table for different positions
        self.drop_table = [None for _ in range(7)]
        self.drop_table[6] = [-184.5, -149, self.BOARD_PLANE-3, 0.11, 0.34, -91.23]
        self.drop_table[5] = [-183, -100, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        self.drop_table[4] = [-182.6, -48, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        self.drop_table[3] = [-181.6, 0, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        self.drop_table[2] = [-180.2, 45, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        self.drop_table[1] = [-184.6, 93, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        self.drop_table[0] = [-186.5, 143, self.BOARD_PLANE, 0.11, 0.34, -91.23]
        

        # Define retry count
        self.retry = 5
        
        # Define discs count
        self.ylw_disc_taken = 0
        self.red_disc_taken = 0

        # Initialize MyCobot instance
        self.mc = MyCobot(port, baudrate, timeout=0.5, debug=True)

        # counter mycobot module contaminating the root logger
        # logging.getLogger().setLevel(logging.CRITICAL)
        self.mc.log.setLevel(logging.DEBUG)
        self.mc.log.propagate = False

        # Set up log to file
        mc_file_hdlr = logging.FileHandler("logs/robot.log")
        mc_file_hdlr.setFormatter(
            logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
        )
        self.mc.log.addHandler(mc_file_hdlr)

        self.mc.set_fresh_mode(0) #1 - Always execute the latest command first. 0 - Execute instructions sequentially in the form of a queue.
        self.mc.set_movement_type(0)

        #setup of IOs
        self.mc.set_basic_output(self.SR_Data_Pin, 0) #
        self.mc.set_basic_output(self.SR_St_Pin, 0) #
        self.mc.set_basic_output(self.SR_Clk_Pin, 0) #
        self.off_all_outputs() # make sure initialy all outpurs are low 
        self.current_state = 0x00 #  update outputs state

    # On byte - this routin only update the state but NOT change ouptut 
    def on_current_state_bit(self, out_number):
        digit_position = 0x01
        digit_position = digit_position << out_number # rotate left 
        self.current_state = (self.current_state | digit_position) #bitwise OR operator

    # Off byte -this routin only update the state but NOT change ouptut 
    def off_current_state_bit(self, out_number):
        digit_position = 0x01
        digit_position = digit_position << out_number # rotate left 
        self.current_state = (self.current_state &(~digit_position)) #bitwise AND and NOT operators

    # shiftOut function adding for python
    def shift_out(self, SR_Data_Pin, SR_Clk_Pin, bit_order, value):
        for i in range(8):
            bit = (value >> (7 - i)) & 0x01 if bit_order == "MSBFIRST" else (value >> i) & 0x01
            self.mc.set_basic_output(SR_Data_Pin, bit)
            self.mc.set_basic_output(SR_Clk_Pin, 1)
            time.sleep(0.1)
            self.mc.set_basic_output(SR_Clk_Pin, 0)

    # drive output rutine - this is the routine that update and change the shift register outputs
    def drive_output(self, output_byte):
        self.shift_out(self.SR_Data_Pin, self.SR_Clk_Pin, "MSBFIRST", output_byte) # shift the all 8 bits into the shift register, most bit first  
        self.mc.set_basic_output(self.SR_St_Pin, 1) # pulse latch/strobe pin to update shift register outputs
        self.mc.set_basic_output(self.SR_St_Pin, 0) #

    #  switch on all outputs - ! without update current state !
    def on_all_outputs(self):
        self.drive_output(0xff)

    #  switch off all outputs - ! without update current state !
    def off_all_outputs(self):
        self.drive_output(0x00)

    #  on_switch_led and update current state
    def on_switch_led(self):
        self.on_current_state_bit(self.LED_SWITCH)
        self.drive_output(self.current_state)

    #  off_switch_led and update current state
    def off_switch_led(self):
        self.off_current_state_bit(self.LED_SWITCH)
        self.drive_output(self.current_state)



    # Method to turn on the pump
    def pump_on(self):
        # close to exust the valve
        self.mc.set_basic_output(self.valve_pin, 1)
        logger.debug(f"exhust closed")
        # start pump
        self.mc.set_basic_output(self.pump_pin, 0)
        logger.debug(f"pump on")
        time.sleep(self.VACCUM_BUILD_TIME)

    # Method to turn off the pump
    def pump_off(self):
        # Close the solenoid valve
        self.mc.set_basic_output(self.pump_pin, 1)
        logger.debug(f"pump off")
        # Start the exhaust valve
        self.mc.set_basic_output(self.valve_pin, 0)
        logger.debug(f"exhaust open")
        time.sleep(self.VACCUM_DROP_TIME)


    # Method to send angles with retry logic
    def send_angles(self, angle, speed):
        self.mc.sync_send_angles(angle, speed, self.MOVE_TIMEOUT)
        for tries in range(3):
            if not self.mc.is_in_position(angle, 0):
                self.mc.sync_send_angles(angle, speed, self.MOVE_TIMEOUT)
        
    # Method to send coords with retry logic
    def send_coords(self, coords, speed, mode = 0):
        self.mc.sync_send_coords(coords, speed, mode, self.MOVE_TIMEOUT)
        for tries in range(3):
            if not self.mc.is_in_position(coords, 1):
                self.mc.sync_send_coords(coords, speed, mode, self.MOVE_TIMEOUT)

    # Method to set basic output with retry logic
    def set_basic_output(self, val1, val2):
        self.mc.set_basic_output(val1, val2)

    # Method to send coordinates with retry logic
    def send_coord(self, arm_id, coord, speed):
        self.mc.send_coord(arm_id, coord, speed)       

    # Method to pass to the prepare position
    def prepare(self):
        self.send_angles(self.angle_table["prepare"], self.ARM_SPEED)
                
    # Method to return to the initial position
    def recovery(self):
        self.send_angles(self.angle_table["recovery"], self.ARM_SPEED)

    # Method to move to the top of the left discs stack
    def hover_over_stack_left(self):
        self.send_coords(self.angle_table["stack-hover-L"], self.ARM_SPEED_PRECISE, 1)
    
    # Method to move to in front of left discs stack
    def apro_stack_left(self):
        self.send_coords(self.angle_table["stack-apro-L"], self.ARM_SPEED,0)

    # Method to move to the top of the right disks stack
    def hover_over_stack_right(self):
        self.send_coords(self.angle_table["stack-hover-R"], self.ARM_SPEED_PRECISE, 1)
        
    # Method to move to in front of right discs stack
    def apro_stack_right(self):
        self.send_coords(self.angle_table["stack-apro-R"], self.ARM_SPEED,0)

    # Method to pick up a disk form stakc level n with thickness t
    def get_disc_yellow(self, counter: int,thickness: int):
        self.temp_target_coords = self.angle_table["stack-hover-R"] 
        self.disc_x_coord=self.DISC_LEVEL+(counter*thickness)
        self.temp_target_coords[0]=self.disc_x_coord
        self.send_coords(self.temp_target_coords, self.ARM_SPEED, 1)
        self.pump_on()
        self.send_coords(self.angle_table["stack-apro-R"], self.ARM_SPEED,1)  
        #self.send_coord(Coord.X.value,self.STACK_ENTRY,self.ARM_SPEED_PRECISE)
	    
    # Method to pick up a disk form stack level n with thickness t
    def get_disc_red(self, counter: int,thickness: int):
        self.temp_target_coords = self.angle_table["stack-hover-L"] 
        self.disc_x_coord=self.DISC_LEVEL+(counter*thickness)
        self.temp_target_coords[0]=self.disc_x_coord
        self.send_coords(self.temp_target_coords, self.ARM_SPEED, 1)
        self.pump_on()
        self.send_coords(self.angle_table["stack-apro-L"], self.ARM_SPEED,1)
        #self.send_coord(Coord.X.value,self.STACK_ENTRY,self.ARM_SPEED_PRECISE)
                    
    # Method to move to the handover window and drop the disk
    def drop_in_window(self):
       #logger.debug("droping disc in window")
       self.send_coords(self.angle_table["handover-window"], self.ARM_SPEED)        
       self.send_coords(self.angle_table["in-window"], self.ARM_SPEED, 1)
       self.pump_off()
       #time.sleep(0.5)
       self.send_coords(self.angle_table["handover-window"], self.ARM_SPEED,0) 


    # Method to move to the top of the chessboard
    def hover_over_chessboard_n(self, n: int):
        if n is not None and 0 <= n <= 6:
            logger.debug(f"Move to chess position {n}, Coords: {self.chess_table[n]}")
            self.send_coords(self.chess_table[n], self.ARM_SPEED)
            self.send_coords(self.drop_table[n], self.ARM_SPEED, 1)
            self.pump_off()
            time.sleep(0.5)
            self.send_coords(self.chess_table[n], self.ARM_SPEED)
        else:
            self.pump_off()
            raise Exception(
                f"Input error, expected chessboard input point must be between 0 and 6, got {n}"
            )

    # Method to move to the observation posture
    def observe_posture(self):
        logger.debug(f"Move to observe position {self.angle_table['observe']}")
        self.send_angles(self.angle_table["observe"], self.ARM_SPEED)
        time.sleep(2)

    # Method to move the arm
    def move(self, action: str):
        logger.debug(f"Action move: {action} Angles {self.angle_table[action]}")
        self.mc.send_angles(self.angle_table[action], self.ARM_SPEED)

    # Method to drop the chess piece
    def drop_piece(self):
        logger.debug(f"Dropping piece at {self.mc.get_angles()}")
        self.mc.move_round()
        time.sleep(2.5)

    # Method to Clear the column n
    def clear_column(self, column:int):
        logger.debug(f"opening pin under column {column}")
        self.on_current_state_bit(column) # only update the state but NOT change ouptut 
        self.drive_output(self.current_state) # now change outputs 
        time.sleep (self.SOLENOIDE_ON_TIME) 
        self.off_current_state_bit(column) # only update the state but NOT change ouptut 
        self.drive_output(self.current_state) # now change outputs 
        time.sleep(self.SOLENOIDE_SPACE_TIME)
        
    # Method to Clear all colums
    def clear_board(self):
        logger.debug(f"clearing board")
        for col in range(7):
            self.clear_column(col)
        self.ylw_disc_taken = 0 
        self.red_disc_taken = 0 

    # method to change head color
    def set_color(self, r:int, g:int, b:int):
        self.mc.set_color(r, g, b)
    
      
