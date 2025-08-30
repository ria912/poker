# tests/services/test_hand_manager.py
from app.services import hand_manager, position_service
from app.models.enum import GameStatus, Position

def test_start_new_hand(game_state):
    # 初期ディーラー位置を設定
    game_state.dealer_seat_index = 0
    hand_manager.start_new_hand(game_state)

    assert game_state.status == GameStatus.IN_PROGRESS
    
    # --- ここから修正 ---
    # ポジション名から座席を動的に取得して検証する
    sb_seat = position_service.get_seat_by_position(game_state, Position.SB)
    bb_seat = position_service.get_seat_by_position(game_state, Position.BB)

    # Blinds are posted
    assert sb_seat is not None
    assert sb_seat.current_bet == 50
    assert bb_seat is not None
    assert bb_seat.current_bet == 100
    # --- 修正ここまで ---

    assert game_state.amount_to_call == 100
    
    # Cards are dealt
    for seat in position_service.get_occupied_seats(game_state):
        assert len(seat.hole_cards) == 2

def test_conclude_hand(game_state):
    game_state.table.pot = 1000
    # s1 is the only one not folded
    game_state.table.seats[0].status = "FOLDED"
    game_state.table.seats[2].status = "FOLDED"
    
    initial_stack = game_state.table.seats[1].stack
    
    hand_manager._conclude_hand(game_state)
    
    assert game_state.status == GameStatus.HAND_COMPLETE
    assert game_state.table.seats[1].stack == initial_stack + 1000

