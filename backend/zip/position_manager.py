# backend/models/position_manager.py
from backend.models.enum import Position
from backend.models.table import Table, Seat
from backend.utils.order_utils import get_circular_order

class PositionManager:
    def __init__(self, table: Table, button_index: int):
        self.table = table
        self.button_index = button_index

    def rotate_button(self):
        """次のハンド用にボタン位置を1つ進める"""
        num_seats = len(self.table.seats)
        while True:
            self.button_index = (self.button_index + 1) % num_seats
            seat = self.table.seats[self.button_index]
            if seat.is_occupied():
                break

    def assign_positions(self):
        """現在のボタン位置から順にポジションを割り当てる"""
        occupied_seats = [seat for seat in self.table.seats if seat.is_occupied()]
        player_count = len(occupied_seats)
        positions = list(Position)[-player_count:]  # 使用するポジション（例: 6人なら LJ〜BB）

        # ボタンを起点に座席を並び替え
        ordered_seats = get_circular_order(occupied_seats, start=self.button_index)

        # BTN → CO → HJ ... の順に座席へポジション割当（※使用順を逆から）
        for seat, pos in zip(ordered_seats, reversed(positions)):
            seat.player.position = pos
