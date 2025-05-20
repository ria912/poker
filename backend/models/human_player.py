# models/human_player.py
from models.player import Player
from models.action import Action

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True

    def decide_action(self, table):
        legal_actions = Action.get_legal_actions(self, table)

        # automodeのアクションを取得
        if table.street == 'preflop' and self.hand == []:
            return Action.CALL, 0
        elif Action.CHECK in legal_actions:
            return Action.CHECK, 0
        else:
            return Action.FOLD, 0
