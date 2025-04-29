
def rotate_players(players):
    """
    プレイヤーの並びを時計回りに1つずらす（離席者も含む）
    """
    players.append(players.pop(0))


def assign_positions(players):
    """
    離席していないプレイヤーにポジションを割り当てる
    """
    full_positions = ['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']
    assignment_order = ['SB', 'BB', 'LJ', 'HJ', 'CO', 'BTN']

    active_players = [p for p in players if not p.has_left]

    available = full_positions[:len(active_players)]
    assigned = [p for p in assignment_order if p in available]

    for player in players:
        player.position = None

    for player, pos in zip(active_players, assigned):
        player.position = pos
