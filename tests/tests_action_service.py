from app.services import game_service, action_service
from app.models.enum import ActionType, SeatState

def test_get_legal_actions_preflop_utg(game_state_with_3_players):
    """プリフロップでUTGが取れるアクションをテスト"""
    gs = game_state_with_3_players
    game_service.start_hand(gs)
    legal_actions = action_service.get_legal_actions(gs)
    
    assert ActionType.FOLD.value in legal_actions
    assert ActionType.CALL.value in legal_actions
    assert legal_actions[ActionType.CALL.value] == 20
    assert ActionType.RAISE.value in legal_actions
    assert legal_actions[ActionType.RAISE.value]["min"] == 40 # 20(コール) + 20(ミニマムレイズ)
    assert legal_actions[ActionType.RAISE.value]["max"] == 1000 # スタック全額

def test_get_legal_actions_all_in(game_state_with_3_players):
    """スタックが足りない場合のオールインアクションをテスト"""
    gs = game_state_with_3_players
    # UTG(Alice)のスタックを少なく設定
    gs.table.seats[0].stack = 15
    game_service.start_hand(gs) # BB=20
    
    legal_actions = action_service.get_legal_actions(gs)
    
    assert ActionType.FOLD.value in legal_actions
    assert ActionType.CALL.value in legal_actions
    # コール額(20)に足りないが、全スタック(15)でコールできる
    assert legal_actions[ActionType.CALL.value] == 15
    # レイズはできないのでRAISEキーは存在しない
    assert ActionType.RAISE.value not in legal_actions

def test_apply_action_all_in_call(game_state_with_3_players):
    """オールインコールのアクションをテスト"""
    gs = game_state_with_3_players
    gs.table.seats[0].stack = 15 # スタックを15に
    game_service.start_hand(gs)
    
    active_player = gs.table.seats[gs.active_seat_index]
    
    action_service.apply_action(gs, ActionType.CALL.value)
    
    assert active_player.stack == 0
    assert active_player.current_bet == 15
    assert active_player.state == SeatState.ALL_IN