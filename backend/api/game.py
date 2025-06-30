from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.state.single_game_state import game_state
from backend.models.enum import Action
from backend.schemas import GameStateResponse, MessageResponse

router = APIRouter()

# ----- リクエスト用モデル -----
class ActionRequest(BaseModel):
    action: Action
    amount: int = 0  # チェックやフォールドなど、amount不要なケースを考慮

# ----- POST /api/game/start -----
@router.post("/game/start", response_model=GameStateResponse)
def start_game():
    try:
        result = game_state.start_new_hand()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ゲーム開始エラー: {str(e)}")

# ----- POST /api/game/action -----
@router.post("/game/action", response_model=GameStateResponse)
def post_action(request: ActionRequest):
    try:
        result = game_state.receive_human_action(request.action, request.amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"アクションエラー: {str(e)}")

# ----- GET /api/game/state -----
@router.get("/game/state", response_model=GameStateResponse)
def get_state():
    try:
        return game_state.get_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状態取得エラー: {str(e)}")