from typing import Optional
from .deck import Card
from .player import Player
from .enum import SeatStatus, Position

class Seat:
    def __init__(self, index: int, player: Optional[Player] = None):
        self.index: int = index
        self.player: Optional[Player] = player
        self.stack: int = 0
        self.hole_cards: list[Card] = []
        self.position: Optional[Position] = None
        self.current_bet: int = 0
        self.bet_total: int = 0
        self.status: SeatStatus = SeatStatus.OUT
        self.acted: bool = False
        
    @property
    def is_occupied(self) -> bool:
        """プレイヤーが座っているかどうか"""
        return self.player is not None
    
    @property
    def is_active(self) -> bool:
        """この座席がアクティブかどうか"""
        return self.is_occupied and self.status == SeatStatus.ACTIVE

    def reset(self) -> None:
        """座席の状態をリセットする"""
        self.current_bet = 0
        self.bet_total = 0
        self.hole_cards = []
        self.acted = False
        if self.is_occupied and self.stack > 0:
            self.status = SeatStatus.ACTIVE
        else:
            self.status = SeatStatus.OUT

    def sit_down(self, player: Player, stack: int) -> None:
        """プレイヤーを座席に座らせる"""
        if self.is_occupied:
            raise ValueError(f"Seat {self.index} is already occupied")
        self.player = player
        self.stack = stack
        self.status = SeatStatus.ACTIVE

    def stand_up(self) -> None:
        """プレイヤーを座席から外す"""
        self.player = None
        self.current_bet = 0
        self.stack = 0
        self.status = SeatStatus.OUT

    def bet(self, amount: int) -> None:
        """座席にいるプレイヤーがベットする"""
        if not self.is_occupied:
            raise ValueError(f"Seat {self.index} is empty")
        if self.stack < amount:
            raise ValueError("Not enough chips to bet")
        self.stack -= amount
        self.current_bet += amount
        self.bet_total += amount

    def receive_cards(self, cards: list[Card]) -> None:
        """座席にいるプレイヤーがカードを受け取る"""
        if not self.is_occupied:
            raise ValueError(f"Seat {self.index} is empty")
        if len(cards) != 2:
            raise ValueError("A player must receive exactly two hole cards")
        self.hole_cards = cards