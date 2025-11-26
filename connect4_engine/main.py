from game import Connect4Game
from hardware.mock import ArduinoDummy, RobotDummy

class Main:
    def __init__(self):
        self.arduino = ArduinoDummy()
        self.robot = RobotDummy(self.arduino)
        self.game = Connect4Game(arduino=self.arduino, robot=self.robot, player_starts=True)
    
    def play(self):
        # Example moves
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        
        # self.game.board.display()
    
if __name__ == "__main__":
    m = Main()
    m.play()