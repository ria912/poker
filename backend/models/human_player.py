# models/human_player.py
from models.player import Player

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True
        self.input_action = None

    def set_action(self, action_dict):
        self.input_action = (action_dict["action"], action_dict.get("amount", 0))

    def decide_action(self, table):
        if self.input_action is None:
            raise WaitingForHumanAction()
        action, amount = self.input_action
        self.input_action = None
        return action, amount

    def to_dict(self, show_hand=True):
        return self.base_dict(show_hand=show_hand)

class WaitingForHumanAction(Exception):
    pass