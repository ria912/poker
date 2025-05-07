# models/position.py
# ポジション割り当ての順番
ASSIGNMENT_ORDER = ['BTN', 'SB', 'BB', 'LJ', 'HJ', 'CO']
# player数に応じて使用するポジションを決定するためのリスト
FULL_POSITIONS = ['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']

def rotate_button(seats):
    num_seats = len(seats)

    current_btn_index = None
    for i, p in enumerate(seats):
        # playerが存在し、BTNポジションを持っている場合
        if p and p.position == 'BTN':
            current_btn_index = i
            break

    start = (current_btn_index + 1) if current_btn_index is not None else 0
    for offset in range(num_seats):
        i = (start + offset) % num_seats
        if seats[i] is not None:
            new_btn_index = i
            break
    else:
        raise ValueError("No active player found to assign BTN.")        

    for p in seats:
        if p:
            p.position = None

    seats[new_btn_index].position = 'BTN'


def assign_positions(seats):
    """
    BTN を起点に時計回りにポジションを割り当てる。
    空席（None）はスキップ。
    """
    # BTN位置を探す
    btn_index = None
    for i, p in enumerate(seats):
        if p and p.position == 'BTN':
            btn_index = i
            break
    if btn_index is None:
        raise ValueError("No BTN assigned in seats.")

    # アクティブプレイヤーをBTNから時計回りに取得
    active_players = []
    num_seats = len(seats)
    for offset in range(num_seats):
        idx = (btn_index + offset) % num_seats
        player = seats[idx]
        if player is not None:
            active_players.append(player)

    # 使用するポジションを決定
    available_positions = FULL_POSITIONS[:len(active_players)]
    ordered_positions = [pos for pos in ASSIGNMENT_ORDER if pos in available_positions]

    # ポジションの割り当て
    for p in seats:
        if p:
            p.position = None

    for player, pos in zip(active_players, ordered_positions):
        player.position = pos