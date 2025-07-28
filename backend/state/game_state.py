# backend/state/game_state.py

from backend.models.table import Table
from backend.models.player import Player, PlayerType
from backend.models.enum import Round
from backend.services.round_manager import RoundManager
from backend.utils.id_generator import generate_uuid


class GameState:
    def __init__(self, num_players: int = 6):
        assert 2 <= num_players <= 6, "プレイヤー数は2〜6人です"

        # プレイヤー準備
        players = []
        for i in range(num_players):
            player_type = PlayerType.HUMAN if i == 0 else PlayerType.AI
            players.append(Player(name=f"Player {i+1}", stack=1000, player_type=player_type))

        self.table = Table(players)
        self.round_manager = RoundManager(self.table)

    def run_hand(self):
        self.table.round = Round.PREFLOP
        self.table.hand_id = generate_uuid()
        self.round_manager.play_round()

    def to_dict(self):
        return {
            "hand_id": self.table.hand_id,
            "round": self.table.round.name,
            "board": [card for card in self.table.board],
            "pot": self.table.pot,
            "players": [seat.to_dict() for seat in self.table.seats],
            "action_log": self.table.action_log,
        }