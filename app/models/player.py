# app/models/player.py
from typing import List, Optional
import uuid

from .deck import Card

class Player:
    def __init__(
        self,
        name: str = "Anonymous",
        stack: int = 0,
        seat_index: Optional[int] = None,
    ):
        self.player_id: str = str(uuid.uuid4())
        self.name: str = name
        self.stack: int = stack
        self.hole_cards: List[Card] = []
        self.seat_index: Optional[int] = seat_index

    def pay(self, amount: int) -> int:
        if amount >= self.stack:
            return self.stack
        pay_amount = min(self.stack, amount)
        self.stack -= pay_amount
        self.bet_total += pay_amount
        return pay_amount