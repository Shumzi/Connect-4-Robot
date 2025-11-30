from connect4_engine.game import Connect4Game
from connect4_engine.hardware.mock import ArduinoDummy, RobotDummy

class Main:
    def __init__(self):
        self.arduino = ArduinoDummy()
        self.robot = RobotDummy(self.arduino)
        self.game = Connect4Game(arduino=self.arduino, robot=self.robot, player_starts=True)
    
    def play(self):
        
        # self.arduino.read_loop()- in real hardware this would be the only thing running.
        # Example moves
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        # player should win here
        # game should reset here
        self.game.board.display()
        self.arduino.puck_dropped_in_col(2)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(3)
        self.arduino.puck_dropped_in_col(5)
        # ai should win here
        # game should reset here
        self.game.board.display()
    
if __name__ == "__main__":
    m = Main()
    m.play()