# backend/state/single_game_state.py
from backend.models.table import Table, Seat
from backend.models.human_player import HumanPlayer
from backend.models.round import OrderManager
from backend.models.action import Action
from backend.models.enum import Status
from backend.schemas import GameStateResponse, PlayerInfo
from fastapi import HTTPException
from typing import List, Optional

class GameState:
    def __init__(self):
        self.table = Table()
        self.table.assign_players_to_seats()
        self.order_manager = OrderManager(self.table)

    def start_new_hand(self):
        self.table.reset()
        self.order_manager.reset()
        self._process_ai_until_human()

    def receive_human_action(self, action: Action, amount: int = None):
        current_seat: Optional[Seat] = self.order_manager.get_current_seat()
        if not current_seat or not current_seat.player.is_human:
            raise HTTPException(status_code=400, detail="現在あなたのターンではありません。")

        player = current_seat.player
        HumanPlayer.receive_action(player, action, amount)
        
        self.order_manager.proceed()
        self._process_ai_until_human()

    def _process_ai_until_human(self):
        while True:
            current_seat = self.order_manager.get_current_seat()
            if not current_seat or current_seat.player.is_human:
                break
            self.order_manager.proceed()


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
                ))

        # 現在のアクションプレイヤー（Optional）
        current = self.order_manager.get_current_seat()
        current_turn = current.player.name if current else None

        return GameStateResponse(
            round=self.table.round,
            pot=self.table.pot,
            board=self.table.board,
            seats=seat_infos,
            current_turn=current_turn,
            status=self.order_manager.round_logic.status.value
        )

# アプリ側で使えるようにインスタンス化
game_state = GameState()
