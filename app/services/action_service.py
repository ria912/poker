from typing import Dict, Any, List
from ..models.enum import ActionType, SeatState
from ..models.game_state import GameState

def get_legal_actions(game_state: GameState) -> Dict[str, Any]:
    """現在のアクティブプレイヤーが取れる合法的なアクションを返す"""
    if game_state.active_seat_index is None:
        return {}

    seat = game_state.table.seats[game_state.active_seat_index]
    if not seat.is_active:
        return {}
    
    actions: Dict[str, Any] = {
        ActionType.FOLD.value: True
    }
    
    amount_to_call = game_state.amount_to_call - seat.current_bet
    can_afford_call = seat.stack >= amount_to_call

    # CHECK / CALL
    if amount_to_call == 0:
        actions[ActionType.CHECK.value] = True
    elif can_afford_call:
        actions[ActionType.CALL.value] = amount_to_call
    
    # BET / RAISE
    # ミニマムレイズ額 or BB額からベット/レイズ可能
    min_bet = max(game_state.min_raise_amount, game_state.big_blind)
    
    # 相手のレイズにさらにレイズする場合のミニマムレイズ額
    if game_state.amount_to_call > 0:
        min_bet = game_state.amount_to_call + game_state.min_raise_amount

    if seat.stack > amount_to_call:
        action_name = ActionType.RAISE.value if amount_to_call > 0 else ActionType.BET.value
        actions[action_name] = {
            "min": min(seat.stack, min_bet),
            "max": seat.stack + seat.current_bet # ベット後の合計額ではなく、追加する額
        }

    return actions


def apply_action(game_state: GameState, action_type: str, amount: int = 0):
    """プレイヤーのアクションをゲーム状態に適用する"""
    if game_state.active_seat_index is None:
        raise ValueError("No active player")

    seat = game_state.table.seats[game_state.active_seat_index]
    action = ActionType(action_type)

    if action == ActionType.FOLD:
        seat.state = SeatState.FOLDED
    
    elif action == ActionType.CHECK:
        pass # 何もしない

    elif action == ActionType.CALL:
        call_amount = game_state.amount_to_call - seat.current_bet
        seat.bet(call_amount)

    elif action == ActionType.BET:
        bet_amount = seat.bet(amount)
        game_state.amount_to_call = bet_amount
        game_state.min_raise_amount = bet_amount
        game_state.last_raiser_seat_index = seat.index

    elif action == ActionType.RAISE:
        raise_total_amount = amount
        additional_bet = raise_total_amount - seat.current_bet
        
        # 実際にベットした額を反映
        actual_bet = seat.bet(additional_bet)
        
        # raise額の差分を計算
        raise_diff = (seat.current_bet - game_state.amount_to_call)
        
        game_state.min_raise_amount = raise_diff
        game_state.amount_to_call = seat.current_bet
        game_state.last_raiser_seat_index = seat.index

    # アクション完了
    seat.acted = True
    
    # オールイン判定
    if seat.stack == 0:
        seat.state = SeatState.ALL_IN