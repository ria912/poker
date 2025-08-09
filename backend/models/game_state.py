from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


# ===== 列挙型（ゲームの状態を定義） =====

class Position(str, Enum):
    DEALER = "dealer"
    SMALL_BLIND = "small_blind"
    BIG_BLIND = "big_blind"


class Action(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"


class RoundPhase(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class PlayerStatus(str, Enum):
    ACTIVE = "active"   # まだ勝負中
    FOLDED = "folded"   # 降りた
    ALL_IN = "all_in"   # 全額ベット済み


# ===== プレイヤーの状態 =====

class PlayerState(BaseModel):
    id: int
    name: str
    stack: int                    # 残りチップ
    hand: Optional[List[str]] = None  # 例: ["Ah", "Ks"]
    position: Position
    current_bet: int = 0          # このラウンドでのベット額
    status: Optional[PlayerStatus] = None
    last_action: Optional[Action] = None


# ===== 席情報 =====

class Seat(BaseModel):
    index: int
    player: Optional[PlayerState] = None  # 空席対応


# ===== テーブルの状態 =====

class TableState(BaseModel):
    max_seats: int
    small_blind: int
    big_blind: int

    btn_index: int
    current_player_index: int

    current_bet: int
    min_raise: int

    round_phase: RoundPhase
    pot: int = 0
    community_cards: List[str] = []   # 例: ["2h", "7d", "Jc"]
    seats: List[Seat]


# ===== ゲーム全体の状態 =====

class GameState(BaseModel):
    table: TableState
    hand_number: int = 1              # 何ハンド目か
    is_game_over: bool = False        # ゲーム終了フラグ