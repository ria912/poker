# app/services/table_service.py
from typing import Optional
from app.models.table import Table, Seat
from app.models.enum import Round, PlayerState

class TableService:
    """テーブル管理と進行ロジック"""

    @staticmethod
    def reset_table(table: Table):
        """新しいハンド開始用にリセット"""
        table.community_cards.clear()
        table.pot = 0
        table.current_round = Round.PREFLOP
        for seat in table.seats:
            if seat.is_occupied:
                seat.player.hand.clear()
                seat.player.bet_total = 0
                if seat.player.stack == 0:
                    seat.player.state = PlayerState.OUT
                else:
                    seat.player.state = PlayerState.ACTIVE

    @staticmethod
    def move_dealer_button(table: Table):
        """ディーラーボタンを次のプレイヤーへ"""
        table.dealer_index = (table.dealer_index + 1) % table.seat_count

    @staticmethod
    def add_to_pot(table: Table, amount: int):
        """ポットにチップ追加"""
        table.pot += amount

    @staticmethod
    def advance_round(table: Table):
        """次のラウンドに進む"""
        table.current_round = table.current_round.next()

    @staticmethod
    def update_current_bet(table: Table, amount: int):
        """現在のベット額を更新"""
        table.current_bet = max(seat.player.bet_total for seat in table.seats if seat.is_occupied)

    @staticmethod
    def update_min_bet(table: Table, amount: int):
        """最小ベット額を更新"""
        table.min_bet = amount
