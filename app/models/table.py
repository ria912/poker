from pydantic import BaseModel, Field
from typing import List, Optional

from .player import Player
from .deck import Card
from .enum import Round, Position, PlayerState

class Seat(BaseModel):
    """テーブルの各座席の状態を管理するモデル"""
    seat_index: int
    player: Optional[Player] = None
    bet_total: int = 0

    @property
    def is_occupied(self) -> bool:
        return self.player is not None

    @property
    def is_active(self) -> bool:
        return self.player is not None and self.player.state == PlayerState.ACTIVE

class Table(BaseModel):
    """ゲームテーブル全体の状態を管理するモデル"""
    big_blind: int = 100
    small_blind: int = 50
    seat_count: int = 6

    seats: List[Seat] = Field(default_factory=list)
    current_round: Round = Round.PREFLOP
    community_cards: List[Card] = Field(default_factory=list)
    pot: int = 0

    current_bet: int = 0  # 現在の最大ベット額
    min_bet: int = big_blind  # 最小ベット額
    dealer_index: int = 0  # ディーラーボタンのseat_index

    def __init__(self, **data):
        super().__init__(**data)
        if not self.seats:
            self.seats = [Seat(seat_index=i) for i in range(self.seat_count)]

    def get_active_seats(self) -> List[Seat]:
        """アクティブな座席を取得する"""
        return [seat for seat in self.seats if seat.is_active]

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """プレイヤーIDからプレイヤーオブジェクトを取得する"""
        for seat in self.seats:
            if seat.is_occupied and seat.player.player_id == player_id:
                return seat.player
        return None

    def get_player_by_position(self, position: Position) -> Optional[Player]:
        """ポジションからプレイヤーオブジェクトを取得する"""
        for seat in self.seats:
            if seat.is_occupied and seat.player.position == position:
                return seat.player
        return None

    def get_player_by_index(self, index: int) -> Optional[Player]:
        """インデックスからプレイヤーオブジェクトを取得する"""
        if 0 <= index < self.seat_count:
            seat = self.seats[index]
            if seat.is_occupied:
                return seat.player
        return None