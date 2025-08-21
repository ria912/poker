from models.game_state import GameState
from models.enum import Position, PlayerState

def _find_next_active_player_index(game_state: GameState, start_index: int) -> int:
    """
    指定されたインデックスから時計回りに、次に行動可能なプレイヤーを探します。
    「行動可能」とは、フォールドしておらず、スタックが0でないプレイヤーを指します。

    Args:
        game_state: 現在のゲーム状態
        start_index: 検索を開始するプレイヤーの座席インデックス

    Returns:
        次に行動可能なプレイヤーのインデックス
    """
    seats = game_state.table.seats
    num_seats = len(seats)
    current_index = (start_index + 1) % num_seats

    while current_index != start_index:
        seat = seats[current_index]
        if seat.player and seat.player.state not in [PlayerState.OUT, PlayerState.FOLDED]:
            return current_index
        current_index = (current_index + 1) % num_seats
    
    # 誰も見つからなかった場合（通常は起こり得ない）
    return start_index


def determine_next_dealer_index(game_state: GameState) -> int:
    """
    現在のディーラーインデックスを基に、次のディーラーを決定します。
    最初のハンドでは、0番目の席のプレイヤーがディーラーになります。

    Args:
        game_state: 現在のゲーム状態

    Returns:
        次のハンドのディーラーのインデックス
    """
    if game_state.dealer_index is None:
        # 最初のディーラーを探す
        for i, seat in enumerate(game_state.table.seats):
            if seat.player and seat.player.state != PlayerState.OUT:
                return i
        return 0 # 該当者なしの場合

    return _find_next_active_player_index(game_state, game_state.dealer_index)


def assign_positions(game_state: GameState, dealer_index: int) -> None:
    """
    ディーラーの位置を基に、全プレイヤーにポジションを割り振ります。
    例：SB, BB, BTN(ディーラー)など

    Args:
        game_state: 現在のゲーム状態
        dealer_index: 現在のディーラーのインデックス
    """
    active_players = [(i, seat.player) for i, seat in enumerate(game_state.table.seats) if seat.player and seat.player.state != PlayerState.OUT]
    num_active_players = len(active_players)

    # プレイヤー数に応じたポジションのリスト
    # 例：6人なら [SB, BB, LJ, HJ, CO, BTN]
    position_order = [Position.SB, Position.BB]
    if num_active_players > 3:
        position_order.extend([Position.LJ, Position.HJ, Position.CO][:num_active_players - 3])
    position_order.append(Position.BTN)
    
    if num_active_players == 2: # ヘッズアップの場合
        position_order = [Position.BTN, Position.BB] # ディーラーがSBを兼ねる


    # ディーラーの位置からポジションを割り当てる
    try:
        dealer_pos_in_active = [i for i, (idx, player) in enumerate(active_players) if idx == dealer_index][0]
    except IndexError:
        # ディーラーがアクティブでない場合、新しいディーラーを探す必要があるが、
        # ここでは単純に最初のアクティブプレイヤーを基準とする
        dealer_pos_in_active = 0


    for i in range(num_active_players):
        player_index_in_seats = active_players[(dealer_pos_in_active + 1 + i) % num_active_players][0]
        player = game_state.table.seats[player_index_in_seats].player
        position = position_order[i % len(position_order)]
        if player:
            player.position = position

