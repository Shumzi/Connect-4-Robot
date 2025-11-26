from abc import ABC, abstractmethod

class IRobot(ABC):

    @abstractmethod
    def drop_piece(self, column: int):
        pass
    
    @abstractmethod
    def give_player_puck(self):
        pass

    @abstractmethod
    def reset(self):
        pass