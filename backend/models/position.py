# models/position.py
from backend.models.enum import Position

class PositionManager:
    ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
    ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]
    
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
    def position_names(n: int) -> list[Position]:
        if n == 2:
            return [Position.BB, Position.BTN_SB]
        elif n > len(PositionManager.ALL_POSITIONS):
            raise ValueError(f"{n}人は未対応（最大{len(PositionManager.ALL_POSITIONS)}人まで）")
        return PositionManager.ALL_POSITIONS[:n]

    @classmethod
    def assign_positions(cls, table):
        active_indices = table.active_seat_indices
        n = len(active_indices)
        if n < 2:
            raise ValueError("assign_positions には2人以上のアクティブプレイヤーが必要")

        valid_positions = cls.position_names(n)
        ordered_positions = [p for p in cls.ASSIGN_ORDER if p in valid_positions]

        seat_count = len(table.seats)
        i = (table.btn_index + 1) % seat_count
        ordered_seats = []

        while len(ordered_seats) < n:
            if i in active_indices:
                ordered_seats.append(i)
            i = (i + 1) % seat_count
                
        # ポジションを割り当てる
        assigned = {}
        for seat_index, pos in zip(ordered_seats, ordered_positions):
            seat = table.seats[seat_index]
            if seat.player:
                seat.player.position = pos
                assigned[seat_index] = pos  # ← 戻り値用に保存

        return assigned  # ← return の位置を修正