# holdem_app/app/services/round_manager.py
from typing import List, Optional
from ..models.game_state import GameState
from ..models.enum import Position, Round, SeatStatus

def _get_players_in_hand_indices(gs: GameState) -> List[int]:
    """現在ハンドに参加している(フォールド/アウトしていない)プレイヤーのインデックスリストを返す"""
    return [
        s.index for s in gs.table.seats 
        if s.is_occupied and s.status not in [SeatStatus.FOLDED, SeatStatus.OUT]
    ]

def _find_next_active_player(gs: GameState, start_index: int) -> Optional[int]:
    """指定したインデックスから時計回りに、次のアクション可能なプレイヤーを探す"""
    players_in_hand = _get_players_in_hand_indices(gs)
    if not players_in_hand:
        return None

    current_index = (start_index + 1) % len(gs.table.seats)
    for _ in range(len(gs.table.seats)):
        seat = gs.table.seats[current_index]
        if seat.index in players_in_hand and seat.status == SeatStatus.ACTIVE:
            return current_index
        current_index = (current_index + 1) % len(gs.table.seats)
    return None

def set_first_action_player(gs: GameState) -> GameState:
    """各ラウンドの最初にアクションするプレイヤーを決定する"""
    if gs.current_round == Round.PREFLOP:
        # プリフロップはBBの左隣(LJ or UTG)
        bb_index = [s.index for s in gs.table.seats if s.position == Position.BB][0]
        first_to_act = _find_next_active_player(gs, bb_index)
    else:
        # ポストフロップはSBに近いアクティブプレイヤー
        dealer_index = gs.dealer_seat_index
        first_to_act = _find_next_active_player(gs, dealer_index)

    gs.current_seat_index = first_to_act
    return gs

def is_betting_round_over(gs: GameState) -> bool:
    """ベッティングラウンドが終了したか判定する"""
    players_in_hand = [gs.table.seats[i] for i in _get_players_in_hand_indices(gs)]
    
    if not players_in_hand:
        return True

    # 1人しか残っていない場合は終了
    if len(players_in_hand) <= 1:
        return True
    
    # まだアクションしていないプレイヤーがいるか
    unacted_players = [p for p in players_in_hand if not p.acted and p.status == SeatStatus.ACTIVE]
    if unacted_players:
        return False
        
    # ベット額が全員同じか (All-inプレイヤーは除く)
    active_bets = {p.current_bet for p in players_in_hand if p.status == SeatStatus.ACTIVE}
    if len(active_bets) > 1:
        return False

    return True

def advance_to_next_player_or_round(gs: GameState) -> GameState:
    """次のプレイヤーにアクションを移すか、次のラウンドに進める"""
    if is_betting_round_over(gs):
        # ポットを回収し、次のラウンドへ
        gs.table.collect_bets()
        
        round_order = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]
        current_round_index = round_order.index(gs.current_round)
        
        if current_round_index + 1 >= len(round_order):
             gs.current_round = Round.SHOWDOWN
        else:
            gs.current_round = round_order[current_round_index + 1]

        # ラウンド開始時のリセット処理
        for seat in gs.table.seats:
            seat.acted = False
        gs.amount_to_call = 0
        gs.min_raise_amount = gs.big_blind
        gs.last_raiser_seat_index = None
        gs = set_first_action_player(gs)
        
    else:
        # 次のアクションプレイヤーへ
        next_player_index = _find_next_active_player(gs, gs.current_seat_index)
        gs.current_seat_index = next_player_index

    return gs