from app.models.game_state import GameState
from app.models.action import Action
from app.models.enum import ActionType, Round, Position
from app.services import action_service
from app.services.ai.ai_strategy import get_hand_representation, OPENING_RANGES

def decide_action(game_state: GameState) -> Action:
    """
    AIのアクションを決定する。
    プリフロップのオープンシチュエーションではレンジ表に基づきレイズ or フォールド。
    それ以外の状況では、チェック -> コール -> フォールドの順で選択。
    """
    seat_index = game_state.current_seat_index
    seat = game_state.table.seats[seat_index]
    player_id = seat.player.player_id
    
    # --- プリフロップのオープン判断 ---
    is_preflop = game_state.current_round == Round.PREFLOP
    # 自分より前にレイズした人がいないか（コール額がBB額のままか）で判断
    is_open_opportunity = game_state.amount_to_call == game_state.big_blind

    if is_preflop and is_open_opportunity:
        hand_str = get_hand_representation(seat.hole_cards)
        position = seat.position
        
        # レンジ表にポジションが存在し、かつハンドがレンジ内にあるか
        if position in OPENING_RANGES and hand_str in OPENING_RANGES[position]:
            # レンジ内ならレイズ
            # オープンレイズ額をBBの2.5倍とする
            raise_amount = int(game_state.big_blind * 2.5)
            
            # 念のため有効なアクションの中からRAISEを探し、min/max額を考慮
            valid_actions = action_service.get_valid_actions(game_state, seat_index)
            raise_action_info = next((a for a in valid_actions if a['type'] == ActionType.RAISE), None)

            if raise_action_info:
                # レイズ額がmin以上max以下になるように調整
                final_amount = max(raise_action_info['min'], min(raise_amount, raise_action_info['max']))
                return Action(player_id, ActionType.RAISE, amount=final_amount)

    # --- 上記の条件に当てはまらない場合（ポストフロップや、誰かがレイズした後など） ---
    valid_actions = action_service.get_valid_actions(game_state, seat_index)
    valid_action_types = [a['type'] for a in valid_actions]

    # 1. チェックが可能か確認
    if ActionType.CHECK in valid_action_types:
        return Action(player_id, ActionType.CHECK)

    # 2. コールが可能か確認
    if ActionType.CALL in valid_action_types:
        call_action_info = next(a for a in valid_actions if a['type'] == ActionType.CALL)
        return Action(player_id, ActionType.CALL, amount=call_action_info.get('amount'))

    # 3. 上記以外の場合はフォールド
    return Action(player_id, ActionType.FOLD)