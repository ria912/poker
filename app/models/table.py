# app/models/table.py
from pydantic import BaseModel, Field
from typing import List, Optional
from .deck import Card, Deck
from .player import Player
from .enum import Position, PlayerState

class Seat(BaseModel):
    index: int
    player: Optional[Player] = None
    position: Position | None = None
    bet_total: int = 0
    state: PlayerState = PlayerState.ACTIVE
    acted: bool = False

    def is_empty(self) -> bool:
        """席にプレイヤーが座っているか"""
        return self.player is None

    def is_active(self) -> bool:
        """席がアクティブかどうかを判定"""
        return self.player is not None and self.state == PlayerState.ACTIVE

class Table(BaseModel):
    seats: List[Seat] = Field(default_factory=list)
    pot: int = 0
    board: List[Card] = Field(default_factory=list)
    deck: Deck = Field(default_factory=Deck)
    
    def active_seat_indices(self)
        return [seat.index for seat in self.seats if seat.is_active()]

    def reset_acted_states(self) -> None:
        """アクティブなプレイヤーのアクション状態をリセット"""
        for seat in self.seats:
            if seat.is_active():
                seat.acted = False

    def reset_for_new_hand(self) -> None:
        """次のハンド用に状態をリセット"""
        self.pot = 0
        self.board.clear()
        self.deck = Deck()  # 新しいデッキを生成
        for seat in self.seats:
            seat.bet_total = 0
            seat.acted = False
            if seat.player:
                seat.player.clear_hand()
                if seat.player.stack <= 0:
                    seat.state = PlayerState.OUT
                else:
                    seat.state = PlayerState.ACTIVE

    def collect_bets_to_pot(self) -> None:
        """全てのベットをポットに集める"""
        for seat in self.seats:
            self.pot += seat.bet_total
            seat.bet_total = 0