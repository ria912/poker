# app/models/table.py
from pydantic import BaseModel, Field
from typing import List, Optional
from .deck import Card, Deck
from .enum import Position, PlayerState, Round

class Seat(BaseModel):

    index: int
    player_id: Optional[str] = None
    stack: int = 0
    position: Optional[Position] = None
    hole_cards: List[Card] = Field(default_factory=list)
    bet_total: int = 0
    state: PlayerState = PlayerState.OUT  # OUT, ACTIVE, FOLDED
    acted: bool = False

    def is_empty(self) -> bool:
        """席が空いているかどうかを判定"""
        return self.player_id is None

    def is_active(self) -> bool:
        """席がアクティブかどうかを判定"""
        return self.player_id is not None and self.state == PlayerState.ACTIVE and self.acted is False

    def reset_for_new_hand(self) -> None:
        """ハンド開始時にSeat状態をリセット"""
        self.acted = False
        self.bet_total = 0
        self.hole_cards.clear()
        if self.stack <= 0:
            self.state = PlayerState.OUT
        else:
            self.state = PlayerState.ACTIVE

class Table(BaseModel):
    deck: Deck = Field(default_factory=Deck)
    seats: List[Seat] = Field(default_factory=list)
    current_round: Round = Round.PREFLOP
    pot: int = 0
    board: List[Card] = Field(default_factory=list)
    
    def get_seat(self, seat_index: int) -> Optional[Seat]:
        for seat in self.seats:
            if seat.index == seat_index:
                return seat
        return None

    def reset_for_new_hand(self) -> None:
        """ハンド開始時にテーブルとSeatを初期化"""
        self.pot = 0
        self.board.clear()
        self.current_round = Round.PREFLOP
        for seat in self.seats:
            if seat.player_id:
                seat.reset_for_new_hand()