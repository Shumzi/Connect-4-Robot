import pytest
import numpy as np

from connect4_engine.core.board import Board


def test_init():
    b = Board()
    assert b.width == 7
    assert b.height == 6
    assert b.grid.shape == (6, 7)
    assert np.all(b.grid == Board.P_EMPTY)


def test_available_actions_and_is_col_valid():
    b = Board()
    assert b.available_actions() == list(range(b.width))
    for col in range(b.width):
        assert b.is_col_valid(col)


def test_available_cell_and_drop_piece_and_full_column():
    b = Board()
    col = 3
    b.drop_piece(col, Board.P_RED)
    # first piece should be at row 0 (bottom)
    assert b.grid[0][col] == Board.P_RED
    assert b.available_cell(col) == 1

    # fill the column
    for _ in range(1, b.height):
        b.drop_piece(col, Board.P_YELLOW)
    assert b.available_cell(col) == -1
    assert not b.is_col_valid(col)
    with pytest.raises(Exception):
        b.drop_piece(col, Board.P_RED)


def test_horizontal_win():
    b = Board()
    for c in range(4):
        b.drop_piece(c, Board.P_RED)
    assert b.is_player_winner(Board.P_RED)


def test_vertical_win():
    b = Board()
    col = 0
    for _ in range(4):
        b.drop_piece(col, Board.P_YELLOW)
    assert b.is_player_winner(Board.P_YELLOW)


def test_leading_diagonal_win():
    b = Board()
    # set a leading diagonal (0,0),(1,1),(2,2),(3,3)
    for i in range(4):
        b.grid[i][i] = Board.P_RED
    assert b.is_player_winner(Board.P_RED)


def test_counter_diagonal_win():
    b = Board()
    # set counter diagonal positions (0,3),(1,2),(2,1),(3,0)
    coords = [(0, 3), (1, 2), (2, 1), (3, 0)]
    for r, c in coords:
        b.grid[r][c] = Board.P_YELLOW
    assert b.is_player_winner(Board.P_YELLOW)


def test_check_board_state_valid_and_should_have_pieces():
    b = Board()
    b.grid[0][0] = Board.P_RED
    b.grid[0][1] = Board.P_RED
    b.grid[0][2] = Board.P_YELLOW
    # red=2, yellow=1 -> valid
    assert b.check_board_state_valid() is True

    b.grid[0][3] = Board.P_RED
    # red=3, yellow=1 -> invalid (diff >= 2)
    assert b.check_board_state_valid() is False

    assert b.should_have_pieces(4) == (2, 1)
    assert b.should_have_pieces(5) == (2, 2)


def test_update_win_status_sets_done_and_winner():
    b = Board()
    for c in range(4):
        b.drop_piece(c, Board.P_RED)
    b.update()
    assert b.done is True
    assert b.winner == Board.P_RED


def test_reset():
    b = Board()
    b.drop_piece(0, Board.P_RED)
    b.reset()
    assert np.all(b.grid == Board.P_EMPTY)
    assert b.done is False
    assert b.winner is None
