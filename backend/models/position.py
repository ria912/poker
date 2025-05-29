# models/position.py
from models.enum import Position
from models import utils
# ポジション割り当ての順番（アクション順）
ACTION_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN]
# player数に応じて使用するポジションを決定するためのリスト
FULL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]

def set_btn_index(table):
    seats = table.seats
    seat_count = len(seats)
    active_players = utils.get_active_players(seats)

    if not active_players:
        return None  # アクティブプレイヤーがいない場合は None を返す

    start = (table.btn_index + 1) if table.btn_index is not None else 0
    
    for offset in range(seat_count): # offset は 0 から seat_count - 1 まで
        i = (start + offset) % seat_count # BTNの次から全席を確認する
        if seats[i] in active_players: # アクティブプレイヤーが見つかったら
            table.btn_index = i
            break # ループを抜ける
    return table.btn_index

def assign_positions(table):
    seats = table.seats
    btn_index = table.btn_index

    if btn_index is None:
        raise ValueError("table.btn_index is not set.")
    
    # 一旦全員の position を None にリセット
    for p in seats:
        if p:
            p.position = None

    # BTN の設定と確認
    btn_player = seats[btn_index]
    if not btn_player or btn_player.has_left:
        raise ValueError("BTN is not assigned to a valid player.")
    btn_player.position = 'BTN'


    # BTNの次から時計回りにアクティブプレイヤーを並べる
    ordered_players = utils.get_ordered_active_players(seats, table.btn_index)
    if not ordered_players:
        raise ValueError("No active players to assign positions.")
    
    # 使用するポジションの一覧を決定して並べ替える
    used_positions = FULL_POSITIONS[:len(ordered_players)]
    ordered_positions = [pos for pos in ACTION_ORDER if pos in used_positions]

    # BTNの次から時計回りにポジションを割り当てる
    for player, pos in zip(ordered_players, ordered_positions):
        player.position = pos