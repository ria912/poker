# schemas/game_state_schema.py
from pydantic import BaseModel
from typing import List, Optional
from backend.models.enum import Round, Position


class PlayerState(BaseModel):
    name: str
    stack: int
    bet: int
    position: Optional[Position]
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
            seats=[
                SeatState(
                    index=i,
                    player=PlayerState(
                        name=seat.player.name,
                        stack=seat.player.stack,
                        bet=seat.player.bet,
                        position=seat.player.position,
                        is_active=seat.player.is_active
                    ) if seat.player else None
                )
                for i, seat in enumerate(table.seats)
            ]
        )