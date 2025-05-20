# api/game.py
from fastapi import APIRouter
from backend.state.game_state import game_state  # 状態管理
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/game/one_action")
def one_action():
    result = game_state.round_manager.proceed_one_action()

    return JSONResponse({
        "status": result,
        "table": game_state.table.to_dict()
    })

@router.post("/game/human_action")
def human_action(action: str, amount: int):
    game_state.round_manager.set_human_action((action, amount))
    result = game_state.round_manager.resume_after_human_action()

    return JSONResponse({
        "status": result,
        "table": game_state.table.to_dict()
    })