# backend/models/position.py
from backend.models.enum import Position
from backend.utils.order_utils import get_circular_order
from typing import List


class PositionManager:
    ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
    ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]

    @staticmethod
    def set_btn_index(table) -> int:
        seats = table.seats
        n = len(seats)

        if table.btn_index is None:
            for i in range(n):
                player = seats[i].player
                if player and not player.sitting_out:
                    table.btn_index = i
                    return i
            raise ValueError("アクティブなプレイヤーがいません")
        
        for offset in range(1, n + 1):
            i = (table.btn_index + offset) % n
            player = seats[i].player
            if player and not player.sitting_out:
                table.btn_index = i
                return i

        raise Exception("No active players to assign BTN")

    @staticmethod
    def get_position_order(n: int) -> List[Position]:
        if n == 2:
            return [Position.BB, Position.BTN_SB]
        if n > len(PositionManager.ALL_POSITIONS):
            raise ValueError(f"{n}人は未対応（最大{len(PositionManager.ALL_POSITIONS)}人まで）")
        use_positions = PositionManager.ALL_POSITIONS[:n]
        return [p for p in PositionManager.ASSIGN_ORDER if p in use_positions]

    @classmethod
    def assign_positions(cls, table):
        active_indices = table.get_active_seat_indices()
        n = len(active_indices)
        if n < 2:
            raise ValueError("2人以上のアクティブプレイヤーが必要")

        valid_positions = cls.get_position_order(n)
        seat_count = len(table.seats)
        start_index = (table.btn_index + 1) % seat_count

        ordered_seats = get_circular_order(
            items=list(range(seat_count)),
            start_index=start_index,
            condition=lambda i: i in active_indices
        )

        assigned = {}
        for seat_index, pos in zip(ordered_seats, valid_positions):
            seat = table.seats[seat_index]
            if seat.player:
                seat.player.position = pos
                assigned[seat_index] = pos
            else:
                raise ValueError(f"Seat {seat_index} にプレイヤーがいません")

        return assigned