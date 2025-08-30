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
    
    # CHECK / CALL / ALL-IN (Call)
    if amount_to_call == 0:
        actions[ActionType.CHECK.value] = True
    else:
        # コール額に足りなくても、全スタックを賭けることでコール（オールイン）できる
        actions[ActionType.CALL.value] = min(amount_to_call, seat.stack)

    # BET / RAISE / ALL-IN (Raise)
    # 相手のベット額よりも多くのチップを持っている場合のみ、ベット/レイズが可能
    if seat.stack > amount_to_call:
        action_name = ActionType.RAISE.value if amount_to_call > 0 else ActionType.BET.value
        
        # ミニマムレイズ額の計算
        min_raise_total = game_state.amount_to_call + game_state.min_raise_amount
        # ただし、少なくともBB額は上乗せする必要がある
        min_raise_total = max(min_raise_total, game_state.amount_to_call + game_state.big_blind)

        actions[action_name] = {
            "min": min(seat.stack + seat.current_bet, min_raise_total),
            "max": seat.stack + seat.current_bet # ベット後の合計額
        }

    return actions

# apply_action関数は変更なしでOKです。
# (元のコードをここにコピーしてください)
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
        
        actual_bet = seat.bet(additional_bet)
        
        raise_diff = (seat.current_bet - game_state.amount_to_call)
        
        game_state.min_raise_amount = raise_diff
        game_state.amount_to_call = seat.current_bet
        game_state.last_raiser_seat_index = seat.index

    seat.acted = True
    
    if seat.stack == 0:
        seat.state = SeatState.ALL_IN