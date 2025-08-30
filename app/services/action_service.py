# holdem_app/app/services/action_service.py
from typing import List
from app.models.game_state import GameState
from app.models.action import Action
from app.models.enum import ActionType, SeatStatus

def process_action(game_state: GameState, action: Action):
    """
    プレイヤーのアクションを処理し、ゲーム状態を更新する。
    例: ベット額をスタックから引く、ポットに加算する、プレイヤーの状態を変更するなど。
    """
    # player_idからseat_indexを見つけるロジックが必要
    seat = next((s for s in game_state.table.seats if s.player and s.player.player_id == action.player_id), None)
    if not seat:
        raise ValueError("Player not found for the action.")

    # アクションの妥当性チェック
    valid_actions = get_valid_actions(game_state, seat.index)
    # ここでactionがvalid_actionsに含まれるかなどをチェックする

    # アクションに応じた状態更新
    if action.action_type == ActionType.FOLD:
        seat.status = SeatStatus.FOLDED
    elif action.action_type == ActionType.CALL:
        # コール額を計算し、ベット処理
        amount = game_state.amount_to_call - seat.current_bet
        seat.bet(amount)
    # ... 他のアクションタイプの処理 ...

    game_state.add_action(action.player_id, action.action_type, action.amount)
    print(f"Action processed: {action}")


def get_valid_actions(game_state: GameState, seat_index: int) -> List[ActionType]:
    """
    指定されたプレイヤーが現在取りうる有効なアクションのリストを返す。
    """
    # 状況（コール額、前のプレイヤーのアクションなど）に応じて
    # FOLD, CHECK, CALL, BET, RAISEなどをリストにして返す
    valid_actions = [ActionType.FOLD]

    seat = game_state.table.seats[seat_index]
    can_check = game_state.amount_to_call == seat.current_bet
    
    if can_check:
        valid_actions.append(ActionType.CHECK)
    else:
        valid_actions.append(ActionType.CALL)
    
    # BETやRAISEが可能かどうかの判定もここで行う
    valid_actions.append(ActionType.RAISE) # 仮
    
    return valid_actions
