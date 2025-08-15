# app/api/game_router.py
from fastapi import APIRouter, Depends, HTTPException
from ..models.game_state import GameState
from ..services import game_service
from ..schemas.response import Message
from ..dependencies import get_game_state

router = APIRouter(
    prefix="/game",
    tags=["Game"]
)

@router.post("/start", response_model=Message)
def start_game(game_state: GameState = Depends(get_game_state)):
    """
    新しいハンドを開始します。
    デッキをシャッフルし、プレイヤーにカードを配ります。
    """
    # 実際にはSB/BBの強制ベットやポジション割り当てなども必要になります
    if len(game_state.players) < 2:
        raise HTTPException(status_code=400, detail="Not enough players to start.")
        
    game_service.start_new_hand(game_state)
    return Message(message="New hand started.")

@router.post("/next_round", response_model=Message)
def proceed_to_next_round(game_state: GameState = Depends(get_game_state)):
    """
    次のベッティングラウンド（フロップ、ターン、リバー）に進みます。
    """
    # 本来は、現在のラウンドのベットが完了しているかなどのチェックが必要です
    game_service.next_round(game_state)
    return Message(message=f"Proceeded to {game_state.table.current_round.value} round.")