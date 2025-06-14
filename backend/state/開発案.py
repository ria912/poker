# state/game_state.py
from backend.models.table import Table
from backend.models.round import Round, RoundManager
from backend.models.action import Action, ActionManager
from backend.models.enum import Status
from fastapi import HTTPException

class GameState:
    """ゲームのユースケースレイヤ。APIレスポンスもここから整理して提供。"""

    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)
        self.table.assign_players_to_seats()  # 初期化時にプレイヤーを座席に割り当てる

    def start_new_hand(self):
        """ゲームのハンドを最初からスタートしてレスポンスも整理して返す。"""
        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager.reset_action_order()

        result = self.round_manager.step()
        if result == Status.WAITING_FOR_HUMAN:
            return self._make_waiting_response()
        elif result == Status.WAITING_FOR_AI:
            self.round_manager.step_apply_action()
            return self._make_waiting_response()
        else:
            return self.process_action(self.round_manager.current_player.decide_action(self.table))

    def process_action(self, current_player, action: str, amount: int = 0):
        """プレイヤが指定したアクションを実行してレスポンスも整理して返す。"""
        if not current_player:
            raise HTTPException(404, f"プレイヤ {current_player.name} を見つけられない")

        action, amount = self.round_manager.current_player.decide_action(self.table)
        if not action or not amount:
            raise HTTPException(400, f"不正なアクション: {action}")

        self.round_manager.step_apply_action(current_player, action, amount)
        return self._make_waiting_response()


    def _make_waiting_response(self):
        """APIレスポンスに必要な情報も整理して帰す。"""
        return {
            "status": self.round_manager.status.name,
            "current_player": (
                self.round_manager.action_order[self.round_manager.action_index].name
                if self.round_manager.action_index < len(self.round_manager.action_order)
                else None
            ),
            "board": self.table.board,
            "pot": self.table.pot,
            "active_players": [p.name for p in self.table.seats if p and p.is_active],
            "action_history": self.table.action_log,
        }
