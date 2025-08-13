from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

#
# --- 依存関係のインポート ---
#
# モデル（データ構造）
from models import GameState, Action, GameStatus, game_state
# サービス（ビジネスロジック）
from services.game.game_service import game_service
from services.game.action_manager import action_manager

#
# --- APIルーターの初期化 ---
#
router = APIRouter(
    prefix="/game",  # このファイル内のAPIは全て /game から始まるURLになる
    tags=["Game"],   # FastAPIのドキュメントでグループ化される
)

#
# --- APIリクエストのデータ構造定義 (Schema) ---
#
class ActionRequest(BaseModel):
    """プレイヤーのアクションを受け取るためのリクエストボディ"""
    player_id: str
    action: Action
    amount: int = 0

#
# --- APIエンドポイントの定義 ---
#

@router.get("/state", response_model=GameState)
async def get_game_state():
    """
    現在のゲーム状態を全て取得します。
    フロントエンドが画面を更新する際に使います。
    """
    return game_state

@router.post("/start", response_model=GameState)
async def start_game():
    """
    新しいハンドを開始します。
    """
    try:
        # ゲームサービスを呼び出して新しいハンドを開始
        game_service.start_new_hand()
    except ValueError as e:
        # サービス内でエラーが発生した場合 (例: プレイヤーが足りない)
        raise HTTPException(status_code=400, detail=str(e))
    
    # 最新のゲーム状態を返す
    return game_state

@router.post("/action", response_model=GameState)
async def perform_action(request: ActionRequest):
    """
    プレイヤーのアクション（コール、レイズなど）を処理します。
    """
    try:
        # アクションマネージャーを呼び出してアクションを処理
        action_manager.handle_action(request.player_id, request.action, request.amount)
        
        # もしアクションの結果、ラウンドが終了していたら、次のラウンドに進める
        if game_state.game_status == GameStatus.ROUND_OVER:
            game_service.advance_to_next_round()

    except ValueError as e:
        # サービス内でエラーが発生した場合 (例: 不正なアクション)
        raise HTTPException(status_code=400, detail=str(e))
    
    # 最新のゲーム状態を返す
    return game_state