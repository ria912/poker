# holdem_app/app/services/position_service.py
from app.models.game_state import GameState
from app.models.enum import Position

def rotate_dealer_button(game_state: GameState):
    """ディーラーボタンを次のアクティブなプレイヤーに移動させる"""
    seats = game_state.table.seats
    num_seats = len(seats)
    
    if game_state.dealer_seat_index is None:
        # 最初はアクティブなプレイヤーからランダムに選ぶ
        active_indices = [s.index for s in seats if s.is_occupied]
        start_index = active_indices[0] if active_indices else 0
    else:
        start_index = (game_state.dealer_seat_index + 1) % num_seats

    for i in range(num_seats):
        next_index = (start_index + i) % num_seats
        if seats[next_index].is_occupied:
            game_state.dealer_seat_index = next_index
            print(f"Dealer button is at seat {next_index}")
            return
            
    # アクティブプレイヤーがいない場合
    game_state.dealer_seat_index = None

def get_next_active_player_index(game_state: GameState, start_index: int) -> int:
    """指定したインデックスの次に行動可能なプレイヤーのインデックスを返す"""
    seats = game_state.table.seats
    num_seats = len(seats)
    for i in range(1, num_seats + 1):
        next_index = (start_index + i) % num_seats
        if seats[next_index].is_active: # is_active でチェック
            return next_index
    return start_index # 1人しかいない場合

def assign_positions(game_state: GameState):
    """各プレイヤーにポジション（SB, BBなど）を割り当てる"""
    # dealer_seat_index を基準にSB, BB, ... を決定するロジック
    print("Assigning positions...")
    pass

def get_first_to_act(game_state: GameState) -> int:
    """そのラウンドで最初にアクションするプレイヤーのインデックスを返す"""
    # プリフロップならBBの次、フロップ以降ならSBの次（アクティブなプレイヤー）
    # ... 実装 ...
    # 仮でディーラーの次を返す
    return get_next_active_player_index(game_state, game_state.dealer_seat_index)
