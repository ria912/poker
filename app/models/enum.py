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
    LJ = "LJ"
    HJ = "HJ"
    CO = "CO"


class PlayerState(str, Enum):
    ACTED = "ACTED"     # アクション済み
    FOLDED = "FOLDED"
    ALL_IN = "ALL_IN"
    OUT = "OUT"
    SITTING_OUT = "SITTING_OUT"

class GameStatus(str, Enum):
    WAITING       = "WAITING"          # ゲーム開始前の待機状態
    GAME_CONTINUE = "GAME_CONTINUE"    # ゲーム進行中
    ROUND_CONTINUE = "ROUND_CONTINUE"   # 現在のラウンドの進行中（次のアクションを求める）
    ROUND_OVER     = "ROUND_OVER"       # ラウンド終了（次のストリートへ）
    SHOWDOWN       = "SHOWDOWN"         # 全員チェックなどでカード公開フェーズへ
    GAME_OVER      = "GAME_OVER"        # ゲーム終了（勝者決定、チップ配分）
