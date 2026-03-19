from .tic_tac_toe import TicTacToeBoard
from .tic_tac_toe_constants import X, O, EMPTY
from game_manager import Player

class TicTacToePlayer(Player):
    """
    Abstract base class for Tic Tac Toe players. Sets the symbol based on player_id.
    """
    def __init__(self, player_id):
        super().__init__(player_id)
        self.symbol = X if player_id == 1 else O

class RandomPlayer(TicTacToePlayer):
    """
    A player that makes random valid moves.
    """
    def __init__(self, player_id):
        super().__init__(player_id)
    def get_move(self, game_status):
        import random
        return random.choice(game_status.get_valid_moves())

class SequentialPlayer(TicTacToePlayer):
    """
    A player that makes moves in a sequential order (top-left to bottom-right).
    """
    def __init__(self, player_id):
        super().__init__(player_id)
    def get_move(self, game_status):
        try:
            return game_status.get_valid_moves()[0]
        except IndexError:
            raise ValueError("No valid moves available")

class MinMaxPlayer(TicTacToePlayer):
    """
    A player that uses the MinMax algorithm to choose the optimal move.
    Assumes perfect play and evaluates all possible game states.
    """
    def __init__(self, player_id):
        super().__init__(player_id)
        self.opponent = O if self.symbol == X else X

    BOARD_SCORES = dict()

    def get_move(self, game_status):
        best_score = -float('inf')
        best_move = None
        for move in game_status.get_valid_moves():
            new_board = game_status.copy_and_move(move[0], move[1], self.symbol)
            score = None
            key = self.opponent + str(new_board)
            if key in self.BOARD_SCORES:
                score = self.BOARD_SCORES[key]
            else:
                score = self.minimax(new_board, self.opponent)
                self.BOARD_SCORES[key] = score
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, board, player):
        winner = board.check_winner()
        if winner:
            return 10 if winner == self.symbol else -10
        elif board.is_full():
            return 0
    
        eval_extreme = -float('inf') if player == self.symbol else float('inf')
        for move in board.get_valid_moves():
            new_board = board.copy_and_move(move[0], move[1], player)
            eval = self.minimax(new_board, O if player == X else X)
            eval_extreme = max(eval_extreme, eval) if player == self.symbol else min(eval_extreme, eval)
        return eval_extreme