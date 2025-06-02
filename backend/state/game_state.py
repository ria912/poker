# state/game_state.py
from models.table import Table
from models.round import RoundManager
from models.action import Action
from models.enum import Status
from fastapi import HTTPException

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)
        self.state = Status.RUNNING

    def start_new_hand(self):
        if self.table.seats is None:
            self.table.seat_assign_players()

        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager.start_round()
        while True:
            result = self.round_manager.step_one_action()
            if result == Status.WAITING_FOR_HUMAN:
                return self._make_waiting_response()
            elif result == Status.HAND_OVER:
                break

        return {"status": result, "state": self.table.to_dict()}

    def receive_human_action(self, action: str, amount: int):
        human = next(p for p in self.table.seats if p and p.is_human)
        human.set_pending_action(Action(action), amount)  # アクションセット
        result = self.round_manager.step_one_action()  # step_one_actionで decide_action 呼び出し
        if result == Status.WAITING_FOR_HUMAN:
            return self._make_waiting_response()
        return {"status": result, "state": self.table.to_dict()}

    def _make_waiting_response(self):
        human = next(p for p in self.table.seats if p and p.is_human)
        return {
            "status": Status.WAITING_FOR_HUMAN,
            "state": self.table.to_dict(),
            "legal_actions": Action.get_legal_actions(human, self.table),
        }

    def get_state(self):
        return self.table.to_dict()

    def get_action_log(self):
        return self.round_manager.action_log

# グローバルなゲーム状態（FastAPIエンドポイントで利用）
game_state = GameState()