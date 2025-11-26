from game import Connect4Game
from hardware.mock import ArduinoDummy, RobotDummy

class Main:
    def __init__(self):
        self.arduino = ArduinoDummy()
        self.robot = RobotDummy(self.arduino)
        self.game = Connect4Game(arduino=self.arduino, robot=self.robot, player_starts=True)
    
    def play(self):
        
        # self.arduino.read_loop()- in real hardware this would be the only thing running.
        # Example moves
        pass
        
        # self.game.board.display()
    
if __name__ == "__main__":
    m = Main()
    m.play()