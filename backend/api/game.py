# api/game.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from state.game_state import game_state
from models.enum import Action

router = APIRouter()

# アクション用リクエストボディ
class ActionRequest(BaseModel):
    action: str
    amount: int = 0  # raise/betの場合のみ使用

# 新しいハンドを開始
@router.post("/api/game/start")
def start_game():
    try:
        return game_state.start_new_hand()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 人間のアクションを受け取る
@router.post("/api/game/action")
def submit_action(req: ActionRequest):
    try:
        return game_state.receive_human_action(req.action, req.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ゲーム状態を取得（SPAの定期ポーリング用など）
@router.get("/api/game/state")
def get_game_state():
    return game_state.get_state()

# アクションログを取得（リプレイ・履歴表示などに使える）
@router.get("/api/game/log")
def get_action_log():
    return game_state.get_action_log()
