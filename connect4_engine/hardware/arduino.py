from typing import Callable

from abc import ABC, abstractmethod


class IArduino(ABC):

    @abstractmethod
    def set_on_player_moved_callback(self, callback: Callable[[int], None]):
        pass

    @abstractmethod
    def reset(self):
        pass