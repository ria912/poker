from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid

# 必要なモデルとサービスをインポート
from app.models.game_state import GameState
from app.models.player import Player
from app.models.action import Action as GameAction
from app.models.enum import GameStatus, SeatStatus, ActionType
from app.services import hand_manager, action_service, round_manager
from .helpers import (
    format_game_state_for_response, 
    get_game_or_404,
    _advance_game_until_human_action,
    _progress_to_next_stage,
    GameStateResponse
)

# --- ルーターの作成 ---
router = APIRouter(
    prefix="/games",
    tags=["Games"],
)

# --- グローバルなゲームストレージ ---
games: Dict[str, GameState] = {}

# --- Pydanticモデル (APIリクエストの型定義) ---

class PlayerCreate(BaseModel):
    name: str
    stack: int = 1000
    is_ai: bool = False

class GameCreateRequest(BaseModel):
    players: List[PlayerCreate]
    small_blind: int = 10
    big_blind: int = 20
    seat_count: int = Field(default=6, ge=2, le=9) # 2-9人の範囲で設定可能に

class ActionPayload(BaseModel):
    player_id: str
    action_type: ActionType
    amount: Optional[int] = None

# --- APIエンドポイントの実装 ---

@router.post("", response_model=GameStateResponse, status_code=201)
def create_game(req: GameCreateRequest):
    """新しいゲームセッションを作成し、最初のハンドを開始します。"""
    game_id = str(uuid.uuid4())
    game_state = GameState(
        big_blind=req.big_blind,
        small_blind=req.small_blind,
        seat_count=req.seat_count
    )

    human_player_found = False
    for i, p_info in enumerate(req.players):
        if i >= req.seat_count: break
        player = Player(name=p_info.name, is_ai=p_info.is_ai)
        game_state.table.sit_player(player, i, p_info.stack)
        if not p_info.is_ai:
            human_player_found = True

    if not human_player_found:
        raise HTTPException(status_code=400, detail="At least one human player is required.")

    games[game_id] = game_state
    
    hand_manager.start_new_hand(game_state)
    message = "New hand started. "
    
    if game_state.status == GameStatus.IN_PROGRESS:
        message += _advance_game_until_human_action(game_state, games)

    return format_game_state_for_response(game_id, game_state, message)


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(game_id: str):
    """指定されたゲームの現在の状態を取得します。"""
    game_state = get_game_or_404(game_id, games)
    return format_game_state_for_response(game_id, game_state)


@router.post("/{game_id}/action", response_model=GameStateResponse)
def player_action(game_id: str, action: ActionPayload):
    """人間プレイヤーのアクションを処理します。"""
    game_state = get_game_or_404(game_id, games)
    
    if game_state.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Game is not in progress.")

    current_seat_idx = game_state.current_seat_index
    if current_seat_idx is None:
        raise HTTPException(status_code=400, detail="It's not anyone's turn.")
    
    current_seat = game_state.table.seats[current_seat_idx]
    if not current_seat.player or current_seat.player.player_id != action.player_id:
        raise HTTPException(status_code=403, detail="It's not your turn.")

    # TODO: アクションの正当性検証 (ValidActionに含まれているかなど)
    
    game_action = GameAction(player_id=action.player_id, action_type=action.action_type, amount=action.amount)
    action_service.process_action(game_state, game_action)
    message = f"{current_seat.player.name} chose {action.action_type.name} {action.amount or ''}. "
    
    if round_manager.is_betting_round_over(game_state):
        message += _progress_to_next_stage(game_state)
    else:
        game_state.current_seat_index = round_manager.position_service.get_next_active_player_index(
            game_state, current_seat_idx
        )
    
    if game_state.status == GameStatus.IN_PROGRESS:
        message += _advance_game_until_human_action(game_state, games)

    return format_game_state_for_response(game_id, game_state, message)


@router.post("/{game_id}/next_hand", response_model=GameStateResponse)
def start_next_hand(game_id: str):
    """現在のハンドを終了し、次のハンドを開始します。"""
    game_state = get_game_or_404(game_id, games)
    
    if game_state.status not in [GameStatus.HAND_COMPLETE, GameStatus.WAITING]:
        raise HTTPException(status_code=400, detail="Cannot start a new hand yet.")
         
    for seat in game_state.table.seats:
        if seat.is_occupied and seat.stack == 0:
            game_state.table.stand_player(seat.index)

    hand_manager.start_new_hand(game_state)
    if game_state.status == GameStatus.WAITING:
        return format_game_state_for_response(game_id, game_state, "Waiting for more players.")

    message = "Started next hand. "
    if game_state.status == GameStatus.IN_PROGRESS:
        message += _advance_game_until_human_action(game_state, games)
    
    return format_game_state_for_response(game_id, game_state, message)

