# backend/api/game_api.py
from fastapi import APIRouter
from schemas.game_schemas import StartGameRequest, GameStateResponse
from services.game_service import start_game_logic

router = APIRouter()

@router.post("/start_game", response_model=GameStateResponse)
def start_game(req: StartGameRequest) -> GameStateResponse:
    return start_game_logic(req)