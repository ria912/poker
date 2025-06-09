# models/position.py
from backend.models.enum import Position

assign_order = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]

def set_btn_index(table):
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

def get_position_list(n):
    """
    プレイヤー人数に応じたポジション配列を返す。
    3人以上は BTN から定義済みの順に。
    """
    if n == 2:
        return [Position.BTN_SB, Position.BB]

    all_positions = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
    if n > len(all_positions):
        raise ValueError(f"対応していないプレイヤー数です（{n}人）。最大{len(all_positions)}人まで対応しています。")

    return all_positions[:n]

def assign_positions(table):
    """
    active_seat_indices にポジションを割り当てる（assign_order に基づく）。
    BTN の次の座席から順番に割り当てる。
    """
    active_indices = table.active_seat_indices
    n = len(active_indices)

    if n < 2:
        raise ValueError("アクティブプレイヤーが2人以上必要です。")

    # プレイヤー数に応じたポジション名を取得（例: 4人 → [BTN, SB, BB, CO]）
    base_positions = get_position_list(n)

    # assign_order に基づいて base_positions を並べ替える
    ordered_positions = [p for p in assign_order if p in base_positions]

    # btn_index の次から並べ替えた active_seat_indices を作成
    seat_count = len(table.seats)
    i = (table.btn_index + 1) % seat_count
    ordered_seats = []

    while len(ordered_seats) < n:
        if i in active_indices:
            ordered_seats.append(i)
        i = (i + 1) % seat_count

    # 割り当て実行
    for seat_index, position in zip(ordered_seats, ordered_positions):
        player = table.seats[seat_index]
        player.position = position