# models/player.py
class Player:
    def __init__(self, name="Player", stack=10000):
        self.name = name
        self.stack = stack
        self.hand = []
        self.position = None
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.has_left = False
        self.is_human = None

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.position = None

    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "current_bet": self.current_bet,
            "hand": self.hand,
            "position": self.position,
            "has_folded": self.has_folded,
            "last_action": self.last_action,
            "has_left": self.has_left,
            "is_human": self.is_human
        }