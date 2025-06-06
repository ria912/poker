# api/game.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.state.game_state import game_state

router = APIRouter()


# ----- リクエスト用モデル -----
class ActionRequest(BaseModel):
    action: str
    amount: int = 0  # チェックやフォールドなど、amount不要なケースを考慮


# ----- POST /api/game/start -----
@router.post("/game/start")
def start_game():
    try:
        result = game_state.start_new_hand()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ゲーム開始エラー: {str(e)}")


# ----- POST /api/game/action -----
@router.post("/game/action")
def post_action(request: ActionRequest):
    try:
        result = game_state.receive_human_action(request.action, request.amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"アクションエラー: {str(e)}")


# ----- GET /api/game/state -----
@router.get("/game/state")
def get_state():
    return game_state._build_response()