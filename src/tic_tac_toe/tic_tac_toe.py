from .tic_tac_toe_constants import X, O, EMPTY
from game_manager import Game

class TicTacToeBoard:
    """
    Represents the game board for Tic Tac Toe.
    """
    def __init__(self, board=None):
        self.__board = EMPTY * 9 if board is None else str(board)

    def __getitem__(self, idx):
        row, col = idx
        return self.__board[row * 3 + col]

    def __str__(self):
        return self.__board

    def move(self, row, col, symbol):
        if symbol not in [X, O]:
            raise ValueError("Symbol must be 'X' or 'O'")
        if symbol == X and self.__board.count(X) > self.__board.count(O):
            raise ValueError("It's O's turn")
        if symbol == O and self.__board.count(O) >= self.__board.count(X):
            raise ValueError("It's X's turn")

        idx = row * 3 + col
        if self.__board[idx] == EMPTY:
            self.__board = self.__board[:idx] + symbol + self.__board[idx + 1:]
        else:
            raise ValueError("Cell is already occupied")

    def copy_and_move(self, row, col, symbol):
        import copy
        new_board = TicTacToeBoard(copy.deepcopy(self.__board))
        new_board.move(row, col, symbol)
        return new_board

    def is_full(self):
        return EMPTY not in self.__board
    
    def check_winner(self)-> str | None:
        for i in range(3):
            if self[i, 0] == self[i, 1] == self[i, 2] != EMPTY:
                return self[i, 0]
            if self[0, i] == self[1, i] == self[2, i] != EMPTY:
                return self[0, i]
        if self[0, 0] == self[1, 1] == self[2, 2] != EMPTY:
            return self[0, 0]
        if self[0, 2] == self[1, 1] == self[2, 0] != EMPTY:
            return self[0, 2]
        return None
    
    def get_valid_moves(self):
        return [(i, j) for i in range(3) for j in range(3) if self[i, j] == EMPTY]

class TicTacToe(Game):
    def __init__(self, name):
        """
        Initialize the Tic Tac Toe game with a name.
        """
        self.name = name
        self.board = TicTacToeBoard()
        self.current_player = X
        self.game_over = False
        self.winner = None

    def get_game_status(self):
        return self.board

    def make_move(self, row, col):
        """
        Make a move on the board at the specified row and column.
        """
        # Stub implementation: check if move is valid, update board, switch player, check for win
        if self.board[row, col] == EMPTY and not self.game_over:
            self.board.move(row, col, self.current_player)
            self.winner = self.board.check_winner()
            if self.winner:
                self.game_over = True
            elif self.board.is_full():
                self.game_over = True
            else:
                self.current_player = O if self.current_player == X else X
        else:
            raise ValueError("Invalid move")