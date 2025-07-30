# backend/models/enum.py
from enum import Enum, auto

class Action(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    RAISE = auto()


class Round(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()
    
    def next(self):
        members = list(Round)
        idx = members.index(self)
        if idx + 1 < len(members):
            return members[idx + 1]
        return Round.SHOWDOWN  # 最終ラウンドでは SHOWDOWN を維持


class Position(Enum):
    LJ = auto()   # Lowjack (UTG相当)
    HJ = auto()   # Hijack
    CO = auto()   # Cutoff
    BTN = auto()  # Button
    SB = auto()   # Small Blind
    BB = auto()   # Big Blind

class State(Enum):
    ACTIVE = auto()
    FOLDED = auto()
    ALL_IN = auto()
    OUT = auto()