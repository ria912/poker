# backend/models/enum.py
from enum import Enum


class Action(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"


class Round(str, Enum):
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"
    SHOWDOWN = "SHOWDOWN"

    def next(self) -> "Round":
        members = list(Round)
        idx = members.index(self)
        if idx + 1 < len(members):
            return members[idx + 1]
        return Round.SHOWDOWN  # 最終ラウンド


class Position(str, Enum): 
    BTN = "BTN"
    SB = "SB"
    BB = "BB"
    LJ = "LJ"
    HJ = "HJ"
    CO = "CO"


class State(str, Enum):
    ACTIVE = "ACTIVE"
    FOLDED = "FOLDED"
    ALL_IN = "ALL_IN"
    OUT = "OUT"
    SITTING_OUT = "SITTING_OUT"

class Status(str, Enum):
    ROUND_CONTINUE = "ROUND_CONTINUE"
    ROUND_OVER = "ROUND_OVER"
    GAME_OVER = "GAME_OVER"
    GAME_CONTINUE = "GAME_CONTINUE"
    INVALID_ACTION = "INVALID_ACTION"
    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    GAME_STARTED = "GAME_STARTED"
    GAME_NOT_STARTED = "GAME_NOT_STARTED"