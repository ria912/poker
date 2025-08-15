# app/api/player_router.py
from fastapi import APIRouter, Depends, HTTPException
from ..models.game_state import GameState
from ..models.player import Player
from ..schemas.player import PlayerCreate
from ..schemas.response import Message
from ..services import player_service
from ..dependencies import get_game_state

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.post("/", response_model=Player)
def add_player_to_table(player_data: PlayerCreate, game_state: GameState = Depends(get_game_state)):
    """
    新しいプレイヤーをテーブルの空いている席に追加します。
    """
    player = player_service.add_player(game_state, name=player_data.name, stack=player_data.stack)
    if not player:
        raise HTTPException(status_code=400, detail="No available seats.")
    return player

@router.delete("/{player_id}", response_model=Message)
def remove_player_from_table(player_id: str, game_state: GameState = Depends(get_game_state)):
    """
    指定されたプレイヤーをテーブルから削除します。
    """
    if not player_service.remove_player(game_state, player_id):
        raise HTTPException(status_code=404, detail="Player not found.")
    return Message(message=f"Player {player_id} has been removed.")

# ここに将来的にプレイヤーのアクション用エンドポイント（/players/{player_id}/action）を追加します。
# アクションのロジックが service 層に実装されたら、一緒に構築しましょう！