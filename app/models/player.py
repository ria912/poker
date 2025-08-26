# app/models/player.py
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

from .deck import Card
from .enum import PlayerState, ActionType


@dataclass
class Player:
    player_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Anonymous"
    stack: int = 0
    hole_cards: List[Card] = field(default_factory=list)

    seat_index: Optional[int] = None
    bet_total: int = 0 # ハンド中の総ベット額

    def reset_for_new_hand(self) -> None:
        self.hole_cards = []
        self.bet_total = 0

    def pay(self, amount: int) -> int:
        if amount <= 0:
            return 0
        pay_amount = min(self.stack, amount)
        self.stack -= pay_amount
        if self.stack == 0:
            self.state = PlayerState.ALL_IN
        return pay_amount
