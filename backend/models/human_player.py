# models/human_player.py
from models.player import Player
from models.action import Action

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True
        self.input_action = None

    def set_action(self, action_dict):
        self.input_action = (action_dict["action"], action_dict.get("amount", 0))

    def decide_action(self, table):
        if self.input_action is None:
            raise Exception("waiting_for_human_action")
        action, amount = self.input_action
        self.input_action = None
        return action, amount