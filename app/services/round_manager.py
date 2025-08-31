# holdem_app/app/services/round_manager.py
from app.models.game_state import GameState
from app.models.enum import SeatStatus, Round
from app.services import position_service, action_service
from typing import Callable, Any

def prepare_for_new_round(game_state: GameState):
    """
    新しいベッティングラウンド（フロップ、ターン、リバー）の準備をします。
    - プレイヤーのアクション済みフラグ(`acted`)をリセットします。
    - ベット関連の状態（コール額など）をリセットします。
    - ラウンドの最初にアクションするプレイヤーを設定します。
    """
    for seat in game_state.table.seats:
        if seat.status not in [SeatStatus.OUT, SeatStatus.FOLDED]:
            seat.acted = False
    
    game_state.amount_to_call = 0
    game_state.last_raiser_seat_index = None
    
    first_to_act_index = position_service.get_first_to_act_index(game_state)
    if first_to_act_index is not None:
        game_state.current_seat_index = first_to_act_index


def run_betting_round(game_state: GameState, get_player_action: Callable[[GameState], Any]):
    active_players = [s for s in game_state.table.seats if s.status == SeatStatus.ACTIVE]
    if len(active_players) <= 1 and game_state.current_round != Round.PREFLOP:
        return

    for seat in position_service.get_occupied_seats(game_state):
        if seat.status != SeatStatus.OUT:
            seat.acted = False
    
    if game_state.current_round == Round.PREFLOP:
        bb_seat = position_service.get_seat_by_position(game_state, "BB")
        if bb_seat:
            game_state.last_raiser_seat_index = bb_seat.index
        game_state.amount_to_call = game_state.big_blind
    else:
        # 新しい関数をポストフロップでも使えるように、共通の準備処理を呼び出す
        prepare_for_new_round(game_state)


    first_to_act_index = position_service.get_first_to_act_index(game_state)
    if first_to_act_index is None: return
    game_state.current_seat_index = first_to_act_index
    
    while True:
        current_player_seat = game_state.table.seats[game_state.current_seat_index]

        if current_player_seat.status == SeatStatus.ACTIVE:
            action = get_player_action(game_state)
            action_service.process_action(game_state, action)

        if is_betting_round_over(game_state):
            break

        game_state.current_seat_index = position_service.get_next_active_player_index(
            game_state, game_state.current_seat_index
        )
    
    game_state.table.collect_bets()

def is_betting_round_over(game_state: GameState) -> bool:
    """ベッティングラウンドが終了したかどうかを判定する"""
    active_seats = [s for s in game_state.table.seats if s.status == SeatStatus.ACTIVE]
    
    # 最優先事項: アクション可能なプレイヤーが1人以下なら、即座にラウンド終了
    if len(active_seats) <= 1:
        return True

    # 全員がアクション済みかチェック
    all_acted = all(s.acted for s in active_seats)
    if not all_acted:
        return False

    # アクティブな（オールインでない）プレイヤーのベット額が全て同じか
    bets_to_check = [s.current_bet for s in active_seats]
    if len(set(bets_to_check)) == 1:
        return True
        
    return False
