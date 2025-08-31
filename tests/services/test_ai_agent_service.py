# tests/services/test_ai_agent_service.py
from app.services.ai import ai_agent_service
from app.models.enum import ActionType

def test_decide_action_can_check(game_state):
    # チェック可能な状況
    game_state.current_seat_index = 0
    game_state.amount_to_call = 0
    
    action = ai_agent_service.decide_action(game_state)
    assert action.action_type == ActionType.CHECK

def test_decide_action_must_fold(game_state):
    # ベットに直面している状況
    game_state.current_seat_index = 0
    game_state.amount_to_call = 100
    
    action = ai_agent_service.decide_action(game_state)
    assert action.action_type == ActionType.CALL
