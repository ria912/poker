# tests/test_run.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.table import Table
from models.round_manager import RoundManager
from models.ai_player import AIPlayer
from models.auto_human_player import AutoHumanPlayer

def _seat_assign_players(table):
    players = [AutoHumanPlayer(name="YOU")]
    for i in range(1, len(table.seats)):
        players.append(AIPlayer(name=f"AI{i}"))
    for i, p in enumerate(players):
        table.seats[i] = p

def main():
    table = Table()
    _seat_assign_players(table)
    table.start_hand()
    round_manager = RoundManager(table)

    print("=== プリフロップ開始 ===")
    from pprint import pprint
    print(table.to_dict())

    while round_manager.street != "showdown":
        round_manager.proceed()
        print(f"=== {round_manager.street.upper()} ===")
        print(table.to_dict())

    round_manager.proceed()

if __name__ == "__main__":
    main()
