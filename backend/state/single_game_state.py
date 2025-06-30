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

        self.action_log = []

    def start_new_hand(self):
        self.table.reset()
        self.table.starting_new_hand()
        self.round_manager.reset()
        self._process_ai_until_human()

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
            if not current_seat or current_seat.player.is_human:
                return self.get_state()
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
game_state = GameState()
