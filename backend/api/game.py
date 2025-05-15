# api/game.py
from fastapi import APIRouter
from pydantic import BaseModel
from state.game_state import game_state

router = APIRouter()

class ActionRequest(BaseModel):
    action: str
    amount: int = 0

@router.post("/start")
def start_new_hand():
    game_state.new_hand()
    return {"status": "new hand started", "state": game_state.table.to_dict()}

@router.post("/action")
def send_action(req: ActionRequest):
    game_state.round_manager.set_human_action((req.action, req.amount))
    result = game_state.round_manager.resume_after_human_action()
    return {
        "result": result,
        "state": game_state.table.to_dict()
    }

@router.get("/state")
def get_state():
    return game_state.table.to_dict()
