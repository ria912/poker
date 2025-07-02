# backend/api/ai_game.py

from fastapi import APIRouter
from backend.state.game_state_ai import ai_game_state
from backend.schemas import GameStateResponse

router = APIRouter()

@router.post("/game/ai_start", response_model=GameStateResponse)
def start_ai_game():
    ai_game_state.start_new_hand()
    return ai_game_state.get_state()
