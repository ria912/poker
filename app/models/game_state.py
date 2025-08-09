from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from models.enum import Position, Action

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
    id: int
    name: str
    stack: int
    hand: Optional[List[str]] = None
    position: Position
    bet: int
    status: PlayerStatus
    last_action: Optional[Action] = None

class TableState(BaseModel):
    id: int
    small_blind: int
    big_blind: int
    pot: int
    current_bet: int
    community_cards: List[str]
    players: List[PlayerState]

class GameState(BaseModel):
    table: TableState
    dealer_position: int
    current_player_position: int
    pot: int
    community_cards: List[str]
    players: List[PlayerState]
    last_action: Optional[str] = None
