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


class Position(Enum):
    LJ = auto()   # Lowjack (UTG相当)
    HJ = auto()   # Hijack
    CO = auto()   # Cutoff
    BTN = auto()  # Button
    SB = auto()   # Small Blind
    BB = auto()   # Big Blind
