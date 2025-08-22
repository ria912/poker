# app/services/table_service.py
from typing import List, Optional
from app.models.table import Table, Seat
from app.models.player import Player
from app.models.enum import Round, PlayerState
from app.models.deck import Card, Deck
from app.models.enum import Position
from app.utils.order_utils import get_next_active_index


class TableService:
    """
    テーブル全体の管理を行うサービス
    """

    # -------------------------
    # 基本操作
    # -------------------------

    def assign_player(self, table: Table, player: Player, seat_index: int) -> None:
        """指定された座席にプレイヤーを座らせる"""
        seat = self._get_seat(table, seat_index)
        if seat.player_id is not None:
            raise ValueError(f"Seat {seat_index} はすでに埋まっています")
        seat.player_id = player.id

    def assign_position(self, table: Table, dealer_index: int) -> None:
        """プレイヤーにポジションを割り当てる"""
        dealer_seat = self._get_seat(table, dealer_index)
        dealer_seat.position = Position.BTN
        sb_index = get_next_active_index(table.seats, dealer_index)
        sb_seat = self._get_seat(table, sb_index)
        sb_seat.position = Position.SB
        bb_index = get_next_active_index(table.seats, sb_index)
        bb_seat = self._get_seat(table, bb_index)
        bb_seat.position = Position.BB

    def collect_blinds(self, table: Table, small_blind: int, big_blind: int) -> None:
        """ブラインドを徴収する"""
        small_blind_index = self.get_index_by_position(table, Position.SB)
        big_blind_index = self.get_index_by_position(table, Position.BB)

        sb_seat = table.seats[small_blind_index]
        bb_seat = table.seats[big_blind_index]

        if sb_seat.player_id:
            sb_seat.bet_total += sb_seat.pay(small_blind)
        if bb_seat.player_id:
            bb_seat.bet_total += bb_seat.pay(big_blind)

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
            if seat.index == seat_number:
                return seat
        raise ValueError(f"Seat {seat_number} は存在しません")

    def get_index_by_position(self, table: Table, position: Position) -> Optional[int]:
        """ポジションから座席インデックスを取得"""
        for seat in table.seats:
            if seat.player.position == position:
                return seat.index
        return None