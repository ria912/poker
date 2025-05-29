# state/game_state.py

from models.table import Table
from models.round_manager import RoundManager, Round
from models.action import Action
from models.human_player import WaitingForHumanAction

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)

    def start_new_hand(self):
        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager.start_new_betting_round()
        return self.round_manager.step_ai_actions()

    def receive_human_action(self, action: str, amount: int):
        """人間のアクションを適用し、次のAIへ進める"""
        try:
            action_enum = Action(action)
        except ValueError:
            raise ValueError(f"無効なアクション: {action}")
        return self.round_manager.receive_human_action(action_enum, amount)

    def get_state(self):
        return self.table.to_dict()

    def get_action_log(self):
        return self.table.action_log

# グローバルなゲーム状態（FastAPIエンドポイントで利用）
game_state = GameState()