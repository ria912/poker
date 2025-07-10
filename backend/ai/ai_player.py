# models/ai_player.py
from backend.models.player import Player
from backend.services.action import Action, ActionManager
import random

class AIPlayer(Player):
    def __init__(self, name):
        super().__init__(name=f"{name}AI", stack=10000)

    def decide_action(self, table):
        legal_info = ActionManager.get_legal_actions_info(self, table)
        legal_actions = legal_info["legal_actions"]
        amount_ranges = legal_info["amount_ranges"]

        if Action.FOLD in legal_actions and random.random() < 0.2:
            return Action.FOLD, 0

        if Action.CALL in legal_actions and random.random() < 0.9:
            return Action.CALL, 0

        if Action.BET in legal_actions and random.random() < 0.1:
            return Action.BET, 0
        if Action.RAISE in legal_actions and random.random() < 0.1:
            return Action.RAISE, 0

        if Action.CHECK in legal_actions:
            return Action.CHECK, 0

        return Action.FOLD, 0
    
    def act(self, table):
        """OrderManager などから呼び出される共通アクション実行インターフェース"""
        return self.decide_action(table)
    
    def to_dict(self, show_hand=False):
        return self.base_dict(show_hand=show_hand)