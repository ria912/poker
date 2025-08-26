# app/api/table_router.py
from fastapi import APIRouter, Depends, HTTPException
from ..models.game_state import GameState
from ..schemas.response import GameStateResponse
from ..dependencies import get_game_state

router = APIRouter(
    prefix="/table",
    tags=["Table"]
)

@router.get("/", response_model=GameStateResponse)
def get_table_state(game_state: GameState = Depends(get_game_state)):
    """
    現在のテーブルとゲームの全体状態を取得します。
    """
    return GameStateResponse(
        table=game_state.table,
        players=game_state.players,
        active_player_id=game_state.active_player_id,
        message="Current game state."
    )