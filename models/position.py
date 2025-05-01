
assignment_order = ['BTN', 'SB', 'BB', 'LJ', 'HJ', 'CO']

# プレイヤーを回転させる
def rotate_players(players):
    players.append(players.pop(0))

# プレイヤーの位置を割り当てる
def assign_positions(players):
    # 使うポジションの順番
    use_positions = ['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']
    active_players = [p for p in players if not p.has_left]

    available = use_positions[:len(active_players)]
    assigned = [p for p in assignment_order if p in available]

    for player in players:
        player.position = None

    for player, pos in zip(active_players, assigned):
        player.position = pos
