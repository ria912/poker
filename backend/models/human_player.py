# models/human_player.py
from models.player import Player
from models.action import Action

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True
        # テスト用
    def decide_action(self, context):
        legal_actions = context["legal_actions"]

        if 'bet' in legal_actions:
            return Action.BET, 200
        elif 'raise' in legal_actions:
            return Action.RAISE, 200
        elif 'call' in legal_actions:
            return Action.CALL, 0
        elif 'check' in legal_actions:
            return Action.CHECK, 0
        else:
            return Action.FOLD, 0
