from .board import Board
from connect4_engine.utils.logger import logger
from time import sleep
class AIPlayerDummy:
    def __init__(self):
        pass

    def choose_move(self, board: Board):
        """
        Choose a move based on a simple strategy: pick the first available column.
        """
        logger.debug("AI is choosing a move...")
        sleep(3)  # simulate thinking time
        available_columns = board.available_actions()
        if available_columns:
            return available_columns[0]
        else:
            raise Exception("No available moves left.")