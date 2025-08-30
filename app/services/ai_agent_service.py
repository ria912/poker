# holdem_app/app/services/ai_agent_service.py
from app.models.game_state import GameState
from app.models.action import Action
from app.models.enum import ActionType
from app.services import action_service

def decide_action(game_state: GameState) -> Action:
    """
    現在のゲーム状態に基づいてAIプレイヤーのアクションを決定する。
    - チェックできるならチェック
    - そうでなければフォールド
    """
    current_seat_index = game_state.current_seat_index
    seat = game_state.table.seats[current_seat_index]
    player_id = seat.player.player_id
    
    # --- ここから修正 ---
    valid_actions = action_service.get_valid_actions(game_state, current_seat_index)
    
    # 有効なアクションの中から戦略に基づいて選択
    action_types = [a['type'] for a in valid_actions]

    if ActionType.CHECK in action_types:
        return Action(player_id=player_id, action_type=ActionType.CHECK)
    
    if ActionType.FOLD in action_types:
        return Action(player_id=player_id, action_type=ActionType.FOLD)

    # フォールドもチェックもできない場合 (例:オールインコールしかできない)
    if ActionType.CALL in action_types:
        call_action = next(a for a in valid_actions if a['type'] == ActionType.CALL)
        return Action(player_id=player_id, action_type=ActionType.CALL, amount=call_action['amount'])

    # 万が一上記に当てはまらない場合（基本的には起こらない）
    # 最も安全なアクション（通常はフォールド）を選択
    return Action(player_id=player_id, action_type=ActionType.FOLD)
    # --- 修正ここまで ---
