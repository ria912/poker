# holdem_app/app/services/position_service.py
import random
from typing import List

from ..models.game_state import GameState
from ..models.enum import Position

def _get_active_player_indices(gs: GameState) -> List[int]:
    """ハンドに参加可能なプレイヤーのシートインデックスリストを返す"""
    return [
        s.index for s in gs.table.seats if s.is_occupied and s.stack > 0
    ]

def determine_dealer_seat(gs: GameState, active_indices: List[int]) -> int:
    """ディーラーボタンのシートインデックスを決定する"""
    if not active_indices:
        raise ValueError("No active players to determine dealer seat.")

    if gs.dealer_seat_index is None:
        # 最初のハンドはアクティブプレイヤーからランダムに選ぶ
        return random.choice(active_indices)
    else:
        # 時計回りで次のアクティブプレイヤーを探す
        current_index = (gs.dealer_seat_index + 1) % len(gs.table.seats)
        while True:
            if current_index in active_indices:
                return current_index
            current_index = (current_index + 1) % len(gs.table.seats)


def assign_positions(gs: GameState) -> GameState:
    """
    ディーラーを決定し、各アクティブプレイヤーにポジションを割り当てる。
    """
    active_indices = _get_active_player_indices(gs)
    num_players = len(active_indices)

    if num_players < 2:
        return gs # プレイ人数が足りない

    # 1. ディーラーボタンを決定
    dealer_index = determine_dealer_seat(gs, active_indices)
    gs.dealer_seat_index = dealer_index
    
    # 2. ポジションを割り当て
    # 参加人数に応じたポジションリストを作成
    # 6-maxの場合: BTN, SB, BB, LJ, HJ, CO
    position_order_map = {
        6: [Position.BTN, Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO],
        5: [Position.BTN, Position.SB, Position.BB, Position.HJ, Position.CO],
        4: [Position.BTN, Position.SB, Position.BB, Position.CO],
        3: [Position.BTN, Position.SB, Position.BB],
        2: [Position.SB, Position.BB], # Heads-up: SB is also the dealer
    }
    positions_to_assign = position_order_map.get(num_players, position_order_map[6])
    
    # ディーラーから時計回りに割り当て
    start_pos_index = active_indices.index(dealer_index)
    
    # Heads-up の特別処理 (DealerがSB)
    if num_players == 2:
        start_pos_index = active_indices.index(dealer_index)
        positions_map = {
            active_indices[start_pos_index]: Position.SB, # Dealer is SB
            active_indices[(start_pos_index + 1) % num_players]: Position.BB,
        }
    else:
        positions_map = {}
        for i, pos_name in enumerate(positions_to_assign):
            player_seat_index = active_indices[(start_pos_index + i) % num_players]
            positions_map[player_seat_index] = pos_name

    for seat in gs.table.seats:
        if seat.index in positions_map:
            seat.position = positions_map[seat.index]
        else:
            seat.position = None # ハンド不参加のプレイヤーはポジションなし

    return gs
