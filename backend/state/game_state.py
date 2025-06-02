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
        result = self.round_manager.step_ai_actions()

        if result == Status.WAITING_FOR_HUMAN:
            return self._make_waiting_response()
        return {"status": result, "state": self.table.to_dict()}

    def receive_human_action(self, action: str, amount: int):
        """人間のアクションを適用し、次のAIへ進める"""
        try:
            action_enum = Action(action)
        except HTTPException:
            raise HTTPException(status_code=400, detail="無効なアクション")
        result = self.round_manager.receive_human_action(action_enum, amount)

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