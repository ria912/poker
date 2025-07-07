# models/player.py
from abc import ABC, abstractmethod

class Player(ABC):  # ABCを継承して「抽象クラス」とする
    def __init__(self, name="Player", stack=10000):
        self.name = name
        self.stack = stack
        self.hand = []
        self.position: str = None
        self.bet_total = 0
        self.seat_number: int = None
        
        self.last_action: str = None
        self.folded = False
        self.all_in = False
        self.sitting_out = False

        self.is_human = False # AIで初期化

    def reset(self, hand_over=False):
        self.bet_total = 0
        self.last_action = None
        
        if hand_over:
            self.folded = False
            self.all_in = False
            self.hand = []
            if self.stack == 0:
                self.sitting_out = True

    @property
    def is_active(self):
        return not self.folded and not self.all_in and not self.sitting_out

    @abstractmethod
    def act(self, table):
        pass

    def base_dict(self, show_hand = False):
        data = {
            "name": self.name,
            "hand": self.hand if show_hand else [],
            "stack": self.stack,
            "position": self.position,
            "bet_total": self.bet_total,
            "last_action": self.last_action,

            "seat_number": self.seat_number,
        }
        return data