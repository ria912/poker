# tests/services/test_game_service.py
import pytest
from app.models.player import Player
from app.models.enum import GameStatus, Round, ActionType
from app.services.game_service import GameService

@pytest.fixture
def game_service():
    return GameService(seat_count=3, big_blind=100, small_blind=50)

def test_start_hand(game_service):
    """ハンド開始処理のテスト"""
    game_service.sit_player(Player("p1"), 0, 1000)
    game_service.sit_player(Player("p2"), 1, 1000)
    game_service.sit_player(Player("p3"), 2, 1000)

    state = game_service.start_hand()
    
    assert state.status == GameStatus.IN_PROGRESS
    assert len(state.table.seats[0].hole_cards) == 2
    assert len(state.table.seats[1].hole_cards) == 2
    assert len(state.table.seats[2].hole_cards) == 2
    
    # SBとBBのベットを確認
    assert state.table.seats[1].current_bet == 50
    assert state.table.seats[2].current_bet == 100
    assert state.table.pot == 0 # ポットに集められるのはラウンド終了後
    assert state.amount_to_call == 100

def test_full_hand_flow_to_showdown(game_service):
    """ハンド開始からショウダウンまでの流れをテスト"""
    p1, p2 = Player("p1"), Player("p2")
    game_service.sit_player(p1, 0, 1000)
    game_service.sit_player(p2, 1, 1000) # Heads-up
    
    state = game_service.start_hand()
    # p1=BTN/SB, p2=BB. プリフロップのアクションはp1から
    assert state.current_seat_index == 0
    
    # Preflop: p1 calls
    game_service.action_service.perform_action(state, 0, ActionType.CALL)
    # p2 checks
    game_service.action_service.perform_action(state, 1, ActionType.CHECK)

    assert game_service.round_service.is_round_over(state)
    game_service.proceed_to_next_stage() # -> Flop

    assert state.current_round == Round.FLOP
    assert len(state.table.community_cards) == 3
    assert state.table.pot == 200 # 100(p1) + 100(p2)

    # Flop: p2 checks, p1 checks
    game_service.action_service.perform_action(state, 1, ActionType.CHECK)
    game_service.action_service.perform_action(state, 0, ActionType.CHECK)
    game_service.proceed_to_next_stage() # -> Turn

    assert state.current_round == Round.TURN
    assert len(state.table.community_cards) == 4

    # Turn: p2 checks, p1 checks
    game_service.action_service.perform_action(state, 1, ActionType.CHECK)
    game_service.action_service.perform_action(state, 0, ActionType.CHECK)
    game_service.proceed_to_next_stage() # -> River

    assert state.current_round == Round.RIVER
    assert len(state.table.community_cards) == 5

    # River: p2 checks, p1 checks
    game_service.action_service.perform_action(state, 1, ActionType.CHECK)
    game_service.action_service.perform_action(state, 0, ActionType.CHECK)
    game_service.proceed_to_next_stage() # -> Showdown

    assert state.current_round == Round.SHOWDOWN
    assert state.status == GameStatus.HAND_COMPLETE
    
    # どちらかがポットを獲得しているはず
    winner_stack = state.table.seats[0].stack
    loser_stack = state.table.seats[1].stack
    assert (winner_stack == 1100 and loser_stack == 900) or \
           (winner_stack == 900 and loser_stack == 1100)
    assert state.table.pot == 0

def test_hand_end_by_fold(game_service):
    """フォールドによるハンド終了のテスト"""
    p1, p2 = Player("p1"), Player("p2")
    game_service.sit_player(p1, 0, 1000)
    game_service.sit_player(p2, 1, 1000)
    
    state = game_service.start_hand()
    
    # Preflop: p1 folds
    game_service.action_service.perform_action(state, 0, ActionType.FOLD)
    
    game_service.proceed_to_next_stage()
    
    assert state.status == GameStatus.HAND_COMPLETE
    assert state.table.seats[0].stack == 950 # SBの50を失う
    assert state.table.seats[1].stack == 1050 # SBの50を獲得
    assert state.table.pot == 0