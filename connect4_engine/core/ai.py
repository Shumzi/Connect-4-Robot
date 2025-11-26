from .board import Board

class AIPlayerDummy:
    def __init__(self):
        pass

    def choose_move(self, board: Board):
        """
        Choose a move based on a simple strategy: pick the first available column.
        """
        available_columns = board.available_actions()
        if available_columns:
            return available_columns[0]
        else:
            raise Exception("No available moves left.")