# backend/state/single_game_state_ai.py
from backend.models.table import Table, Seat
from backend.models.round import RoundManager
from backend.models.action import Action
from backend.models.enum import Status
from backend.schemas import GameStateResponse, PlayerInfo
from fastapi import HTTPException
from typing import List, Optional

class AIGameState:
    def __init__(self):
        self.table = Table()
        self.table.assign_players_to_seats(human_included=False)
        self.round_manager = RoundManager(self.table)
        self.status = Status.ROUND_CONTINUE

        self.action_log = []

    def start_new_hand(self):
        self.table.reset()
        self.table.starting_new_hand()
        self.round_manager.reset()
        self._run_full_hand()
    
    def _run_full_hand(self):
        while True:
            current = self.round_manager.get_current_seat()
            if not current:
                status = self.round_manager.proceed()
                self.status = status
                if status == Status.HAND_OVER:
                    return self.get_state()
            else:
                self.round_manager.proceed()

    def get_state(self) -> GameStateResponse:
        # 座席情報をPlayerInfoに変換
        seat_infos: List[PlayerInfo] = []
        for seat in self.table.seats:
            player = seat.player
            if player:
                seat_infos.append(PlayerInfo(
                    name=player.name,
                    position=player.position,
                    stack=player.stack,
                    bet_total=player.bet_total,
                    is_active=player.is_active,
                    last_action=player.last_action,
                    folded=player.folded,
                    all_in=player.all_in,
                ))

        # 現在のアクションプレイヤー（Optional）
        current = self.round_manager.get_current_seat()
        current_turn = current.player.name if current else None

        return GameStateResponse(
            round=self.table.round.value,
            pot=self.table.pot,
            board=self.table.board,
            seats=seat_infos,
            current_turn=current_turn,
            status=self.round_manager.status.value
        )

# アプリ側で使えるようにインスタンス化
ai_game_state = AIGameState()
