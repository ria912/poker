from typing import List, Optional
from gemini_app.models.table import Seat

def get_next_active_seat_index(seats: List[Seat], current_index: int) -> Optional[int]:
    """
    指定されたインデックスの次に行動可能な（アクティブな）プレイヤーの座席インデックスを見つける。
    アクティブなプレイヤーが見つかるまでテーブルを一周する。
    """
    start_index = (current_index + 1) % len(seats)
    
    # 開始位置から一周して探す
    for i in range(len(seats)):
        check_index = (start_index + i) % len(seats)
        seat = seats[check_index]
        # プレイヤーがいて、かつアクティブ（フォールドしていない）ならそのインデックスを返す
        if seat.player and seat.player.is_active:
            return check_index
            
    # アクティブなプレイヤーが他にいない場合
    return None

def get_active_player_count(seats: List[Seat]) -> int:
    """アクティブなプレイヤーの数を数える"""
    return sum(1 for seat in seats if seat.player and seat.player.is_active)