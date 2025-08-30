# holdem_app/app/services/ai_agent_service.py
import random
from app.models.game_state import GameState
from app.models.player import Player
from app.models.action import Action
from . import action_service

def decide_action(game_state: GameState, player: Player) -> Action:
    """
    AIプレイヤーの思考ルーチン。
    現在のゲーム状態を分析し、最適なアクションを決定する。
    """
    seat = next((s for s in game_state.table.seats if s.player and s.player.player_id == player.player_id), None)
    if not seat:
        raise ValueError("AI Player not found in seats.")
        
    # 現在可能なアクションを取得
    valid_actions = action_service.get_valid_actions(game_state, seat.index)
    
    # --- ここからAIのロジック ---
    # 現段階ではランダムなアクションを選択する
    chosen_action_type = random.choice(valid_actions)
    
    amount = None
    if chosen_action_type in ["BET", "RAISE", "ALL_IN"]:
        # 仮のベット/レイズ額
        amount = game_state.big_blind 
    
    # --- AIロジックここまで ---

    print(f"AI ({player.name}) decides to {chosen_action_type.name}")
    return Action(player_id=player.player_id, action_type=chosen_action_type, amount=amount)
