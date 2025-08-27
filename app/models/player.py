# app/models/player.py
from typing import List, Optional
import uuid

from .deck import Card

class Player:
    def __init__(
        self,
        name: str = "Anonymous",
        stack: int = 0,
        hole_cards: Optional[List[Card]] = None,
        seat_index: Optional[int] = None,
    ):
        self.player_id: str = str(uuid.uuid4())
        self.name: str = name
        self.stack: int = stack
        self.hole_cards: List[Card] = hole_cards if hole_cards is not None else []
        self.seat_index: Optional[int] = seat_index
        self.bet_total: int = 0  # ハンド中の総ベット額

    def reset_for_new_hand(self) -> None:
        self.hole_cards = []
        self.bet_total = 0

    def pay(self, amount: int) -> int:
        if amount <= 0:
            return 0
        pay_amount = min(self.stack, amount)
        self.stack -= pay_amount
        self.bet_total += pay_amount
        return pay_amount