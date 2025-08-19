from pydantic import BaseModel, Field
from typing import List, Optional
from .player import Player
from .deck import Deck, Card

class Seat(BaseModel):
    """テーブルの座席を表現するクラス"""
    seat_index: int
    player: Optional[Player] = None

class Table(BaseModel):
    """ゲームテーブルの状態を管理するクラス"""
    seats: List[Seat] = Field(default_factory=lambda: [Seat(seat_index=i) for i in range(9)]) # 9人席をデフォルトに
    deck: Deck = Field(default_factory=Deck)
    pot: int = 0
    community_cards: List[Card] = Field(default_factory=list)
    dealer_button_position: int = 0
    
    def add_player(self, player: Player, seat_index: int) -> bool:
        """指定した座席にプレイヤーを追加する"""
        if 0 <= seat_index < len(self.seats) and self.seats[seat_index].player is None:
            self.seats[seat_index].player = player
            return True
        return False

    def clear_for_new_hand(self):
        """次のハンドのためにテーブルの状態をリセットする"""
        self.deck.shuffle()
        self.pot = 0
        self.community_cards = []
        # 各プレイヤーの状態もリセット
        for seat in self.seats:
            if seat.player:
                seat.player.clear_for_new_hand()