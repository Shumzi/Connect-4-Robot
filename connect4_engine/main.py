from game import Connect4Game
from hardware.mock import ArduinoDummy, RobotDummy
from hardware.robot import RobotCommunicator
from hardware.arduino import ArduinoCommunicator
import serial
from core.ai import AIPascalPons, main
from core.board import Board

class Main:
    def __init__(self):
        self.arduino = ArduinoCommunicator(ser=serial.Serial("COM7", 115200))
        self.robot = RobotCommunicator("COM11")
        # self.arduino = ArduinoDummy()
        # self.robot = RobotDummy(arduino=self.arduino)
        self.game = Connect4Game(arduino=self.arduino, robot=self.robot, player_starts=False)
    
    def play(self):
        # self.game.game_start()
        # self.arduino.puck_dropped_in_col(3)
        # self.arduino.puck_dropped_in_col(2)
        # self.arduino.puck_dropped_in_col(3)
        # self.arduino.puck_dropped_in_col(0)

        self.arduino.read_loop()  # in real hardware this would be the only thing running.

    
if __name__ == "__main__":
    m = Main()
    m.play()
    # # m.play()
    # Example usage
    # main()
    # board = Board()
    # ai_player = AIPascalPons(ai_executable_path="./connect4_engine/core/connect4ai/connect4/c4solver")
    # move = ai_player.choose_move(board)
    # print(f"AI chose column: {move}")