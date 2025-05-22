# api/game.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Body
from state.game_state import GameState

router = APIRouter()

game_state = GameState()

@router.get("/state")
async def get_game_state(show_all_hands: bool = False):
    """
    現在のゲーム状態を返す。
    show_all_hands=True なら全プレイヤーの手札も返す（デバッグ用など）
    """
    state = game_state.get_state(show_all_hands=show_all_hands)
    return JSONResponse(content=state)

@router.post("/action")
async def post_action(action: dict = Body(...)):
    """
    人間プレイヤーのアクションを受け付ける。
    action = {"action": "fold/call/bet/raise/check", "amount": 0〜}
    """
    try:
        result = game_state.human_action(action)
    except Exception as e:
        if str(e) == "waiting_for_human_action":
            return JSONResponse({"status": "waiting_for_human"})
        raise HTTPException(status_code=400, detail=str(e))
    
    # AIのアクションを進めるループ（AIターンが続く限り）
    while result == "ai_acted":
        try:
            result = game_state.proceed_game()
        except Exception as e:
            if str(e) == "waiting_for_human_action":
                result = "waiting_for_human"
                break
            raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse({"status": result, "state": game_state.get_state()})

@router.post("/start")
async def start_hand():
    """
    新しい手札を開始する
    """
    game_state.start_new_hand()
    return JSONResponse({"status": "hand_started", "state": game_state.get_state()})
