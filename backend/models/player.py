# models/player.py
class Player:
    def __init__(self, name="Player", stack=10000):
        self.name = name
        self.stack = stack
        self.hand = []
        self.position = None
        self.seat_number = None
        self.current_bet = 0
        self.last_action = None
        self.has_acted = False # アクション済みである
        self.folded = False
        self.all_in = False
        self.is_human = False # AIで初期化

        self.sitting_out = False # 離席中かどうか

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.last_action = None
        self.has_acted = False
        self.folded = False
        self.all_in = False

    def reset_for_next_round(self):
        self.current_bet = 0
        self.last_action = None
        self.has_acted = False
    
    @property
    def is_active(self):
        return not self.folded and not self.all_in and not self.sitting_out

    def base_dict(self, show_hand=False):
        data = {
            "name": self.name,
            "stack": self.stack,
            "position": self.position,
            "seat_number": self.seat_number,
            "current_bet": self.current_bet,
            "last_action": self.last_action,
            "has_acted": self.has_acted,            
            "folded": self.folded,
            "all_in": self.all_in,
            "sitting_out": self.sitting_out,
        }
        
        if show_hand:
            data["hand"] = self.hand

        return data