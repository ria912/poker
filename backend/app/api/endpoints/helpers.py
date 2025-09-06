# app/api/endpoints/helpers.py

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

from app.models.game_state import GameState
from app.models.enum import ActionType, Round, GameStatus, SeatStatus, Position
from app.services import action_service, hand_manager, round_manager
from app.services.ai import ai_agent_service

# --- (PlayerInfo, CardInfo, WinnerInfo, SeatInfoモデルは変更なし) ---
class PlayerInfo(BaseModel):
    player_id: str
    name: str
    is_ai: bool

class CardInfo(BaseModel):
    rank: str
    suit: str
    
class WinnerInfo(BaseModel):
    player_name: str
    amount: int
    hand_rank: str

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
    dealer_seat_index: Optional[int]
    amount_to_call: int
    # ▼▼▼ 変更点: last_messageをlog_messagesに変更 ▼▼▼
    log_messages: Optional[List[str]] = None
    valid_actions: Optional[List[Dict[str, Any]]] = None
    winners: Optional[List[WinnerInfo]] = None

# --- ヘルパー関数 ---

def get_game_or_404(game_id: str, games: Dict[str, GameState]) -> GameState:
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]

# ▼▼▼ 変更点: 引数とレスポンスのフィールド名を変更 ▼▼▼
def format_game_state_for_response(game_id: str, game_state: GameState, messages: Optional[List[str]] = None) -> GameStateResponse:
    valid_actions = None
    current_seat_idx = game_state.current_seat_index
    if current_seat_idx is not None and game_state.status == GameStatus.IN_PROGRESS:
        current_seat = game_state.table.seats[current_seat_idx]
        if current_seat.player and not current_seat.player.is_ai:
             valid_actions = action_service.get_valid_actions(game_state, current_seat_idx)
    
    is_showdown = game_state.status == GameStatus.HAND_COMPLETE
    
    occupied_seats = [s for s in game_state.table.seats if s.is_occupied]
    
    sorted_seats_for_display = []
    if occupied_seats:
        dealer_seat_index = game_state.dealer_seat_index
        start_pos = 0
        if dealer_seat_index is not None:
            try:
                dealer_list_index = next(i for i, s in enumerate(occupied_seats) if s.index == dealer_seat_index)
                start_pos = (dealer_list_index + 1) % len(occupied_seats)
            except (StopIteration, IndexError):
                start_pos = 0 
        
        sorted_seats_for_display = occupied_seats[start_pos:] + occupied_seats[:start_pos]

    return GameStateResponse(
        game_id=game_id,
        status=game_state.status,
        seats=[
            SeatInfo(
                index=s.index,
                is_occupied=s.is_occupied,
                player=PlayerInfo(**s.player.__dict__) if s.player else None,
                stack=s.stack,
                current_bet=s.current_bet,
                bet_total=s.bet_total,
                status=s.status,
                position=s.position,
                hole_cards=[CardInfo(**c.__dict__) for c in s.hole_cards]
                           if s.player and (not s.player.is_ai or (is_showdown and s.status != SeatStatus.FOLDED))
                           else [],
            ) for s in sorted_seats_for_display
        ],
        community_cards=[CardInfo(**c.__dict__) for c in game_state.table.community_cards],
        pot=game_state.table.pot,
        current_round=game_state.current_round,
        current_seat_index=game_state.current_seat_index,
        dealer_seat_index=game_state.dealer_seat_index,
        amount_to_call=game_state.amount_to_call,
        # ▼▼▼ 変更点: log_messagesに設定 ▼▼▼
        log_messages=messages,
        valid_actions=valid_actions,
        winners=[WinnerInfo(**w) for w in game_state.winners] if game_state.winners else None,
    )

# ▼▼▼ 変更点: 文字列の代わりにリストを返すように変更 ▼▼▼
def _advance_game_until_human_action(game_state: GameState, games: Dict[str, GameState]) -> List[str]:
    messages = []
    max_turns = len(game_state.table.seats) * 3 
    turn_count = 0

    while game_state.status == GameStatus.IN_PROGRESS and turn_count < max_turns:
        current_seat = game_state.table.seats[game_state.current_seat_index]
        
        if current_seat.player and not current_seat.player.is_ai and current_seat.status == SeatStatus.ACTIVE:
            return messages

        if current_seat.status == SeatStatus.ACTIVE:
            action = ai_agent_service.decide_action(game_state)
            messages.append(f"{current_seat.player.name} chose {action.action_type.name} {action.amount or ''}")
            action_service.process_action(game_state, action)

            if round_manager.is_betting_round_over(game_state):
                messages.extend(_progress_to_next_stage(game_state))
                continue

        game_state.current_seat_index = round_manager.position_service.get_next_active_player_index(
            game_state, game_state.current_seat_index
        )
        turn_count += 1
        
    return messages

# ▼▼▼ 変更点: 文字列の代わりにリストを返すように変更 ▼▼▼
def _progress_to_next_stage(game_state: GameState) -> List[str]:
    messages = []
    if hand_manager._is_hand_over(game_state):
        hand_manager._conclude_hand(game_state)
        return ["Hand concluded"]

    game_state.table.collect_bets()
    
    current_round_index = list(Round).index(game_state.current_round)
    if current_round_index < list(Round).index(Round.RIVER):
        next_round = list(Round)[current_round_index + 1]
        game_state.current_round = next_round
        
        hand_manager.proceed_to_next_round(game_state)
        round_manager.prepare_for_new_round(game_state)
        messages.append(f"Proceeding to {next_round.name}")
    else:
        hand_manager._conclude_hand(game_state)
        messages.append("Showdown!")

    return messages
