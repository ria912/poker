# backend/state/single_game_state.py
from backend.models.table import Table
from backend.models.round import OrderManager
from backend.models.action import Action
from backend.models.enum import Status
from backend.schemas import GameStateResponse, PlayerInfo
from fastapi import HTTPException
from typing import List, Optional

class GameState:
    def __init__(self):
        self.table = Table()
        self.order_manager = OrderManager(self.table)
        self.table.assign_players_to_seats()

    def start_new_hand(self):
        self.table.reset()
        self.order_manager.reset()

        # AIプレイヤーが先なら自動で処理
        while True:
            player = self.order_manager.get_next_player()
            if player is None:
                break
            if player.is_human:
                break
            player.act()  # AIのアクション（act() はAI側で定義）
            self.order_manager.proceed()

    def receive_human_action(self, action: Action, amount: int = None):
        current = self.order_manager.get_next_player()
        if not current or not current.is_human:
            raise HTTPException(status_code=400, detail="現在あなたのターンではありません。")

        action, amount = current.receive_action(action)
        current.decide_action
        self.order_manager.proceed()

        # AIのターンを処理
        while True:
            player = self.order_manager.get_next_player()
            if player is None:
                break
            if player.is_human:
                break
            player.act()
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
        current_player = self.order_manager.get_next_player()
        current_turn = current_player.name if current_player else None

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
