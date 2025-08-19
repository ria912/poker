from enum import Enum

class Suit(Enum):
    """カードのスート（マーク）"""
    SPADES = "s"
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"

class Rank(Enum):
    """カードのランク（数字）"""
    2 = 2
    3 = 3
    4 = 4
    5 = 5
    6 = 6
    7 = 7
    8 = 8
    9 = 9
    10 = 10
    J = 11
    Q = 12
    K = 13
    A = 14

class Position(Enum):
    """プレイヤーのテーブルでのポジション"""
    SB = "SB"  # Small Blind
    BB = "BB"  # Big Blind
    LJ = "LJ"  # Low Jack
    HJ = "HJ"  # High Jack
    CO = "CO"  # Cut Off
    BTN = "BTN" # Button

class Action(Enum):
    """プレイヤーが取れるアクション"""
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"

class Round(Enum):
    """ゲームのラウンド"""
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"
    SHOWDOWN = "SHOWDOWN"

class GameStatus(Enum):
    """ゲーム全体のステータス"""
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"