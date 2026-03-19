from tic_tac_toe import (
    TicTacToe,
    RandomPlayer as TTT_RandomPlayer,
    SequentialPlayer as TTT_SequentialPlayer,
    MinMaxPlayer as TTT_MinMaxPlayer
)
from game_manager import GameManager
import matplotlib.pyplot as plt
import logging
from itertools import combinations
from collections import defaultdict
import os
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
LOGS_DIR = 'logs'

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Game and player definitions
GAMES = {
    'tic_tac_toe': {
        'class': TicTacToe,
        'players': [TTT_RandomPlayer, TTT_SequentialPlayer, TTT_MinMaxPlayer]
    }
}

# Set up logging to file
logging.basicConfig(filename=f'{LOGS_DIR}/game_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def plot_tournament_results(wins, game_class, num_players, total_games):
    """
    Plot the tournament results using matplotlib.
    """
    # Create a pretty graph
    players = sorted(wins.keys(), key=lambda p: wins[p]['wins'])
    y = range(len(players))
    
    plt.figure(figsize=(12, 8))
    for i, player in enumerate(players):
        plt.barh(i, wins[player]['wins'], color='green', label='Wins' if i == 0 else "", edgecolor='black', linewidth=1.2)
        plt.barh(i, wins[player]['losses'], left=wins[player]['wins'], color='red', label='Losses' if i == 0 else "", edgecolor='black', linewidth=1.2)
        plt.barh(i, wins[player]['draws'], left=wins[player]['wins'] + wins[player]['losses'], color='grey', label='Draws' if i == 0 else "", edgecolor='black', linewidth=1.2)
    
    plt.yticks(y, players)
    plt.title(f'{game_class.__name__} Tournament Results: {num_players} Players ({total_games} total games)', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Games', fontsize=14)
    plt.ylabel('Player', fontsize=14)
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add value labels on bars
    for i, player in enumerate(players):
        left = 0
        for category, color in [('wins', 'green'), ('losses', 'red'), ('draws', 'grey')]:
            width = wins[player][category]
            if width > 0:
                plt.text(left + width / 2, i, str(width), ha='center', va='center', fontsize=10, fontweight='bold', color='white')
            left += width
    
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(f'{LOGS_DIR}/tournament_results.png')
    plt.show()

def main(game_class, player_classes, num_games_per_pair=10, num_threads=1):
    """
    Dynamic main function to run a tournament between multiple players.
    Uses round-robin with num_games_per_pair games per pair.
    
    Args:
        game_class: The game class to instantiate (e.g., TicTacToe)
        player_classes: List of player classes (2 or more)
        num_games_per_pair: Number of games each pair plays (for n != 3)
        num_threads: Number of worker threads to use for running games (default: 1)
    """
    start_time = time.perf_counter()
    print(f"[TIMING] main() start: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if len(player_classes) < 2:
        raise ValueError("At least 2 players are required.")
    
    num_players = len(player_classes)
    match_ups = [(p1, p2, num_games_per_pair) for p1, p2 in combinations(player_classes, 2)]
    total_games = len(match_ups) * num_games_per_pair
    
    print(f"Running tournament: {num_players} players, total {total_games} games")
    
    # Initialize win counters
    wins = {player_class.__name__: {'wins': 0, 'losses': 0, 'draws': 0} for player_class in player_classes}

    game_count = 0
    count_lock = threading.Lock()

    def _play_single_game(p1_class, p2_class, game_num, matchup):
        # Create a new game instance
        game = game_class(f"{matchup} - Game {game_num}")

        # Create players with symbols
        player_1 = p1_class(game_num % 2)
        player_2 = p2_class(1 - (game_num % 2))

        # Create game manager
        game_manager = GameManager(game, player_1, player_2)

        # Play the game silently
        winner = game_manager.play()
        return (p1_class.__name__, p2_class.__name__, winner, player_1.symbol, player_2.symbol)

    def _record_result(result):
        nonlocal game_count
        p1_name, p2_name, winner, sym1, sym2 = result

        with count_lock:
            if winner == sym1:
                wins[p1_name]['wins'] += 1
                wins[p2_name]['losses'] += 1
            elif winner == sym2:
                wins[p2_name]['wins'] += 1
                wins[p1_name]['losses'] += 1
            else:
                wins[p1_name]['draws'] += 1
                wins[p2_name]['draws'] += 1

            game_count += 1
            # Progress update
            if game_count % max(1, total_games // 10) == 0:
                print(f"Completed {game_count}/{total_games} games...")

    if num_threads > 1:
        print(f"Running with up to {num_threads} threads...")
        tasks = []
        for p1_class, p2_class, count in match_ups:
            matchup = f"{p1_class.__name__} vs {p2_class.__name__}"
            print(f"Starting matchup: {matchup} ({count} games)")
            for game_num in range(1, count + 1):
                tasks.append((p1_class, p2_class, game_num, matchup))

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(_play_single_game, *t) for t in tasks]
            for future in as_completed(futures):
                _record_result(future.result())
    else:
        for p1_class, p2_class, count in match_ups:
            matchup = f"{p1_class.__name__} vs {p2_class.__name__}"
            print(f"Starting matchup: {matchup} ({count} games)")

            for game_num in range(1, count + 1):
                result = _play_single_game(p1_class, p2_class, game_num, matchup)
                _record_result(result)

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[TIMING] main() end: {time.strftime('%Y-%m-%d %H:%M:%S')}, elapsed: {elapsed:.2f}s")
    logging.info(f"Tournament execution time: {elapsed:.2f}s")
    
    # Log final results
    logging.info(f"Tournament results for {game_class.__name__} with {num_players} players: {wins}")
    
    # Print final statistics
    print("\nFinal Tournament Results:")
    for player, stats in sorted(wins.items(), key=lambda x: x[1]['wins'], reverse=True):
        print(f"{player}: Wins={stats['wins']}, Losses={stats['losses']}, Draws={stats['draws']}")
    
    # Plot the results
    plot_tournament_results(wins, game_class, num_players, total_games)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a game tournament")
    parser.add_argument('--game', required=True, choices=GAMES.keys(), help='The game to play')
    parser.add_argument('--num_games', type=int, default=10, help='Number of games per pairing (default: 10)')
    parser.add_argument('--threads', type=int, default=1, help='Number of worker threads to use (default: 1)')

    args = parser.parse_args()
    
    game_class = GAMES[args.game]['class']
    player_classes = GAMES[args.game]['players']
    main(
        game_class=game_class,
        player_classes=player_classes,
        num_games_per_pair=args.num_games,
        num_threads=args.threads,
    )