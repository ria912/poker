# state/game_state.py
from backend.models.table import Table
from backend.models.round import RoundManager
from backend.models.action import Action, ActionManager
from backend.models.enum import Status
from fastapi import HTTPException

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)
        self.table.assign_players_to_seats()  # 初期化時にプレイヤーを座席に割り当てる

    def start_new_hand(self):
        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager.reset_action_order()

        result = self.round_manager.step()
        if result == Status.WAITING_FOR_HUMAN:
            return self._make_waiting_response()
        
        elif result == Status.WAITING_FOR_AI:
            self.round_manager.step_apply_action()
            return self._build_response(self.round_manager.status)

    def receive_human_action(self, action: str, amount: int):
        player = self.round_manager.current_player
        if player is None or not player.is_human:
            raise HTTPException(400, "現在のプレイヤーは人間ではありません")
        player.set_pending_action(Action(action), amount)
        self.round_manager.step_apply_action()  # player.decide_action 呼び出し
        return self._build_response(self.round_manager.status)

    def _make_waiting_response(self):
        if self.round_manager.current_player.is_human:
            return self._build_response(Status.WAITING_FOR_HUMAN)
        else:
            raise HTTPException(500, f"Unexpected human: {self.round_manager.current_player}")

    def _build_response(self, status: Status):
        current_player = self.round_manager.current_player
        if current_player is None:
            raise HTTPException(500, "現在のプレイヤーが不明です")
            
        response = {
            "status": status.value,
            "state": self.table.to_dict(),
            "current_player": current_player.name,
            "legal_actions": [action.value for action in ActionManager.get_legal_actions(current_player, self.table)],
        }
        return response
        
    def get_state(self):
        return self._build_response()
# グローバルなゲーム状態（FastAPIエンドポイントで利用）
game_state = GameState()