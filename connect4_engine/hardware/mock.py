from typing import Callable, Optional
from .arduino import IArduino
from .robot import IRobot

class ArduinoDummy(IArduino):
    def __init__(self):
        self.on_player_moved_callback: Optional[Callable[[int], None]] = None

    def set_on_player_moved_callback(self, callback: Callable[[int], None]):
        """
        Set the callback function to be called when a player move is detected.
        """
        self.on_player_moved_callback = callback

    def puck_dropped_in_col(self, column: int):
        """
        Simulate listening for player moves from the Arduino hardware.
        in this case we just tell it which column to simulate a move for.
        actual implementation would involve serial communication and waiting for input from the Arduino.
        """
        print("Arduino listening for player moves...")
        # Simulate a player move for demonstration purposes
        simulated_player_move = column
        print(f"Simulated player move detected in column {simulated_player_move}")
        if self.on_player_moved_callback is None:
            # Contract violated: someone forgot to register the callback
            raise RuntimeError("on_player_moved callback not set; call set_on_player_moved() first")
        self.on_player_moved_callback(simulated_player_move)

    def reset(self):
        """
        Simulate resetting the Arduino hardware.
        """
        print("Arduino resetting solenoids...")

class RobotDummy(IRobot):
    def __init__(self, arduino: ArduinoDummy):
        self.arduino = arduino

    def drop_piece(self, column: int):
        """
        Simulate dropping a piece in the specified column using the robot hardware.
        """
        print(f"Robot dropping piece in column {column}")
        print(f"""    go to robot puck pile
    turn on pump
    move to column {column}
    turn off pump
    return to home position""")
        self.arduino.puck_dropped_in_col(column)

    def give_player_puck(self):
        """
        Simulate giving a puck to the player.
        """
        print("""Robot giving puck to player
    go to player puck pile
    turn on pump
    move to player pickup location
    turn off pump
    return to home position""")
        
    def reset(self):
        """
        Simulate resetting the robot hardware.
        """
        print("Robot resetting to home position...")
