# backend/services/dealer.py
from backend.models.deck import Deck
from backend.models.table import Table, Seat
from backend.models.enum import Position
from backend.utils.order_utils import get_circular_order

class Dealer:
    def __init__(self, table: Table):
        self.table = table
        self.deck = Deck()
        self.button_index = 0  # ボタン位置のインデックス

    def assign_positions(self):
        """現在の着席状況に応じてポジションを割り当てる"""
        occupied_seats = [seat for seat in self.table.seats if seat.is_occupied()]
        player_count = len(occupied_seats)
        positions = list(Position)[-player_count:]  # BTN〜LJ のうち必要数を使用
        ordered_seats = get_circular_order(occupied_seats, start=self.button_index)

        for seat, pos in zip(ordered_seats, reversed(positions)):
            seat.player.position = pos

    def deal_hole_cards(self):
        """全プレイヤーに2枚ずつ配る"""
        for seat in self.table.seats:
            if seat.is_occupied():
                cards = self.deck.draw(2)
                seat.player.deal_hole_cards(cards)

    def post_blinds(self):
        """SBとBBにブラインドを投稿させる"""
        for seat in self.table.seats:
            if not seat.is_occupied():
                continue
            pos = seat.player.position
            if pos == Position.SB:
                self.table.post_blind(seat, amount=10)
            elif pos == Position.BB:
                self.table.post_blind(seat, amount=20)

    def deal_community_cards(self, round_name):
        """フロップ、ターン、リバーのカードを配る"""
        if round_name == "FLOP":
            self.table.board.extend(self.deck.draw(3))
        elif round_name in {"TURN", "RIVER"}:
            self.table.board.extend(self.deck.draw(1))

    def distribute_pot(self):
        """簡易版：残っている中で1人だけならその人にポットを全額渡す"""
        active_seats = self.table.get_active_seats()
        if len(active_seats) == 1:
            winner = active_seats[0].player
            winner.stack += self.table.pot
            self.table.pot = 0
