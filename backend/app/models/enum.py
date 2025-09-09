# server/app/models/enums.py
from enum import Enum

class Position(str, Enum):
    BTN = "BTN"
    SB = "SB"
    BB = "BB"
    LJ = "LJ"
    HJ = "HJ"
    CO = "CO"
    
class ActionType(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"
    POST_SB = "POST_SB"
    POST_BB = "POST_BB"
    DEAL = "DEAL"

class Round(str, Enum):
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"
    SHOWDOWN = "SHOWDOWN"

class SeatStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FOLDED = "FOLDED"
    ALL_IN = "ALL_IN"
    OUT = "OUT"

class GameStatus(str, Enum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    HAND_COMPLETE = "HAND_COMPLETE"


