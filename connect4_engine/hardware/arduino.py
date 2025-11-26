from typing import Callable

from abc import ABC, abstractmethod

import serial

class IArduino(ABC):

    @abstractmethod
    def set_on_puck_dropped_callback(self, callback: Callable[[int], None]):
        pass

    @abstractmethod
    def reset(self):
        pass

class ArduinoCommunicator(IArduino):
    def __init__(self, ser, logger):
        self._ser = ser
        self._logger = logger
        self._accept_moves = False          # only accept drops when game is active

    def set_on_puck_dropped_callback(self, callback: Callable[[int], None]):
        self._on_puck_dropped = callback

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

    def reset(self):
        msg = f"RESET\n"
        self._logger.info(f"Sending to Arduino: {msg.strip()}")
        self._ser.write(msg.encode("utf-8"))
        self._accept_moves = False
