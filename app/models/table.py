from pydantic import BaseModel, Field
from typing import List, Optional

from .player import Player
from .deck import Card
from .enum import Round, Position, PlayerState

class Seat(BaseModel):
    """テーブルの各座席の状態を管理するモデル"""
    seat_index: int
    player: Optional[Player] = None

    @property
    def is_occupied(self) -> bool:
        return self.player is not None

    @property
    def is_active(self) -> bool:
        return self.player is not None and self.player.state == PlayerState.ACTIVE

class Table(BaseModel):
    """ゲームテーブル全体の状態を管理するモデル"""
    seats: List[Seat] = Field(default_factory=[Seat(seat_index=i) for i in range(6)])
    seat_count: int = 6
    community_cards: List[Card] = Field(default_factory=list)
    pot: int = 0
    current_round: Round = Round.PREFLOP
    dealer_position: int = 0 # ディーラーボタンのseat_index

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