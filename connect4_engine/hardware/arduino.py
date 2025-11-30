from typing import Callable

from abc import ABC, abstractmethod
from utils.logger import logger
import serial

class IArduino(ABC):

    @abstractmethod
    def set_on_puck_dropped_callback(self, callback: Callable[[int], None]):
        pass
    
    @abstractmethod
    def set_game_start_callback(self, callback: Callable[[], None]):
        pass
    
    @abstractmethod
    def reset(self):
        pass

class ArduinoCommunicator(IArduino):
    def __init__(self, ser):
        self._ser = ser
        self._logger = logger
        self._accept_moves = False          # only accept drops when game is active

    def set_on_puck_dropped_callback(self, callback: Callable[[int], None]):
        self._on_puck_dropped = callback
    
    def set_game_start_callback(self, callback: Callable[[], None]):
        self.game_start = callback

    def read_loop(self):
        self._logger.info("Arduino read loop started")
        while True:
            line = self._ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            self._logger.debug(f"Serial line: {line}")
            self._handle_line(line)

    def _handle_line(self, line: str):
        parts = line.split()

        if parts[0] == "START":
            self.handle_start()

        elif parts[0] == "DROP" and self._accept_moves and len(parts) == 2:
            return self.handle_drop(line, parts)
        elif parts[0] == "LOG":
            self._logger.info(f"Arduino log: {' '.join(parts[1:])}")

    def handle_drop(self, line, parts):
        try:
            col = int(parts[1])
        except ValueError:
            self._logger.warning(f"Invalid column in line: {line}")
            return
        self._logger.info(f"Detected puck in column {col}")
        self._on_puck_dropped(col)

    def handle_start(self):
        self._logger.info("Start signal from Arduino")
        self._accept_moves = True
        self.game_start()

    def reset(self):
        msg = f"RESET\n"
        self._logger.info(f"Sending to Arduino: {msg.strip()}")
        self._ser.write(msg.encode("utf-8"))
        self._accept_moves = False

if __name__ == "__main__":
    arduino = ArduinoCommunicator(ser=serial.Serial('COM3', 115200))
    arduino.read_loop()