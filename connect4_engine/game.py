from typing import Callable
from core.board import Board
from core.ai import AIPlayerDummy
from hardware.robot import IRobot
from hardware.arduino import IArduino
class Connect4Game:

    PLAYER_COLOR = Board.P_RED
    AI_COLOR = Board.P_YELLOW

    def __init__(self,
                 arduino: IArduino,
                 robot: IRobot,
                 player_starts: bool = False):
        
        self.board = Board()
        self.ai = AIPlayerDummy()
        self.robot = robot
        self.arduino = arduino
        self.arduino.set_on_player_moved_callback(self.piece_dropped_in_board)
        self.turn = 'ai'

        # possibly setup robot and arduino if not done elsewhere

        # initial turn
        if player_starts:
            self.turn = 'player'
            self.robot.give_player_puck()

    def game_over(self, message: str):
        """
        Handle game over scenario
        """
        print(message)
        self.board.display()
        self.arduino.reset()
        self.robot.reset()
        self.board.reset()
    
    def piece_dropped_in_board(self, column: int):
        """
        arduino callback when a piece is dropped by the player.
        note we're only updating the board when the ledstrip detects a piece drop,
        not just when we tell the robot to insert it there.
        """
        if self.turn == 'ai':
            self.board.drop_piece(column, Connect4Game.AI_COLOR)
            if self.check_winner():
                return
            self.turn = 'player'
        else:
            self.board.drop_piece(column, Connect4Game.PLAYER_COLOR)
            if self.check_winner():
                return
            self.turn = 'ai'
            self.ai_turn()

    def check_winner(self):
        """
        unoptimized winner check after each move. checks for both players.
        """
        if self.board.is_player_winner(Connect4Game.PLAYER_COLOR):
            self.game_over("Player wins!")
            return True
        if self.board.is_player_winner(Connect4Game.AI_COLOR):
            self.game_over("AI wins!")
            return True
        elif self.board.is_draw():
            self.game_over("It's a draw!")
            return True
        return False
    
    def ai_turn(self):
        # AI's turn 
        ai_column = self.ai.choose_move(self.board)
        self.robot.drop_piece(ai_column)
        self.robot.give_player_puck()
    