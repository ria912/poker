# state/game_state.py
from backend.models.table import Table
from backend.models.round import RoundManager
from backend.models.action import Action
from backend.models.enum import Status
from fastapi import HTTPException

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)

    def start_new_hand(self):
        if self.table.seats is None:
            self.table.seat_assign_players()

        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager.start_round()
        while True:
            self.round_manager.step_one_action()
            if self.round_manager.status == Status.WAITING_FOR_HUMAN:
                return self._make_waiting_response()
            elif self.round_manager.status == Status.RUNNING:
                return self.get_state()
            elif self.round_manager.status == Status.HAND_OVER:
                break

        return {"status": self.round_manager.status.value, "state": self.table.to_dict()}

    def _make_waiting_response(self):
        if self.round_manager.current_player.is_human:
            return {
                "status": Status.WAITING_FOR_HUMAN.value,
                "state": self.table.to_dict(),
                "legal_actions": Action.get_legal_actions(self.round_manager.current_player, self.table),
            }
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected human: {self.round_manager.currentplayer}")

    def receive_human_action(self, action: str, amount: int):
        self.round_manager.current_player.set_pending_action(Action(action), amount)  # アクションセット
        self.round_manager.step_apply_action()  # step_aplly_actionで decide_action 呼び出し
        if self.round_manager.status == Status.WAITING_FOR_HUMAN:
            return self._make_waiting_response()
        elif self.round_manager.status == Status.HAND_OVER:
            return self.get_state()
        elif self.round_manager.status == Status.RUNNING:
            return self.round_manager.step_one_action()
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected status: {self.round_manager.status}")

    def get_state(self):
        return {
            "status": self.round_manager.status.value,
            "state": self.table.to_dict(),
        }

    @property
    def action_log(self):
        return self.round_manager.action_log

# グローバルなゲーム状態（FastAPIエンドポイントで利用）
game_state = GameState()