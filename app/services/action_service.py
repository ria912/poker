# holdem_app/app/services/action_service.py
from ..models.game_state import GameState
from ..models.enum import SeatStatus, ActionType

class ActionError(Exception):
    """アクションが不正な場合に送出される例外"""
    pass

def get_legal_actions(gs: GameState, seat_index: int) -> dict:
    """指定されたプレイヤーが実行可能なアクションを返す"""
    seat = gs.table.seats[seat_index]
    if not seat.is_active or gs.current_seat_index != seat_index:
        return {}

    legal_actions = {
        ActionType.FOLD: True
    }
    
    can_check = gs.amount_to_call == seat.current_bet
    if can_check:
        legal_actions[ActionType.CHECK] = True
    else:
        # コール可能な額
        call_amount = min(gs.amount_to_call - seat.current_bet, seat.stack)
        legal_actions[ActionType.CALL] = call_amount

    # レイズ/ベット可能な額
    # 詳細は後で実装
    min_raise = gs.min_raise_amount
    max_raise = seat.stack + seat.current_bet
    if max_raise > min_raise:
         legal_actions[ActionType.RAISE] = {'min': min_raise, 'max': max_raise}

    return legal_actions


def validate_and_apply_fold(gs: GameState, seat_index: int):
    """フォールドを処理する"""
    if gs.current_seat_index != seat_index:
        raise ActionError("It's not your turn.")
    
    seat = gs.table.seats[seat_index]
    seat.status = SeatStatus.FOLDED
    seat.acted = True
    return gs

def validate_and_apply_call(gs: GameState, seat_index: int):
    """コール/チェックを処理する"""
    if gs.current_seat_index != seat_index:
        raise ActionError("It's not your turn.")
        
    seat = gs.table.seats[seat_index]
    amount_to_call = gs.amount_to_call - seat.current_bet

    if amount_to_call > 0: # Call
        if seat.stack < amount_to_call: # All-in call
            seat.bet(seat.stack)
            seat.status = SeatStatus.ALL_IN
        else:
            seat.bet(amount_to_call)

    # チェックの場合はベット額は変わらない
    seat.acted = True
    return gs

# validate_and_apply_raise などの他のアクション関数も同様に定義
