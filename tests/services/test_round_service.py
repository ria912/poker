# tests/services/test_round_service.py
import pytest
from app.models.game_state import GameState
from app.models.player import Player
from app.models.enum import Round
from app.services.round_service import RoundService

@pytest.fixture
def round_service():
    return RoundService()

@pytest.fixture
def game_state_for_round():
    """ラウンド進行テスト用のGameState"""
    state = GameState(seat_count=3)
    state.table.seats[0].sit_down(Player("p1"), 1000)
    state.table.seats[1].sit_down(Player("p2"), 1000)
    state.table.seats[2].sit_down(Player("p3"), 1000)
    state.dealer_seat_index = 0
    return state

def test_start_flop(round_service, game_state_for_round):
    """フロップラウンド開始のテスト"""
    state = game_state_for_round
    state.current_round = Round.FLOP
    
    round_service.start_new_round(state)
    
    assert len(state.table.community_cards) == 3
    assert state.amount_to_call == 0
    assert state.current_seat_index == 1 # ディーラーの次のアクティブプレイヤー

def test_is_round_over(round_service, game_state_for_round):
    """ラウンド終了判定のテスト"""
    state = game_state_for_round
    # 全員が同額をベットし、アクション済み
    state.amount_to_call = 100
    state.table.seats[0].current_bet = 100
    state.table.seats[0].acted = True
    state.table.seats[1].current_bet = 100
    state.table.seats[1].acted = True
    state.table.seats[2].current_bet = 100
    state.table.seats[2].acted = True
    
    # この状態ではまだアクションプレイヤーがいるので終了しない
    state.current_seat_index = 0 
    assert not round_service.is_round_over(state)

    # アクションすべきプレイヤーがいなくなったら終了
    state.current_seat_index = None 
    assert round_service.is_round_over(state)