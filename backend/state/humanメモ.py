 # backend/state/single_game_state.py
from backend.models.table import Table, Seat
from backend.models.human_player import HumanPlayer
from backend.models.round import RoundManager
from backend.models.action import Action
from backend.models.enum import Status
from backend.schemas import GameStateResponse, PlayerInfo
from fastapi import HTTPException
from typing import List, Optional

class GameState:
    def __init__(self):
        self.table = Table()
        self.table.assign_players_to_seats()
        self.round_manager = RoundManager(self.table)
        self.status = Status.ROUND_CONTINUE

        self.action_log = []

    def receive_human_action(self, action: Action, amount: Optional[int] = None):
        current_seat: Optional[Seat] = self.round_manager.get_current_seat()
        if not current_seat or not current_seat.player.is_human:
            raise HTTPException(status_code=400, detail="現在プレイヤーのターンではありません。")

        player = current_seat.player
        HumanPlayer.receive_action(player, action, amount)
        
        self.round_manager.proceed()
        self._process_ai_until_human()

    def _process_ai_until_human(self):
        while True:
            current_seat = self.round_manager.get_current_seat()
            if not current_seat or not current_seat.player.is_human:
                self.round_manager.proceed()
            elif current_seat.player.is_human:
                self.status