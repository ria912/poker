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
        return self._step_until_response()
        
    def _step_untill_response(self):
        status = self.round_manager.advance_until_human_or_end()
        while True:
            if status == Status.WAITING_FOR_HUMAN:
                return self._make_waiting_response()
            elif status == Status.HAND_OVER:
                return self._build_response(Status.HAND_OVER)
            elif self.round_manager.status == Status.RUNNING:
                self.round_manager.step_one_action()
            else:
                raise HTTPException(500, f"Unexpected status: {status}")
            
    def _make_waiting_response(self):
        if self.round_manager.current_player.is_human:
            return self._build_response(Status.WAITING_FOR_HUMAN, include_legal_actions=True)
        else:
            raise HTTPException(500, f"Unexpected human: {self.round_manager.current_player}")

    def receive_human_action(self, action: str, amount: int):
        self.round_manager.current_player.set_pending_action(Action(action), amount)  # アクションセット
        self.round_manager.step_apply_action()  # step_aplly_actionで decide_action 呼び出し
        return self._step_until_response()

    def _build_response(self, status: Status, include_legal_actions=False):
        response = {
            "status": status.value,
            "state": self.table.to_dict(),
        }
    if include_legal_actions:
        response["legal_actions"] = Action.get_legal_actions(self.round_manager.current_player, self.table)
    return response
# グローバルなゲーム状態（FastAPIエンドポイントで利用）
game_state = GameState()