# app/models/table.py
from pydantic import BaseModel
from typing import List, Optional

from .deck import Card, Deck
from .player import Player


class Seat(BaseModel):
    """座席（プレイヤーを乗せて、ベット額を管理）"""

    number: int
    player: Optional[Player] = None
    bet_total: int = 0

    def is_occupied(self) -> bool:
        return self.player is not None

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

    def place_bet(self, amount: int) -> int:
        if not self.player:
            raise ValueError("プレイヤー不在")
        paid = self.player.pay(amount)
        self.bet_total += paid
        return paid

    def clear_bet(self) -> int:
        """ラウンド終了時にベットをポットへ移動"""
        total, self.bet_total = self.bet_total, 0
        return total


class Table(BaseModel):
    """テーブル全体：座席、ポット、ボードを管理"""

    seats: List[Seat]
    pot: int = 0
    board: List[Card] = []
    deck: Deck = Deck()

    def collect_bets(self) -> None:
        """全席のベットを回収してポットに加算"""
        for seat in self.seats:
            self.pot += seat.clear_bet()

    def deal_to_player(self, seat: Seat, n: int) -> None:
        """座席のプレイヤーにカードを配る"""
        if not seat.player:
            raise ValueError("プレイヤー不在")
        cards = self.deck.draw(n)
        for c in cards:
            seat.player.receive_card(c)

    def deal_to_board(self, n: int) -> None:
        """コミュニティカードを配る"""
        cards = self.deck.draw(n)
        self.board.extend(cards)

    def reset_round(self) -> None:
        """ラウンド終了時にボードとベットをリセット"""
        self.collect_bets()
        self.board.clear()
        for seat in self.seats:
            if seat.player:
                seat.player.clear_hand()
    
    #役判定
    def evaluate_hands(self, board: Optional[List[Card]] = None) -> Dict[str, Dict]:
        """
        任意のボードで役判定
        """
        board = board if board is not None else self.board
        results = {}
        for seat in self.seats:
            if seat.player and seat.player.state not in ("FOLDED",):
                score, name = EvaluateUtils.evaluate_hand(seat.player.hand, board)
                results[seat.player.player_id] = {
                    "score": score,
                    "hand": seat.player.hand,
                    "hand_name": name,
                }
        return results

    def determine_winner(self, board: Optional[List[Card]] = None) -> Optional[str]:
        """
        任意のタイミングで勝者判定
        """
        board = board if board is not None else self.board
        active_hands = {
            seat.player.player_id: seat.player.hand
            for seat in self.seats
            if seat.player and seat.player.state not in ("FOLDED",)
        }
        if not active_hands:
            return None
        return EvaluateUtils.compare_hands(active_hands, board)