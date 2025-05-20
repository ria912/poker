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
        if self.input_action is None:
            raise Exception("waiting_for_human_action")
        action = self.input_action
        self.input_action = None
        return action