# models/enum.py
from enum import Enum

class Position(str, Enum):
    SB = 'sb'
    BB = 'bb'
    LJ = 'lj'
    HJ = 'hj'
    CO = 'co'
    BTN = 'btn'
    BTN_SB = "btn_sb"

    ALL_POSITIONS = [BTN, SB, BB, CO, HJ, LJ]

    ASSIGN_ORDER = [SB, BB, LJ, HJ, CO, BTN, BTN_SB]

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
    DEF = "def"
    AI_ACTED = "ai_acted"
    WAITING_FOR_HUMAN = "waiting_for_human"
    WAITING_FOR_AI = "waiting_for_ai"
    ROUND_OVER = "round_over"
    HAND_OVER = "hand_over"
    ERROR = "error"