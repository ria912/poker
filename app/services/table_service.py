# app/services/table_service.py
from typing import List, Optional
from app.models.table import Table, Seat
from app.models.player import Player
from app.models.enum import Round, PlayerState
from app.models.deck import Card, Deck


class TableService:
    """
    テーブル全体の管理を行うサービス
    """

    # -------------------------
    # 基本操作
    # -------------------------

    def assign_player(self, table: Table, player: Player, seat_number: int) -> None:
        """指定された座席にプレイヤーを座らせる"""
        seat = self._get_seat(table, seat_number)
        if seat.player is not None:
            raise ValueError(f"Seat {seat_number} はすでに埋まっています")
        seat.player = player

    def collect_blinds(self, table: Table, small_blind: int, big_blind: int, dealer_index: int) -> None:
        """ブラインドを徴収する"""
        small_blind_index = (dealer_index + 1) % len(table.seats)
        big_blind_index = (dealer_index + 2) % len(table.seats)

        sb_seat = table.seats[small_blind_index]
        bb_seat = table.seats[big_blind_index]

        if sb_seat.player:
            sb_seat.bet_total += sb_seat.player.pay(small_blind)
        if bb_seat.player:
            bb_seat.bet_total += bb_seat.player.pay(big_blind)

    def deal_hole_cards(self, table: Table, num_cards: int = 2) -> None:
        """各プレイヤーにホールカードを配る"""
        table.deck.shuffle()
        for _ in range(num_cards):
            for seat in table.seats:
                if seat.player:
                    card = table.deck.draw()
                    seat.player.receive_card(card)

    def deal_community_cards(self, table: Table, num_cards: int) -> None:
        """フロップ・ターン・リバーの配布"""
        for _ in range(num_cards):
            card = table.deck.draw()
            table.board.append(card)

    # -------------------------
    # ベット / ポット管理
    # -------------------------

    def add_to_pot(self, table: Table, amount: int) -> None:
        """ポットにチップを追加"""
        table.pot += amount

    def reset_bets(self, table: Table) -> None:
        """全座席のベット額をクリア"""
        for seat in table.seats:
            seat.bet_total = 0

    def settle_bets_to_pot(self, table: Table) -> None:
        """全座席のベット額をポットに集約"""
        for seat in table.seats:
            table.pot += seat.bet_total
            seat.bet_total = 0

    # -------------------------
    # ユーティリティ
    # -------------------------

    def _get_seat(self, table: Table, seat_number: int) -> Seat:
        """座席を取得"""
        for seat in table.seats:
            if seat.number == seat_number:
                return seat
        raise ValueError(f"Seat {seat_number} は存在しません")