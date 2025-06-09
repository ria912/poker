# models/position.py
from backend.models.enum import Position
# ポジション割り当ての順番（アクション順）
ACTION_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]
# player数に応じて使用するポジションを決定するためのリスト
FULL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]

def get_ordered_active_players(seats, btn_index):
    """
    btn_index の次から時計回りに、アクティブプレイヤーを順にリストで返す。

    Args:
        seats (list): プレイヤーの座席リスト
        btn_index (int): BTNの座席インデックス

    Returns:
        list: アクティブプレイヤー（Playerオブジェクト）の順序付きリスト
    """
    if btn_index is None:
        btn_index = 0

    active_players = [
        seat.player for seat in seats if seat.player and seat.player.is_active
    ]
    if not active_players:
        return None

    seat_count = len(seats)
    ordered = []
    for offset in range(1, seat_count + 1):
        i = (btn_index + offset) % seat_count
        seat = seats[i]
        if seat.player and seat.player in active_players:
            ordered.append(seat.player)

    return ordered


def set_btn_index(seats, btn_index):
    seat_count = len(seats)
    active_players = [seat for seat in seats if seat.player and seat.player.is_active]

    if not active_players:
        return None

    start = (btn_index + 1) if btn_index is not None else 0

    for offset in range(seat_count):
        i = (start + offset) % seat_count
        if seats[i] in active_players:
            return i  # 新しい btn_index を返す

    return None

def assign_positions(seats, btn_index):
    if btn_index is None:
        raise ValueError("btn_index is not set.")

    for seat in seats:
        if seat.player:
            seat.player.position = None

    btn_seat = seats[btn_index]
    if not btn_seat.player or btn_seat.player.has_left:
        raise ValueError("BTN is not assigned to a valid player.")

    btn_seat.player.position = 'BTN'

    ordered_players = get_ordered_active_players(seats, btn_index)
    if not ordered_players:
        raise ValueError("No active players to assign positions.")

    used_positions = FULL_POSITIONS[:len(ordered_players)]
    ordered_positions = [pos for pos in ACTION_ORDER if pos in used_positions]

    for player, pos in zip(ordered_players, ordered_positions):
        player.position = pos
