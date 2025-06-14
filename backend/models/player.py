# models/player.py
class Player:
    def __init__(self, name="Player", stack=10000):
        self.name = name
        self.stack = stack
        self.hand = []
        self.position = None
        self.seat_number = None
        self.bet_total = 0
        self.last_action = None
        self.has_acted = False # アクション済みである（チェック確認用）
        self.folded = False
        self.all_in = False
        self.is_human = False # AIで初期化

        self.sitting_out = False # 離席中かどうか

    def reset(self, hand_over=False):
        self.bet_total = 0
        self.last_action = None
        self.has_acted = False
        
        if hand_over:
            self.folded = False
            self.all_in = False
            self.hand = []

    @property
    def is_active(self):
        return not self.folded and not self.all_in and not self.sitting_out

    def base_dict(self, show_hand = False):
        data = {
            "name": self.name,
            "stack": self.stack,
            "position": self.position,
            "bet_total": self.bet_total,
            "last_action": self.last_action,

            "seat_number": self.seat_number,
        }
        
        if show_hand:
            data["hand"] = self.hand

        return data