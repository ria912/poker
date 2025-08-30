# tests/services/test_action_service.py
import pytest
from app.models.game_state import GameState
from app.models.player import Player
from app.models.enum import ActionType, SeatStatus
from app.services.action_service import ActionService

@pytest.fixture
def action_service():
    return ActionService()

@pytest.fixture
def game_state_preflop():
    """プリフロップアクション開始直後のGameStateをセットアップ"""
    state = GameState(seat_count=3)
    state.table.seats[0].sit_down(Player("p1"), 1000)
    state.table.seats[1].sit_down(Player("p2"), 1000)
    state.table.seats[2].sit_down(Player("p3"), 1000)

    # ポジション設定
    state.dealer_seat_index = 0
    state.table.seats[0].position = "BTN"
    state.table.seats[1].position = "SB"
    state.table.seats[2].position = "BB"
    
    # ブラインドベット
    state.table.seats[1].bet(50)
    state.table.seats[2].bet(100)
    
    state.amount_to_call = 100
    state.min_raise_amount = 200
    state.current_seat_index = 0 # BTNのアクションから
    return state

def test_perform_fold(action_service, game_state_preflop):
    """フォールドアクションのテスト"""
    state = game_state_preflop
    action_service.perform_action(state, 0, ActionType.FOLD)
    
    assert state.table.seats[0].status == SeatStatus.FOLDED
    assert state.current_seat_index == 1 # 次のプレイヤー(SB)にターンが移る

def test_perform_call(action_service, game_state_preflop):
    """コールアクションのテスト"""
    state = game_state_preflop
    seat = state.table.seats[0]
    initial_stack = seat.stack
    
    action_service.perform_action(state, 0, ActionType.CALL)

    assert seat.status == SeatStatus.ACTIVE
    assert seat.current_bet == 100
    assert seat.stack == initial_stack - 100
    assert state.current_seat_index == 1

def test_perform_raise(action_service, game_state_preflop):
    """レイズアクションのテスト"""
    state = game_state_preflop
    seat = state.table.seats[0]
    initial_stack = seat.stack
    raise_total_amount = 300
    
    action_service.perform_action(state, 0, ActionType.RAISE, amount=raise_total_amount)

    assert seat.current_bet == raise_total_amount
    assert seat.stack == initial_stack - raise_total_amount
    assert state.amount_to_call == raise_total_amount
    assert state.min_raise_amount == 500 # 300 + (300-100)
    assert state.last_raiser_seat_index == 0
    assert not state.table.seats[1].acted # 他プレイヤーのアクションは未完了になる
    assert state.current_seat_index == 1

def test_invalid_check(action_service, game_state_preflop):
    """ベットがある場合にチェックできないことのテスト"""
    state = game_state_preflop
    with pytest.raises(ValueError, match="Cannot check"):
        action_service.perform_action(state, 0, ActionType.CHECK)