# models/human_player.py
from backend.models.player import Player

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.pending_action = None
        self.pending_amount = None
        self.is_human = True

    def set_pending_action(self, action: str, amount: int,):
        self.pending_action = action
        self.pending_amount = amount

    def decide_action(self):
        if self.pending_action is not None:
            action = self.pending_action
            amount = self.pending_amount
            
            self.pending_action = None
            self.pending_amount = None
            return action, amount
        else:
            raise ValueError("No pending action set for HumanPlayer.")

    def to_dict(self, show_hand=True):
        return self.base_dict(show_hand=show_hand)