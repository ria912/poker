# models/position.py
from backend.models.enum import Position

class PositionManager:
    ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
    # ポジションを割り当てる順番（BTN_SBが最後でヘッズアップに対応）Round 制御に注意！！
    ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN, Position.BTN_SB]
    # 上記リスト、enum にあるが念のため再記入

    @staticmethod
    def set_btn_index(table) -> int:
        """
        button_index を決定して table にセットする。
        ない場合は最初の着席者をBTNに、以降は次の着席者へ移動。
        """
        seat_count = len(table.seats)

        # 初回: 最初の非NoneのプレイヤーをBTNに
        if table.btn_index is None:
            for i in range(seat_count):
                if table.seats[i] is not None and not table.seats[i].sitting_out:
                    table.btn_index = i
                    return i
            raise Exception("No active players to assign BTN")
        
        # 2回目以降: 次の有効なプレイヤーへBTNを回す
        for offset in range(1, seat_count + 1):
            i = (table.btn_index + offset) % seat_count
            if table.seats[i] is not None and not table.seats[i].sitting_out:
                table.btn_index = i
                return i
    
        raise Exception("No active players to assign BTN")

    @staticmethod
    def position_names(n: int) -> list[Position]:
        # 使用するポジションのリストを作成する
        if n == 2:
            return [Position.BB, Position.BTN_SB]
        elif n > len(PositionManager.ALL_POSITIONS):
            raise ValueError(f"{n}人は未対応（最大{len(PositionManager.ALL_POSITIONS)}人まで）")
        return PositionManager.ALL_POSITIONS[:n]

    @classmethod
    def assign_positions(cls, table):
        """
        BTNを起点に、ASSIGN_ORDER順でアクティブプレイヤーにポジションを割り振る。
        """
        active_indices = table.active_seat_indices
        n = len(active_indices)
        if n < 2:
            raise ValueError("assign_positions には2人の以上のアクティブプレイヤーが必要")

        # 有効なポジション名と、ASSIGN_ORDERに従った並び
        valid_positions = cls.position_names(n)
        ordered_positions = [p for p in cls.ASSIGN_ORDER if p in valid_positions]

        # btn_index の次から順番にアクティブプレイヤーを回す
        seat_count = len(table.seats)
        i = (table.btn_index + 1) % seat_count
        ordered_seats = []

        while len(ordered_seats) < n:
            if i in active_indices:
                ordered_seats.append(i)
            i = (i + 1) % seat_count
                
        # ポジションを割り当てる
        for seat_index, pos in zip(ordered_seats, ordered_positions):
            player = table.seats[seat_index]
            player.position = pos