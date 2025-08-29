# app/models/player.py
from typing import List, Optional
import uuid

from .deck import Card

class Player:
    def __init__(
        self,
        name: str = "Anonymous",
        stack: int = 0,
    ):
        self.player_id: str = str(uuid.uuid4())
        self.name: str = name
        self.stack: int = stack
        self.hole_cards: List[Card] = []

    def pay(self, amount: int) -> int:
        if amount <= 0:
            return 0
        pay_amount = min(self.stack, amount)
        self.stack -= pay_amount
        return pay_amount
    
    def set_hole_cards(self, cards: List[Card]):
        if len(cards) != 2:
            raise ValueError("Hole cards must be exactly 2")
        self.hole_cards = cards