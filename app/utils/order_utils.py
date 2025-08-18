# utils/order_utils.py
from typing import Optional, List
from ..models.game_state import GameState
from ..models.player import PlayerState
from ..models.enum import Round


def get_next_active_index(game_state: GameState, current_index: Optional[int]) -> Optional[int]:
    """
    現在の座席インデックスから次に行動可能なプレイヤーを探して返す。
    条件:
        - 座席が occupied
        - PlayerState.ACTIVE のみ（FOLDED, ALL_IN はスキップ）
    """
    seats = game_state.table.seats
    num_seats = len(seats)
    if num_seats == 0:
        return None

    start_index = (current_index + 1) % num_seats if current_index is not None else game_state.table.action_start_index

    for i in range(num_seats):
        idx = (start_index + i) % num_seats
        seat = seats[idx]
        if seat.is_occupied and seat.player.state == PlayerState.ACTIVE:
            return idx

    return None  # 該当なし