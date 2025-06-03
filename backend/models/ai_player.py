# models/ai_player.py
from backend.models.player import Player
from backend.models.action import Action
import random

class AIPlayer(Player):
    def __init__(self, name):
        super().__init__(name=f"{name}AI", stack=10000)

    def decide_action(self, table):
        legal_actions = Action.get_legal_actions(self, table)

        if Action.FOLD in legal_actions and random.random() < 0.2:
            return Action.FOLD, 0

        if Action.CALL in legal_actions:
            return Action.CALL, 0

        if Action.BET in legal_actions:
            return Action.BET, 0
        if Action.RAISE in legal_actions:
            return Action.RAISE, 0

        if Action.CHECK in legal_actions:
            return Action.CHECK, 0

        return Action.FOLD, 0
    
    def to_dict(self, show_hand=False):
        return self.base_dict(show_hand=show_hand)
    