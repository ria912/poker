from app.services import game_service, round_service, action_service
from app.models.enum import ActionType, Street, SeatState

# round_service.pyとgame_service.pyのインポートを修正
from app.models.enum import Street as RoundEnum
import sys
sys.modules['..models.enum.Round'] = RoundEnum


def test_is_betting_round_over(game_state_with_3_players):
    """ベッティングラウンドが終了したかの判定をテスト"""
    gs = game_state_with_3_players
    game_service.start_hand(gs) # dealer=0, sb=1, bb=3, utg=0
    
    action_service.apply_action(gs, ActionType.CALL.value) # UTG(0) calls 20
    gs.active_seat_index = round_service.find_next_action_player_index(gs)
    
    action_service.apply_action(gs, ActionType.FOLD.value) # SB(1) folds
    assert not round_service.is_betting_round_over(gs)

    gs.active_seat_index = round_service.find_next_action_player_index(gs)
    action_service.apply_action(gs, ActionType.CHECK.value) # BB(3) checks
    
    assert round_service.is_betting_round_over(gs)

def test_start_next_street_to_flop(game_state_with_3_players):
    """プリフロップからフロップへ正しく移行できるかテスト"""
    gs = game_state_with_3_players
    game_service.start_hand(gs)
    
    # プリフロップを終了させる
    action_service.apply_action(gs, ActionType.CALL.value)
    gs.active_seat_index = round_service.find_next_action_player_index(gs)
    action_service.apply_action(gs, ActionType.CALL.value)
    gs.active_seat_index = round_service.find_next_action_player_index(gs)
    action_service.apply_action(gs, ActionType.CHECK.value)
    
    round_service.start_next_street(gs)
    
    assert gs.current_street == Street.FLOP
    assert len(gs.table.community_cards) == 3
    assert gs.table.pot == 60