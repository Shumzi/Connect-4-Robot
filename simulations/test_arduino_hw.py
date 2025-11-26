from connect4_engine.hardware.arduino import ArduinoCommunicator
from connect4_engine.hardware.mock import RobotDummySerial
from connect4_engine.game import Connect4Game
from connect4_engine.utils.logger import logger

class MockSerial:
    def __init__(self):
        self.lines = []
        self.write_log = []

    def push_line(self, line: str):
        self.lines.append(line + "\n")

    def readline(self):
        if self.lines:
            return self.lines.pop(0).encode("utf-8")
        return b""

    def write(self, data: bytes):
        self.write_log.append(data.decode("utf-8").strip())
        logger.info(f"MockSerial wrote: {data.decode('utf-8').strip()}")

def test_puck_drop_triggers_game_logic():
    events = []

    def on_puck_dropped(col: int):
        events.append(col)

    mock_ser = MockSerial()
    arduino = ArduinoCommunicator(
        ser=mock_ser,
        logger=logger
    )
    robot = RobotDummySerial(mock_ser)
    game = Connect4Game(arduino=arduino, robot=robot, player_starts=True)
    # Feed fake serial lines
    mock_ser.push_line("START")
    mock_ser.push_line("DROP 3")
    
    arduino.read_loop()

    assert events == [3, 5]

if __name__ == "__main__":
    test_puck_drop_triggers_game_logic()