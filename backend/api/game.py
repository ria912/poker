# api/game.py
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from state.game_state import GameState
from models.human_player import WaitingForHumanAction

router = APIRouter()

# ゲーム状態を一括管理するオブジェクト（シングルプレイヤー想定）
game_state = GameState()

@router.get("/state")
async def get_game_state(show_all_hands: bool = False):
    """現在のゲーム状態を返す。手札を見せるかはフラグで制御"""
    try:
        return JSONResponse(content=game_state.get_state(show_all_hands))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状態取得エラー: {e}")

@router.post("/start")
async def start_hand():
    """新しい手札を配ってゲームを開始"""
    try:
        game_state.start_new_hand()
        return JSONResponse({"status": "hand_started", "state": game_state.get_state()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"新規ハンド開始エラー: {e}")

@router.post("/action")
async def post_action(action: dict = Body(...)):
    """
    人間プレイヤーのアクションを受け取る。
    形式: {"action": "fold/call/raise", "amount": 数値}
    """
    try:
        result = game_state.human_action(action)
    except WaitingForHumanAction:
        return JSONResponse({"status": "waiting_for_human"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"アクションエラー: {e}")
    
    # AIターンが続く限りループして進行
    loop_count = 0
    while result == "ai_acted":
        loop_count += 1
        if loop_count > 20:
            raise HTTPException(status_code=500, detail="AIターンが多すぎます")
        try:
            result = game_state.proceed_game()
        except WaitingForHumanAction:
            break
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"AI進行エラー: {e}")
    
    # 最新状態を返す
    return JSONResponse({"status": result, "state": game_state.get_state()})
