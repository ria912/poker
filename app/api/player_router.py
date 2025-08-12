from fastapi import APIRouter, HTTPException
from ..services.game import action_manager
from ..schemas import player_schema, game_schema
from ..models.game_state import game_state

router = APIRouter(
    prefix="/player",
    tags=["Player Actions"],
)

@router.post("/action", response_model=game_schema.GameState)
def perform_action(action_data: player_schema.PlayerAction):
    """
    プレイヤーがアクション（フォールド、チェック、コール、ベット、レイズ）を実行する
    """
    # 現在アクションすべきプレイヤーか検証
    if game_state.active_player_id != action_data.player_id:
        raise HTTPException(status_code=403, detail="It's not your turn.")

    try:
        # アクションの種類に応じて、サービス層の適切な関数を呼び出す
        if action_data.action == "FOLD":
            action_manager.handle_fold(game_state, action_data.player_id)
        elif action_data.action == "CHECK":
            action_manager.handle_check(game_state, action_data.player_id)
        elif action_data.action == "CALL":
            action_manager.handle_call(game_state, action_data.player_id)
        elif action_data.action == "BET":
            action_manager.handle_bet(game_state, action_data.player_id, action_data.amount)
        elif action_data.action == "RAISE":
            action_manager.handle_raise(game_state, action_data.player_id, action_data.amount)
        else:
            raise HTTPException(status_code=400, detail="Invalid action.")
        
        # アクション後のゲーム状態を返す
        return game_state
        
    except ValueError as e:
        # 例：ベット額が不正、チェックできない状況でチェックした、など
        raise HTTPException(status_code=400, detail=str(e))