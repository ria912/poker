# models/enum.py
from enum import Enum, auto

class Position(str, Enum):
    SB = auto()
    BB = auto()
    LJ = auto()
    HJ = auto()
    CO = auto()
    BTN = auto()
    BTN_SB = auto()

class Round(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

    ROUND_ORDER = [PREFLOP, FLOP, TURN, RIVER, SHOWDOWN]

    @staticmethod
    def next(current):
        sequence = list(Round)  # [Round.PREFLOP, Round.FLOP, ...]
        i = sequence.index(current)
        return sequence[i + 1]

class Action(str, Enum):
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'

    @classmethod
    def betting_actions(cls):
        return [cls.BET, cls.RAISE]

    @classmethod
    def passive_actions(cls):
        return [cls.FOLD, cls.CALL, cls.CHECK]

class Status(str, Enum):
    ROUND_CONTINUE = "round_continue" # round.step()待ちフラグ（初期）
    WAITING_FOR_HUMAN = "waiting_for_human"
    WAITING_FOR_AI = "waiting_for_ai"
    PLAYER_ACTED = "player_acted"
    ROUND_OVER = "round_over" # 各ラウンド終了フラグ
    WAITING_FOR_WINNER = "waiting_for_winner" # ショウダウン処理待ちフラグ
    HAND_OVER = "hand_over" # ショウダウン処理終了フラグ
    GAME_OVER = "game_over" # ゲーム終了フラグ
    ERROR = "error"

    @classmethod
    def is_waiting(cls, status):
        # 人間・AI・勝者判定・待機状態
        return status in [cls.WAITING_FOR_HUMAN, cls.WAITING_FOR_AI, cls.WAITING_FOR_WINNER]

    @classmethod
    def waiting_step(cls, status):
        # 処理完了フラグ（エラー以外）
        return status in [cls.HUMAN_ACTED, cls.AI_ACTED, cls.ROUND_CONTINUE, cls.ROUND_OVER]