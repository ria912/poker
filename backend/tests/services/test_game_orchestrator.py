# tests/services/test_game_orchestrator.py
from unittest.mock import patch
from app.services.game_orchestrator import GameOrchestrator

def test_run_game_calls_play_hand(game_state):
    """run_gameがplay_handを正しい回数呼び出すかテスト"""
    orchestrator = GameOrchestrator(game_state)

    # 2回目の呼び出しでプレイヤーが1人になる状況をシミュレート
    def side_effect():
        if mock_play_hand.call_count == 2:
            game_state.table.stand_player(0)
            game_state.table.stand_player(1)

    with patch.object(orchestrator, 'play_hand', side_effect=side_effect) as mock_play_hand:
        orchestrator.run_game(num_hands=5)
        # 2ハンド実行後、プレイヤーが足りなくなりループが止まるはず
        assert mock_play_hand.call_count == 2

@patch('app.services.ai_agent_service.decide_action')
def test_get_action_for_player_ai(mock_decide_action, game_state):
    """AIプレイヤーのアクション取得をテスト"""
    orchestrator = GameOrchestrator(game_state)
    game_state.current_seat_index = 0
    # プライベートメソッドをテスト
    orchestrator._get_action_for_player(game_state)
    mock_decide_action.assert_called_once_with(game_state)
