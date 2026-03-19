from abc import ABC, abstractmethod

class Game(ABC):
    """
    Abstract base class for games.
    """
    @abstractmethod
    def get_game_status(self):
        """
        Get the current game status.
        Returns a dictionary with relevant game information.
        """
        pass

    @abstractmethod
    def make_move(self, row, col):
        """
        Make a move at the specified position.
        """
        pass

class Player(ABC):
    """
    Abstract base class for players. Subclasses can implement different types of players
    (e.g., CLI input, AI algorithms).
    """
    def __init__(self, player_id):
        self.player_id = player_id

    @abstractmethod
    def get_move(self, game_status):
        """
        Get the next move from the player based on the current game status.
        Returns a tuple (row, col) for the move.
        """
        pass

class GameManager:
    """
    Manages the game flow between two players.
    """
    def __init__(self, game, player1, player2):
        self.game = game
        self.players = {player1.symbol: player1, player2.symbol: player2}

    def play(self):
        """
        Play the game until it's over, alternating turns between players.
        Returns the winner symbol or None for a draw.
        """
        while not self.game.game_over:
            current_player = self.players[self.game.current_player]
            status = self.game.get_game_status()
            try:
                move = current_player.get_move(status)
                self.game.make_move(*move)
            except ValueError as e:
                print(f"Invalid move by {current_player.symbol}: {e}")
                # In a real implementation, you might want to handle invalid moves differently
                continue
        return self.game.winner