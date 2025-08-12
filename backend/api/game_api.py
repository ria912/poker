# backend/api/game_api.py
from fastapi import APIRouter
from backend.schemas.game_schema import StartGameRequest, GameStateResponse
from backend.services.game.game_manager import start_game_logic

router = APIRouter()

@router.post("/start_game", response_model=GameStateResponse)
def start_game(req: StartGameRequest) -> GameStateResponse:
    return start_game_logic(req)