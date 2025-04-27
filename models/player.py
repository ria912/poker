class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.stack = 10000
        self.current_bet = 0
        self.hand = []
        self.position = None
        self.current_bet = 0
        self.has_folded = False

    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "current_bet": self.current_bet,
            "hand": self.hand if self.is_human else ["X", "X"],
            "position": self.position,
            "has_folded": self.has_folded
        }
