# FastAPIのDependsと、モデル/スキーマをインポート
from fastapi import APIRouter, HTTPException, Depends
from ..models.game_state import GameState # 型ヒントのためにクラス自体はインポート
from ..schemas import game_schema

# サービスと、新しく作った依存性関数をインポート
from ..services.game import game_service
from ..dependencies import get_game_state # ← こちらをインポートする

router = APIRouter(
    prefix="/game",
    tags=["Game"],
)

@router.get("/state", response_model=game_schema.GameState)
def get_game_state_endpoint(game_state: GameState = Depends(get_game_state)):
    """ゲーム全体の現在の状態を取得する"""
    return game_state

@router.post("/start", response_model=game_schema.GameState)
def start_game(game_state: GameState = Depends(get_game_state)):
    """新しいハンドを開始する"""
    try:
        game_service.start_new_hand(game_state)
        return game_state
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))