from fastapi import APIRouter, HTTPException
from backend.states.game_state import GameState
from backend.models.enum import Action
from backend.schemas.game_schema import (
    StartGameRequest, 
    ActionRequest,
    GameStateResponse,
    WinnerInfoResponse
)

router = APIRouter()

# グローバルなGameState（簡易なセッション用）
game_state: GameState = None

@router.post("/start_game")
def start_game(request: StartGameRequest) -> GameStateResponse:
    global game_state
    game_state = GameState(player_num=request.player_num)
    game_state.reset()
    return GameStateResponse(**game_state.get_observation())

@router.post("/action")
def play_action(request: ActionRequest) -> GameStateResponse:
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started")
    game_state.step(request.action, request.amount or 0)
    return GameStateResponse(**game_state.get_observation())

@router.get("/state")
def get_state() -> GameStateResponse:
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started")
    return GameStateResponse(**game_state.get_observation())

@router.post("/simulate_ai")
def simulate_ai() -> GameStateResponse:
    if game_state is None:
        raise HTTPException(status_code=400, detail="Game not started")

    # 人間以外のAIプレイヤーにアクションさせる（簡易ロジック）
    while not game_state.is_hand_over() and not game_state.table.get_current_seat().is_human:
        legal_actions = game_state.get_legal_actions()
        first_action = legal_actions[0]["action"]
        amount = legal_actions[0].get("amount", 0)
        game_state.step(Action[first_action], amount)
    
    return GameStateResponse(**game_state.get_observation())

@router.get("/result")
def get_result() -> WinnerInfoResponse:
    if game_state is None or not game_state.is_hand_over():
        raise HTTPException(status_code=400, detail="Hand not over yet")
    return WinnerInfoResponse(**game_state.get_winner_info())
