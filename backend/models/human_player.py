# models/human_player.py
from models.player import Player
from models.action import Action

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True
        self.input_action = None

    def set_action(self, action_tuple):
        """外部（API）から人間のアクションを与える"""
        self.input_action = action_tuple

    def decide_action(self, table):
        legal_actions = Action.get_legal_actions(self, table)

        # input_action がセットされていない場合、まだ入力待ち
        if self.input_action is None:
            raise Exception("waiting_for_human_action")

        action, amount = self.input_action
        # セーフティチェック：合法手かどうか
        if action not in legal_actions:
            raise ValueError(f"Invalid action: {action}. Legal actions: {legal_actions}")

        # 使い終わったら消す（1回限り）
        self.input_action = None
        return action, amount