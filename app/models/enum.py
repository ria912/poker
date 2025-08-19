# backend/models/enum.py
from enum import Enum

class Action(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"


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
    CO = "CO"
    HJ = "HJ"
    LJ = "LJ"


class PlayerState(str, Enum):
    ACTIVE = "ACTIVE"
    ACTED = "ACTED"
    FOLDED = "FOLDED"
    ALL_IN = "ALL_IN"
    OUT = "OUT"


class GameStatus(str, Enum):
    WAITING       = "WAITING"          # ゲーム開始前の待機状態
    IN_PROGRESS   = "IN_PROGRESS"      # ゲーム進行中
    FINISHED      = "FINISHED"         # 全員チェックなどでカード公開フェーズへ
    GAME_OVER     = "GAME_OVER"        # ゲーム終了