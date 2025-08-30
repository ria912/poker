from typing import List, Optional
from .deck import Deck, Card
from .seat import Seat
from .player import Player

class Table:
    def __init__(self, seat_count: int = 6):
        self.deck = Deck()
        self.seats: List[Seat] = [Seat(index=i) for i in range(seat_count)]
        self.community_cards: List[Card] = []
        self.pot: int = 0

    def reset(self):
        """テーブルの状態をリセットする"""
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        for seat in self.seats:
            seat.reset()

    def sit_player(self, player: Player, seat_index: int, stack: int) -> None:
        """指定した座席にプレイヤーを座らせる"""
        if not (0 <= seat_index < len(self.seats)):
            raise IndexError("Invalid seat index")
        
        # seat.sit_down を呼び出すように変更
        self.seats[seat_index].sit_down(player, stack)

    def stand_player(self, seat_index: int) -> None:
        """指定した座席からプレイヤーを立たせる"""
        if seat_index < 0 or seat_index >= len(self.seats):
            raise IndexError("Invalid seat index")
        self.seats[seat_index].stand_up()

    def collect_bets(self) -> None:
        """全座席のベット額をポットに集めてリセット"""
        for seat in self.seats:
            self.pot += seat.current_bet
            seat.current_bet = 0

    def active_players(self) -> List[Player]:
        """アクティブなプレイヤー一覧を返す"""
        return [
            seat.player for seat in self.seats
            if seat.is_active
        ]

    def empty_seats(self) -> List[int]:
        """空席のインデックス一覧を返す"""
        return [
            seat.index for seat in self.seats if not seat.is_occupied
        ]