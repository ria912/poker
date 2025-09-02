# app/api/endpoints/helpers.py

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

from app.models.game_state import GameState
from app.models.enum import ActionType, Round, GameStatus, SeatStatus, Position
from app.models.action import Action as GameAction
from app.services import action_service, hand_manager, round_manager
from app.services.ai import ai_agent_service

# --- Pydanticモデル (APIレスポンスの型定義) ---
class PlayerInfo(BaseModel):
    player_id: str
    name: str
    is_ai: bool

class CardInfo(BaseModel):
    rank: str
    suit: str

class SeatInfo(BaseModel):
    index: int
    is_occupied: bool
    player: Optional[PlayerInfo]
    stack: int
    current_bet: int
    bet_total: int
    status: SeatStatus
    position: Optional[Position]
    hole_cards: List[CardInfo]

class GameStateResponse(BaseModel):
    game_id: str
    status: GameStatus
    seats: List[SeatInfo]
    community_cards: List[CardInfo]
    pot: int
    current_round: Round
    current_seat_index: Optional[int]
    amount_to_call: int
    last_message: Optional[str] = None
    valid_actions: Optional[List[Dict[str, Any]]] = None

# --- ヘルパー関数 ---

def get_game_or_404(game_id: str, games: Dict[str, GameState]) -> GameState:
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]

def format_game_state_for_response(game_id: str, game_state: GameState, message: Optional[str] = None) -> GameStateResponse:
    valid_actions = None
    current_seat_idx = game_state.current_seat_index
    if current_seat_idx is not None and game_state.status == GameStatus.IN_PROGRESS:
        current_seat = game_state.table.seats[current_seat_idx]
        if current_seat.player and not current_seat.player.is_ai:
             valid_actions = action_service.get_valid_actions(game_state, current_seat_idx)

    return GameStateResponse(
        game_id=game_id,
        status=game_state.status,
        seats=[
            SeatInfo(
                index=s.index,
                is_occupied=s.is_occupied,
                player=PlayerInfo(player_id=s.player.player_id, name=s.player.name, is_ai=s.player.is_ai) if s.player else None,
                stack=s.stack,
                current_bet=s.current_bet,
                bet_total=s.bet_total,
                status=s.status,
                position=s.position,
                hole_cards=[CardInfo(rank=c.rank, suit=c.suit) for c in s.hole_cards] if s.player and not s.player.is_ai else [],
            ) for s in game_state.table.seats
        ],
        community_cards=[CardInfo(rank=c.rank, suit=c.suit) for c in game_state.table.community_cards],
        pot=game_state.table.pot,
        current_round=game_state.current_round,
        current_seat_index=game_state.current_seat_index,
        amount_to_call=game_state.amount_to_call,
        last_message=message,
        valid_actions=valid_actions
    )

def _advance_game_until_human_action(game_state: GameState, games: Dict[str, GameState]) -> str:
    message = ""
    max_turns = len(game_state.table.seats) * 3 
    turn_count = 0

    while game_state.status == GameStatus.IN_PROGRESS and turn_count < max_turns:
        current_seat = game_state.table.seats[game_state.current_seat_index]
        
        if current_seat.player and not current_seat.player.is_ai and current_seat.status == SeatStatus.ACTIVE:
            return message

        if current_seat.status == SeatStatus.ACTIVE:
            action = ai_agent_service.decide_action(game_state)
            message += f"{current_seat.player.name} chose {action.action_type.name} {action.amount or ''}. "
            action_service.process_action(game_state, action)

            if round_manager.is_betting_round_over(game_state):
                message += _progress_to_next_stage(game_state)
                continue

        game_state.current_seat_index = round_manager.position_service.get_next_active_player_index(
            game_state, game_state.current_seat_index
        )
        turn_count += 1
        
    return message

def _progress_to_next_stage(game_state: GameState) -> str:
    message = ""
    if hand_manager._is_hand_over(game_state):
        hand_manager._conclude_hand(game_state)
        return "Hand concluded."

    game_state.table.collect_bets()
    
    current_round_index = list(Round).index(game_state.current_round)
    if current_round_index < list(Round).index(Round.RIVER):
        next_round = list(Round)[current_round_index + 1]
        game_state.current_round = next_round
        
        hand_manager.proceed_to_next_round(game_state)
        round_manager.prepare_for_new_round(game_state)
        message = f"Proceeding to {next_round.name}."
    else:
        hand_manager._conclude_hand(game_state)
        message = "Showdown!"

    return message

