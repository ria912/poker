# backend/models/player.py
from typing import List, Optional
from models.enum import Position, Action, State

class Player:
    def __init__(self, player_id: int, name: str, stack: int=10000, is_human: bool = False):
        self.player_id = player_id
        self.name = name
        self.stack = stack
        self.is_human = is_human

        self.position: Optional[Position] = None
        self.hole_cards: List[int] = []
        self.bet_total: int = 0
        self.state: Optional[State] = None
        self.last_action: Optional[Action] = None

    @property
    def is_active(self) -> bool:
        return self.stack > 0 and self.state not in {State.FOLDED, State.ALL_IN, State.SITTING_OUT}

    def act(self, action: Action, amount: int = 0):
        if action == Action.FOLD:
            self.last_action = Action.FOLD
            self.state = State.FOLDED

        elif action == Action.CHECK:
            self.last_action = Action.CHECK
            self.state = State.ACTED
            
        elif action == Action.CALL:
            self.last_action = Action.CALL
            self.stack -= amount
            self.bet_total += amount
            if self.stack == 0:
                self.state = State.ALL_IN
            else:
                self.state = State.ACTED

        elif action == Action.BET or action == Action.RAISE:
            self.last_action = action
            self.stack -= amount
            self.bet_total += amount
            if self.stack == 0:
                self.state = State.ALL_IN
            else:
                self.state = State.ACTED
        
        elif action == Action.ALL_IN:
            self.last_action = Action.ALL_IN
            self.stack = 0
            self.bet_total += self.stack
            self.state = State.ALL_IN
        else:
            raise ValueError(f"Unknown action or amount: {action}, {amount}")

    def reset_round(self):
        if self.state == State.ACTED:
            self.state = None
        self.bet_total = 0
        self.last_action = None

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.bet_total = 0
        self.folded = False
        self.last_action = None
