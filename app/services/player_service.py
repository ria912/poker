from typing import List
from app.models.table import Seat
from app.models.deck import Card
from app.models.enum import PlayerState


class PlayerService:
    """Seat(=プレイヤー状態)を操作するサービス"""

    def bet(self, seat: Seat, amount: int) -> None:
        """プレイヤーがベットする"""
        if seat.stack < amount:
            raise ValueError("スタックが不足しています。")
        seat.stack -= amount
        seat.bet_total += amount
        seat.acted = True
        seat.state = PlayerState.ACTIVE

    def call(self, seat: Seat, call_amount: int) -> int:
        """プレイヤーがコールする。実際に支払った額を返す"""
        to_pay = min(seat.stack, call_amount)
        seat.stack -= to_pay
        seat.bet_total += to_pay
        seat.acted = True
        if seat.stack == 0:
            seat.state = PlayerState.ALL_IN
        return to_pay

    def fold(self, seat: Seat) -> None:
        """プレイヤーがフォールドする"""
        seat.hole_cards = []
        seat.state = PlayerState.FOLDED
        seat.acted = True

    def check(self, seat: Seat) -> None:
        """プレイヤーがチェックする"""
        seat.acted = True
        seat.state = PlayerState.ACTIVE

    def deal_cards(self, seat: Seat, cards: List[Card]) -> None:
        """プレイヤーにカードを配る"""
        seat.hole_cards = cards

    def reset_for_new_hand(self, seat: Seat) -> None:
        """新しいハンド用にプレイヤーをリセット"""
        seat.hole_cards = []
        seat.bet_total = 0
        seat.state = PlayerState.WAITING
        seat.acted = False