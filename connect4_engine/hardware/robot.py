from abc import ABC, abstractmethod
from legacy.ArmInterface import ArmInterface
from pymycobot import MyCobot280
from connect4_engine.utils.logger import logger
import time
import json

class IRobot(ABC):

    @abstractmethod
    def drop_piece(self, column: int, puck_no: int):
        pass
    
    @abstractmethod
    def give_player_puck(self, puck_no: int):
        pass

    @abstractmethod
    def reset(self):
        pass

class RobotCommunicator(IRobot):
    def __init__(self, com_port: str = "COM11"):
        self.robot = MyCobot280(com_port)
        self.load_angles()
        self.pump_pin = 5
        self.valve_pin = 2
        self.VACCUM_BUILD_TIME = 0.1 #seconds
        self.VACCUM_DROP_TIME = 0.2 #seconds
        self.robot.sync_send_angles(self.angles["0"], 50)

    
    def load_angles(self):
        with open('connect4_engine/hardware/robot_angles.json', 'r') as f:
            self.angles = json.load(f)

    def drop_piece(self, column: int,  puck_no: int):
        angles = self._get_puck_angle('red', puck_no)
        logger.debug(f"Picking up red puck number {puck_no} at angles {angles}")
        self.robot.sync_send_angles(angles, 50)
        self._pump_on()
        logger.debug(f"Moving to column {column} drop angles {self.angles[f'column_{column}']}")
        self.robot.sync_send_angles(self.angles[f"column_{column}"], 50)
        self._pump_off()
        self.robot.sync_send_angles(self.angles["home"], 50)
        logger.debug(f"Returned to home position")
    
    def give_player_puck(self, puck_no: int):
        logger.debug("Giving player a puck")
        angles = self._get_puck_angle('yellow', puck_no)
        logger.debug(f"Picking up yellow puck number {puck_no} at angles {angles}")
        self.robot.sync_send_angles(angles, 50)
        self._pump_on()
        logger.debug("Puck picked up, moving to player position")
        self.robot.sync_send_angles(self.angles["player_dropoff"], 50)
        logger.debug("At player position, releasing puck")
        self._pump_off()
        self.robot.sync_send_angles(self.angles["home"], 50)
        logger.debug("Returned to home position")

    def _get_puck_angle(self, color: str, puck_no: int):
        """
        given that as we take pucks the height changes, we need to adjust the angle accordingly.
        Get the angles for picking up a puck of a given color, given that it's the nth puck.
        """
        key = f"{color}_puck_width"
        angles = self.angles[color]
        angles[5] -= self.angles[key] * puck_no
        return angles
    
        # Method to turn on the pump
    def _pump_on(self):
        # close to exust the valve
        self.robot.set_basic_output(self.valve_pin, 1)
        logger.debug(f"exhust closed")
        # start pump
        self.robot.set_basic_output(self.pump_pin, 0)
        logger.debug(f"pump on")
        time.sleep(self.VACCUM_BUILD_TIME)

    # Method to turn off the pump
    def _pump_off(self):
        # Close the solenoid valve
        self.robot.set_basic_output(self.pump_pin, 1)
        logger.debug(f"pump off")
        # Start the exhaust valve
        self.robot.set_basic_output(self.valve_pin, 0)
        logger.debug(f"exhaust open")
        time.sleep(self.VACCUM_DROP_TIME)

    def reset(self):
        self.robot.sync_send_angles(self.angles["home"], 50)
        logger.debug("Robot reset to home position")

if __name__ == "__main__":
    robot = RobotCommunicator()
    robot.drop_piece(3, 0)  # Drop a puck in column 3, first puck