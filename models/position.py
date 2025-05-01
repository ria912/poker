# models/position.py

ASSIGNMENT_ORDER = ['BTN', 'SB', 'BB', 'LJ', 'HJ', 'CO']
FULL_POSITIONS = ['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']

def rotate_players(players):
    """プレイヤーを1つ後ろに回して、BTNを進める"""
    players.append(players.pop(0))

def assign_positions(players):
    """
    アクティブプレイヤーにポジションを割り当てる。
    - FULL_POSITIONS の順に必要数だけポジションを切り出す。
    - その中から ASSIGNMENT_ORDER の順で割り当てる。
    """
    active_players = [p for p in players if not p.has_left]

    # アクティブプレイヤー数だけポジション候補を取り出す
    available_positions = FULL_POSITIONS[:len(active_players)]

    # assignment_order の優先順でポジションを並べ替える
    ordered_positions = [pos for pos in ASSIGNMENT_ORDER if pos in available_positions]

    # 全プレイヤーのポジション初期化
    for p in players:
        p.position = None

    # アクティブプレイヤーに順番にポジションを割り当てる
    for player, pos in zip(active_players, ordered_positions):
        player.position = pos