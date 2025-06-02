# models/enum.py
from enum import Enum

class Position(str, Enum):
    SB = 'sb'
    BB = 'bb'
    LJ = 'lj'
    HJ = 'hj'
    CO = 'co'
    BTN = 'btn'

class Action(str, Enum):
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'

class Round(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class Status(str, Enum):
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    ROUND_OVER = "round_over"
    HAND_OVER = "hand_over"
    ERROR = "error"