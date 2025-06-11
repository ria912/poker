# models/position.py
from backend.models.enum import Position

class PositionManager:
    
    @staticmethod
    def set_btn_index(table) -> int:
        seat_count = len(table.seats)

        # 初回: 最初の非NoneのプレイヤーをBTNに
        if table.btn_index is None:
            for i in range(seat_count):
                player = table.seats[i].player
                if player and not player.sitting_out:
                    table.btn_index = i
                    return i
            raise Exception("No active players to assign BTN")
        
        # 2回目以降: 次の有効なプレイヤーへBTNを回す
        for offset in range(1, seat_count + 1):
            i = (table.btn_index + offset) % seat_count
            player = table.seats[i].player  # ← player を定義追加
            if player and not player.sitting_out:
                table.btn_index = i
                return i
    
        raise Exception("No active players to assign BTN")

    @staticmethod
    def get_position_order(n: int) -> list[Position]:
        if n == 2:
            return [Position.BB, Position.BTN_SB]
        elif n > len(Position.ALL_POSITIONS):
            raise ValueError(f"{n}人は未対応（最大{len(Position.ALL_POSITIONS)}人まで）")
        
        position_list = Position.ALL_POSITIONS[:n]
        return [pos for pos in Position.ASSIGN_ORDER if pos in position_list]

    @classmethod
    def assign_positions(cls, table):
        n = len(table.active_seat_indices)
        if n < 2:
            raise ValueError("assign_positions には2人以上のアクティブプレイヤーが必要")

        # BTNの次からスタートして、BTNを最後にする並び順
        ordered_seats = sorted(
            table.active_seat_indices,
            key=lambda i: (i - table.btn_index) % len(table.seats)
        )

        # ポジション順を取得
        ordered_positions = cls.get_position_order(n)

        # 割り当て
        assigned = {}
        for seat_index, pos in zip(ordered_seats, ordered_positions):
            seat = table.seats[seat_index]
            if seat.player:
                seat.player.position = pos
                assigned[seat_index] = pos
            else:
                raise ValueError(f"Seat {seat_index} にプレイヤーがいません")

        return assigned
