# backend/state/game_state.py
from fastapi import HTTPException
from backend.models.table import Table
from backend.models.round import RoundManager, Status, Action
# グローバルに保持
game_state = None

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(table = self.table)

        self.result: Status = None

    def start_new_hand(self):
        """新しくハンドをスタートしてAIも最初にアクションしておく。"""
        if self.table.seats[0].player is None:
            self.table.assign_players_to_seats()

        self.round_manager.reset()
        self.table.start_hand()
        self.round_manager.action_order.reset()
        
        self.result = self.round_manager.step()

    def step(self):
        if self.result == Status.WAITING_FOR_AI:
            self.round_manager.step_apply_action()
            self.result = self.round_manager.status

        elif self.result == Status.WAITING_FOR_HUMAN:
            self.get_state()

    def apply_action(self, action, amount=None):
        """プレイヤーからアクションを受け付け、AIも次に動く。"""
        self.round_manager.step_apply_action(player_action=action, amount=amount)
        self.result = self.round_manager.status

        if self.result == Status.waiting_step(self.result):
            self.result = self.round_manager.step()
        
    def state_manager(self):
        if self.result == Status.WAITING_FOR_HUMAN:
            return self.get_state()
        if self.result == Status.WAITING_FOR_AI:
            return self.round_manager.step_apply_action()

    def get_state(self):
        """APIレスポンス用にゲーム情報を整理して取得。"""
        return {
            "status": self.result.value,
            "table": self.table.to_dict(),  # table.to_dict を実装してあるという前提
        }

    def is_waiting(self) -> bool:
        return Status.is_waiting(self.status)


# アプリケーション起動時に１つだけ用意しておく
game_state = GameState()
