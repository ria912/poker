# holdem_app/app/services/action_service.py
from typing import List, Dict, Any
from app.models.game_state import GameState
from app.models.action import Action
from app.models.enum import ActionType, SeatStatus

def get_valid_actions(game_state: GameState, seat_index: int) -> List[Dict[str, Any]]:
    """
    指定された座席のプレイヤーが現在取りうる有効なアクションをリストで返す
    """
    valid_actions = []
    seat = game_state.table.seats[seat_index]
    
    can_check = seat.current_bet == game_state.amount_to_call

    if can_check:
        valid_actions.append({"type": ActionType.CHECK})
        min_bet = game_state.big_blind
        max_bet = seat.stack
        if min_bet <= max_bet:
            valid_actions.append({"type": ActionType.BET, "min": min_bet, "max": max_bet})
    else:
        valid_actions.append({"type": ActionType.FOLD})
        
        call_amount = game_state.amount_to_call - seat.current_bet
        if call_amount > 0 and seat.stack > 0:
            amount = min(call_amount, seat.stack)
            valid_actions.append({"type": ActionType.CALL, "amount": amount})

        min_raise = game_state.min_raise_amount
        # レイズするには、コール額をカバーしてさらに上乗せできるスタックが必要
        if seat.stack > call_amount:
             # 自分の全スタック + 現在のベット額が、ミニマムレイズ額以上であること
            if (seat.stack + seat.current_bet) >= min_raise:
                valid_actions.append({"type": ActionType.RAISE, "min": min_raise, "max": seat.stack + seat.current_bet})

    return valid_actions


def process_action(game_state: GameState, action: Action):
    """プレイヤーのアクションを処理し、ゲーム状態を更新する"""
    try:
        seat = next(s for s in game_state.table.seats if s.player and s.player.player_id == action.player_id)
    except StopIteration:
        return

    seat.acted = True

    if action.action_type == ActionType.FOLD:
        seat.status = SeatStatus.FOLDED

    elif action.action_type == ActionType.CALL:
        call_amount = game_state.amount_to_call - seat.current_bet
        actual_call = min(call_amount, seat.stack)
        seat.bet(actual_call)

    elif action.action_type == ActionType.CHECK:
        pass

    elif action.action_type in [ActionType.BET, ActionType.POST_SB, ActionType.POST_BB]:
        seat.bet(action.amount)
        game_state.amount_to_call = seat.current_bet
        game_state.min_raise_amount = seat.current_bet * 2
        game_state.last_raiser_seat_index = seat.index
        if action.action_type == ActionType.BET:
            _reset_acted_flags_except(game_state, seat.index)

    elif action.action_type == ActionType.RAISE:
        previous_amount_to_call = game_state.amount_to_call
        total_bet_amount = action.amount
        bet_amount = total_bet_amount - seat.current_bet
        seat.bet(bet_amount)

        game_state.amount_to_call = total_bet_amount
        raise_delta = total_bet_amount - previous_amount_to_call
        game_state.min_raise_amount = total_bet_amount + raise_delta
        game_state.last_raiser_seat_index = seat.index
        _reset_acted_flags_except(game_state, seat.index)

    if seat.stack <= 0:
        seat.stack = 0
        seat.status = SeatStatus.ALL_IN

def _reset_acted_flags_except(game_state: GameState, current_player_index: int):
    """レイズがあった場合に、他のプレイヤーが再度アクションできるようにactedフラグをリセット"""
    for seat in game_state.table.seats:
        if seat.status == SeatStatus.ACTIVE and seat.index != current_player_index:
            seat.acted = False

