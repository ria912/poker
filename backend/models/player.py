# backend/models/player.py
from typing import List, Optional
from backend.models.enum import Position, Action

class Player:
    def __init__(self, name: str, stack: int, is_human: bool = False):
        self.name = name
        self.stack = stack
        self.position: Optional[Position] = None
        self.hole_cards: List[int] = []
        self.bet_total = 0
        self.folded = False
        self.is_all_in = False
        self.last_action: Optional[Action] = None
        self.is_human = is_human

    def deal_hole_cards(self, cards: List[int]):
        self.hole_cards = cards

    def bet(self, amount: int):
        self.stack -= amount
        self.bet_total += amount

    def fold(self):
        self.folded = True
        self.last_action = Action.FOLD

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.bet_total = 0
        self.folded = False
        self.last_action = None
