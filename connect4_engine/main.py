from game import Connect4Game
from hardware.mock import ArduinoDummy, RobotDummy
from hardware.robot import RobotCommunicator
from hardware.arduino import ArduinoCommunicator
import serial

class Main:
    def __init__(self):
        self.arduino = ArduinoCommunicator(ser=serial.Serial('COM7', 115200))
        self.robot = RobotCommunicator()
        self.game = Connect4Game(arduino=self.arduino, robot=self.robot, player_starts=False)
    
    def play(self):
        
        self.arduino.read_loop()  # in real hardware this would be the only thing running.

    
if __name__ == "__main__":
    m = Main()
    m.play()
    # m.play()