# models/utils.py

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

    active_players = [
        seat.player for seat in seats if seat.player.is_active]
    if not active_players:
        return None

    seat_count = len(seats)
    ordered = []

    # BTNの次からスタートして1周する
    for offset in range(1, seat_count + 1):
        i = (btn_index + offset) % seat_count
        player = seats[i].player
        if player in active_players:
            ordered.append(player)

    return ordered