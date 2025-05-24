# models/utils.py

# player関連
def get_seat_summary(seats):
    """
    各プレイヤーの seat_number, name, position をまとめて返す。
    空席（None）はスキップ。
    """
    return [
        {
            "seat_number": player.seat_number,
            "name": player.name,
            "position": player.position
        }
        for player in seats
        if player is not None
    ]

def get_active_players(seats):
    return [
        player for player in seats
        if player and not player.has_folded and not player.has_all_in and not player.has_left
    ]

# position関連
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
        btn_index = 0  # BTNが未設定の場合は0にする
        
    active_players = get_active_players(seats)
    if not active_players:
        return []

    seat_count = len(seats)
    ordered = []

    # BTNの次からスタートして1周する
    for offset in range(1, seat_count + 1):
        i = (btn_index + offset) % seat_count
        player = seats[i]
        if player in active_players:
            ordered.append(player)

    return ordered

def find_next_active_index(seats, start_index):
    """
    start_index の次の席から時計回りに探索して、
    最初に見つかったアクティブプレイヤーのインデックスを返す。

    - start_index: 探索を開始する位置（例: BTNのインデックス）
    - アクティブ: フォールド・オールイン・退席していないプレイヤー

    Returns:
        アクティブプレイヤーのインデックス（int） or None（いなければ）
    """
    active_players = get_active_players(seats)
    if not active_players:
        return None

    seat_count = len(seats)
    start = (start_index + 1) % seat_count if start_index is not None else 0

    for offset in range(seat_count):
        i = (start + offset) % seat_count
        if seats[i] in active_players:
            return i

    return None  # 念のため（通常ここには来ない）