from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from .table import Table

class RoundPhase(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class PlayerStatus(str, Enum):
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all_in"

class PlayerState(BaseModel):
    id: str
    name: str
    chips: int
    bet: int
    hand: Optional[List[str]] = None  # 例: ["Ah", "Ks"]
    status: PlayerStatus

class GameState(BaseModel):
    round_phase: RoundPhase
    dealer_position: int
    current_player_position: int
    pot: int
    community_cards: List[str]
    players: List[PlayerState]
    last_action: Optional[str] = None
