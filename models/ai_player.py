from player import Player
from action import Action
import random

class AIPlayer(Player):
    def __init__(self, name, stack=10000):
        super().__init__(name, is_human=False, stack=stack)

    def decide_action(self, legal_actions):
        """
        legal_actionsからコールまたはチェックを選択（ランダム）
        """
        actions = legal_actions.get("actions", [])
        # コールまたはチェックが含まれているアクションリストを取得
        available_actions = [action for action in legal_actions if action in [Action.CALL, Action.CHECK]]

        if not available_actions:
            # コールまたはチェックが選べない場合の処理
            print(f"{self.name} has no available actions")
            return None, 0

        # ランダムにコールまたはチェックを選択
        action = random.choice(available_actions)
        amount = 0  # チェックの場合は金額は不要

        if action == Action.CALL:
            # コールする場合、適切な金額（コール額）を決定
            to_call = legal_actions.get('current_bet', 0) - self.current_bet
            amount = to_call  # コール額を設定

        self.last_action = action
        return action, amount