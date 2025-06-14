# backend/state/game_state.py

from fastapi import HTTPException
from backend.models.table import Table
from backend.models.round import RoundManager, Status

# グローバルに保持
game_state = None


class GameState:
    """ゲームの状態管理クラス"""

    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(table = self.table)
        self.table.assign_players_to_seats()

        self.result: Status = None

    def start_new_hand(self):
        """新しくハンドをスタートしてAIも最初にアクションしておく。"""
        self.table.reset_for_new_hand()
        self.round_manager.start_new_round()
        self.result = self.round_manager.status

        if self.round_manager.status == Status.WAITING_FOR_AI:
            self.round_manager.step_apply_action()
            self.result = self.round_manager.status

    def receive_human_action(self, action, amount=None):
        """プレイヤーからアクションを受け付け、AIも次に動く。"""
        if self.result == Status.WAITING_FOR_HUMAN:
            self.round_manager.step_apply_action(player_action=action, amount=amount)
            self.result = self.round_manager.status

            if self.result == Status.WAITING_FOR_AI:
                self.round_manager.step_apply_action()
                self.result = self.round_manager.status

        else:
            raise HTTPException(
                status_code=400,
                detail=f"現在プレイヤーのアクションフェイズじゃありません。status = {self.status}",
            )

    def get_state(self):
        """APIレスポンス用にゲーム情報を整理して取得。"""
        return {
            "status": self.status.value,
            "table": self.table.to_dict(),  # table.to_dict を実装してあるという前提
        }

    def is_waiting(self) -> bool:
        return Status.is_waiting(self.status)


    def is_terminal(self) -> bool:
        return Status.is_terminal(self.status)


# アプリケーション起動時に１つだけ用意しておく
game_state = GameState()
