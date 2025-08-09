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

class Seat(BaseModel):
    index: int
    player: Optional[PlayerState]

class TableState(BaseModel):
    small_blind: int
    big_blind: int

    btn_index: int
    current_player_index: int
    
    current_bet: int
    min_bet: int
    
    round_phase: RoundPhase
    pot: int
    community_cards: List[str]
    seats: List[Seat]
    
class GameState(BaseModel):
    table: TableState
    
    
    