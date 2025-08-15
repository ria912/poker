# app/services/table_service.py
from app.models.table import Table, Seat
from app.models.enum import Round, PlayerState
from .player_service import reset_player

def reset_table(table: Table):
    """新しいハンド開始用にリセット"""
    table.community_cards.clear()
    table.pot = 0
    table.current_bet = 0
    table.min_bet = table.big_blind
    table.current_round = Round.PREFLOP
    for seat in table.seats:
        if seat.is_occupied:
            reset_player(seat.player)

def move_dealer_button(table: Table):
    """ディーラーボタンを次のプレイヤーへ"""
    table.dealer_index = (table.dealer_index + 1) % table.seat_count

def add_to_pot(table: Table, amount: int):
    """ポットにチップ追加"""
    table.pot += amount

def advance_round(table: Table):
    """次のラウンドに進む"""
    table.current_round = table.current_round.next()

def update_current_bet(table: Table):
    """現在のベット額を更新"""
    table.current_bet = max(seat.player.bet_total for seat in table.seats if seat.is_occupied)

def update_min_bet(table: Table, amount: int):
    """最小ベット額を更新"""
    table.min_bet = amount
