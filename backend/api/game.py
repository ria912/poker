# api/game.py
from fastapi import APIRouter
from state.game_state import game_state

router = APIRouter()

@router.post("/start")
def start_new_hand():
    game_state.new_hand()
    return {"status": "new hand started", "state": game_state.table.to_dict()}

@router.post("/action")
def send_action(action: str, amount: int = 0):
    game_state.round_manager.set_human_action((action, amount))
    result = game_state.round_manager.resume_after_human_action()
    return {
        "result": result,
        "state": game_state.table.to_dict()
    }

@router.get("/state")
def get_state():
    return game_state.table.to_dict()
