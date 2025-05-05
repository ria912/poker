from fastapi import APIRouter
from backend.core.game_manager import game_state

router = APIRouter()

@router.get("/game/state")
def get_game_state():
    return game_state.to_dict()

@router.post("/game/action")
def post_player_action(action_data: dict):
    # ここでプレイヤーのアクションを処理する
    result = game_state.apply_action(action_data)
    return result
