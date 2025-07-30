# backend/models/position_manager.py
from backend.models.enum import Position
from backend.models.table import Table, Seat
from backend.utils.order_utils import get_circular_order

class PositionManager:
    POSITION_ORDER = [
        Position.LJ,
        Position.HJ,
        Position.CO,
        Position.BTN,
        Position.SB,
        Position.BB,
    ]

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
        occupied_seats = [seat for seat in self.table.seats if seat.is_occupied()]
        player_count = len(occupied_seats)

        if player_count == 2:
            positions = [Position.BTN, Position.BB]
        else:
            # 使用するポジションをスライスで取得
            positions = self.POSITION_ORDER[-player_count:]

            # BTN(-3)を起点に回転させる
            positions = positions[-3:] + positions[:-3]

        # BTN座席から回転
        btn_seat = self.table.seats[self.button_index]
        btn_index_in_occupied = occupied_seats.index(btn_seat)
        ordered_seats = get_circular_order(occupied_seats, start=btn_index_in_occupied)

        for seat, pos in zip(ordered_seats, positions):
            seat.player.position = pos