from models.player import Player

class AutoHumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True

    def decide_action(self, context):
        legal_actions = context["legal_actions"]

        if 'bet' in legal_actions:
            return 'bet', 200
        elif 'raise' in legal_actions:
            return 'raise', 200
        elif 'call' in legal_actions:
            return 'call', 0
        elif 'check' in legal_actions:
            return 'check', 0
        else:
            return 'fold', 0
