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

class Round(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

    ROUND_ORDER = [PREFLOP, FLOP, TURN, RIVER, SHOWDOWN]

    @classmethod
    def next(cls, current_round):
        order = cls.ROUND_ORDER
        try:
            i = order.index(current_round)
            return order[i + 1] if i + 1 < len(order) else None
        except ValueError:
            return None

class Action(str, Enum):
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    BET = 'bet'
    RAISE = 'raise'

    @classmethod
    def betting_actions(cls):
        # ベット系アクションの集合。BETとRAISEは金額指定が必要
        return [cls.BET, cls.RAISE]

    @classmethod
    def passive_actions(cls):
        # パッシブなアクション（掛け金増やさない）
        return [cls.FOLD, cls.CALL, cls.CHECK]

    @classmethod
    def requires_amount(cls, action):
        # どのアクションがベット額（amount）を必要とするか
        return action in cls.betting_actions()

class Status(str, Enum):
    RUNNING = "running" # round.step()待ちフラグ（初期）
    WAITING_FOR_HUMAN = "waiting_for_human"
    WAITING_FOR_AI = "waiting_for_ai"
    HUMAN_ACTED = "human_acted"
    AI_ACTED = "ai_acted"
    ROUND_OVER = "round_over" # ラウンド終了フラグ（ショウダウン）
    HAND_OVER = "hand_over" # ショウダウン処理終了フラグ
    ERROR = "error"

    @classmethod
    def is_waiting(cls, status):
        # 人間・AIいずれかの待機状態か判定
        return status in [cls.WAITING_FOR_HUMAN, cls.WAITING_FOR_AI]

    @classmethod
    def is_terminal(cls, status):
        # ラウンド終了またはハンド終了、エラーなどの状態判定
        return status in [cls.ROUND_OVER, cls.HAND_OVER, cls.ERROR]

    @classmethod
    def is_active(cls, status):
        # まだアクションが期待されている状態
        return not cls.is_terminal(status)