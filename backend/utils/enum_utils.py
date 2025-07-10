# backend/utils/enum_utils.py

from backend.models.enum import Position, Round, Action

ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN, Position.BTN_SB]

ROUND_ORDER = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]

def next_round(current: Round) -> Round:
    i = ROUND_ORDER.index(current)
    return ROUND_ORDER[i + 1]

def betting_actions() -> list[Action]:
    return [Action.BET, Action.RAISE]

def passive_actions() -> list[Action]:
    return [Action.FOLD, Action.CALL, Action.CHECK]
