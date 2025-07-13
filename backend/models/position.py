from backend.models.enum import Position
from typing import List
from backend.utils.order_utils import get_circular_order

class PositionManager:
    ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
    ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]

    @staticmethod
    def set_btn_index(table) -> int:
        seat_count = len(table.seats)
        if table.btn_index is None:
            for i in range(seat_count):
                player = table.seats[i].player
                if player and not player.sitting_out:
                    table.btn_index = i
                    return i
            raise ValueError("アクティブなプレイヤーがいません")
        
        for offset in range(1, seat_count + 1):
            i = (table.btn_index + offset) % seat_count
            player = table.seats[i].player
            if player and not player.sitting_out:
                table.btn_index = i
                return i
        
        raise Exception("BTN を移動できるアクティブプレイヤーがいません")

    @classmethod
    def assign_positions(cls, table):
        active_indices = table.get_active_seat_indices()
        n = len(active_indices)
        if n < 2:
            raise ValueError("2人以上のアクティブプレイヤーが必要")

        valid_positions = cls.ASSIGN_ORDER[:n]
        ordered_seats = get_circular_order(
            table.seats,
            start_index=(table.btn_index + 1),
            condition=lambda seat: seat.index in active_indices
        )

        assigned = {}
        for seat, pos in zip(ordered_seats, valid_positions):
            if seat.player:
                seat.player.position = pos
                assigned[seat.index] = pos
            else:
                raise ValueError(f"Seat {seat.index} にプレイヤーがいません")

        return assigned