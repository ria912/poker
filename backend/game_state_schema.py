# schemas/game_state_schema.py
from pydantic import BaseModel
from typing import List, Optional
from backend.models.enum import Round, Position


class PlayerState(BaseModel):
    name: str
    hand: List[str]
    position: Optional[Position]
    stack: int
    bet: int
    is_active: bool


class SeatState(BaseModel):
    index: int
    player: Optional[PlayerState]


class GameStateSchema(BaseModel):
    round: Round
    pot: int
    board: List[str]
    seats: List[SeatState]

    @classmethod
    def from_table(cls, table) -> "GameStateSchema":
        return cls(
            round=table.round,
            pot=table.pot,
            board=table.board,
            seats=[seat.to_schema() for seat in table.seats]
        )