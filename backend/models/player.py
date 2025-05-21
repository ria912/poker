# models/player.py
class Player:
    def __init__(self, name="Player", stack=10000):
        self.name = name
        self.stack = stack
        self.hand = []
        self.position = None
        self.current_bet = 0
        self.last_action = None
        self.has_acted = False # アクション済みである
        self.has_folded = False
        self.has_all_in = False
        self.has_left = False

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.last_action = None
        self.has_acted = False
        self.has_folded = False
        self.has_all_in = False


    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "hand": self.hand,
            "position": self.position,
            "current_bet": self.current_bet,
            "last_action": self.last_action,
            "has_acted": self.has_acted,            
            "has_folded": self.has_folded,
            "has_all_in": self.has_all_in,
            "has_left": self.has_left,
            "is_human": self.is_human
        }