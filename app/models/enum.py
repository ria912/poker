from __future__ import annotations
from enum import Enum


class Position(str, Enum):
    """ポジション（最大6-max想定）。
    人数に応じた割当は services/position_manager 等で行う。
    """
    BTN = "BTN"
    SB = "SB"
    BB = "BB"
    UTG = "UTG"
    HJ = "HJ"  # 5-6人時の中間
    CO = "CO"


class Street(str, Enum):
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"
    SHOWDOWN = "SHOWDOWN"


class SeatState(str, Enum):
    ACTIVE = "ACTIVE"      # アクション可能
    FOLDED = "FOLDED"      # フォールド
    ALL_IN = "ALL_IN"      # オールイン（以後アクション不可）
    OUT = "OUT"            # テーブル不在（スタック0等）


class TableState(str, Enum):
    WAITING = "WAITING"        # 着席待ち/ハンド未開始
    IN_HAND = "IN_HAND"        # 進行中
    HAND_COMPLETE = "HAND_COMPLETE"  # ハンド終了（配当後）


class ActionType(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"
    POST_SB = "POST_SB"
    POST_BB = "POST_BB"
    DEAL = "DEAL"  # デバッグ/履歴用（カード配布）
