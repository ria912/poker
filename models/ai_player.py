from player import Player
from action import Action
import random

class AIPlayer(Player):
    def __init__(self, name, stack=10000):
        super().__init__(name, is_human=False, stack=stack)

    def decide_action(self, legal_info):
    legal_actions = legal_info["actions"]
    current_bet = legal_info["current_bet"]

    # 優先順位: CHECK > CALL > FOLD
    if Action.CHECK in legal_actions:
        self.last_action = Action.CHECK
        return Action.CHECK, 0

    elif Action.CALL in legal_actions:
        to_call = current_bet - self.current_bet
        amount = min(self.stack, to_call)
        self.last_action = Action.CALL
        return Action.CALL, amount

    else:
        self.last_action = Action.FOLD
        return Action.FOLD, 0