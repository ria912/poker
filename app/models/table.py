# app/models/table.py
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.enum import PlayerState, Position
from .deck import Card, Deck
from .player import Player


class Seat(BaseModel):
    """座席（プレイヤーを乗せて、ベット額を管理）"""

    index: int
    player: Optional[Player] = None
    bet_total: int = 0

    # --- 状態判定 ---
    def is_occupied(self) -> bool:
        return self.player is not None

    def is_active(self) -> bool:
        return self.player is not None and self.player.state == PlayerState.ACTIVE

    # --- プレイヤー操作 ---
    def sit(self, player: Player) -> None:
        if self.player:
            raise ValueError("すでにプレイヤーが座っています")
        self.player = player

    def leave(self) -> Player:
        if not self.player:
            raise ValueError("プレイヤーがいません")
        p, self.player = self.player, None
        self.bet_total = 0
        return p

    # --- ベット操作 ---
    def place_bet(self, amount: int) -> int:
        if not self.player:
            raise ValueError("プレイヤー不在")
        paid = self.player.pay(amount)  # Player がスタックを減らす
        self.bet_total += paid
        return paid

    def clear_bet(self) -> int:
        """ラウンド終了時にベットをポットへ移動"""
        total, self.bet_total = self.bet_total, 0
        return total


class Table(BaseModel):
    """テーブル全体を表すクラス"""

    seats: List[Seat] = Field(default_factory=lambda: [Seat(index=i) for i in range(6)])  # 最大6席
    pot: int = 0
    board: List[Card] = []
    deck: Deck = Deck()

    # --- 座席操作 ---
    def get_active_seats(self) -> List[Seat]:
        return [s for s in self.seats if s.is_active()]

    def get_occupied_seats(self) -> List[Seat]:
        return [s for s in self.seats if s.is_occupied()]

    def find_seat_by_player(self, player: Player) -> Optional[Seat]:
        return next((s for s in self.seats if s.player == player), None)

    def find_player_by_position(self, position: Position) -> Optional[Player]:
        return next((s.player for s in self.seats if s.player and s.player.position == position), None)

    # --- ポット管理 ---
    def collect_bets_to_pot(self) -> None:
        """全員のbet_totalをポットに集約"""
        for seat in self.get_occupied_seats():
            self.pot += seat.clear_bet()

    def reset_pot(self) -> None:
        self.pot = 0

    # --- ボード操作 ---
    def deal_to_board(self, num: int) -> List[Card]:
        """ボードにカードを配る"""
        cards = [self.deck.draw() for _ in range(num)]
        self.board.extend(cards)
        return cards

    def reset_board(self) -> None:
        self.board = []

    # --- デッキ操作 ---
    def reset_deck(self) -> None:
        self.deck = Deck()
        self.deck.shuffle()

    def deal_to_player(self, seat: Seat, num: int = 2) -> List[Card]:
        """プレイヤーにカードを配る"""
        if not seat.is_occupied():
            raise ValueError("空席にカードは配れません")
        cards = [self.deck.draw() for _ in range(num)]
        seat.player.hole_cards = cards
        return cards

    def is_round_complete(self) -> bool:
        """現在のラウンドが終了しているかどうかを判定"""
        return all(seat.player.state != PlayerState.ACTIVE for seat in self.seats if seat.is_occupied())
