# backend/models/player.py
from typing import List, Optional
from backend.models.enum import Position, Action, State

class Player:
    def __init__(self, player_id: int, name: str, stack: int, is_human: bool = False):
        self.player_id = player_id
        self.name = name
        self.stack = stack
        self.is_human = is_human

        self.position: Optional[Position] = None
        self.hole_cards: List[int] = []
        self.bet_total: int = 0
        self.state: State = State.ACTIVE
        self.last_action: Optional[Action] = None

    @property
    def is_active(self) -> bool:
        return self.state == State.ACTIVE and self.stack > 0

    def deal_hole_cards(self, cards: List[int]):
        self.hole_cards = cards

    def bet(self, amount: int):
        self.stack -= amount
        self.bet_total += amount

    def fold(self):
        self.state = State.FOLDED
        self.last_action = Action.FOLD

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.bet_total = 0
        self.folded = False
        self.last_action = None
