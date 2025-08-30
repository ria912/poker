# holdem_app/app/services/position_service.py
from typing import List
from app.models.game_state import GameState
from app.models.enum import Position, Round, SeatStatus
from app.models.seat import Seat

def get_occupied_seats(game_state: GameState) -> List[Seat]:
    """着席しているプレイヤーの座席リストを返す"""
    return [s for s in game_state.table.seats if s.is_occupied]

def get_active_seats_in_hand(game_state: GameState) -> List[Seat]:
    """ハンドに参加していて、まだアクションの権利がある座席のリストを返す"""
    return [s for s in game_state.table.seats if s.status in [SeatStatus.ACTIVE, SeatStatus.ALL_IN]]

def rotate_dealer_button(game_state: GameState):
    """ディーラーボタンを次のアクティブなプレイヤーに移動させる"""
    seats = game_state.table.seats
    occupied_seats = get_occupied_seats(game_state)
    if not occupied_seats:
        game_state.dealer_seat_index = None
        return

    if game_state.dealer_seat_index is None:
        game_state.dealer_seat_index = occupied_seats[0].index
    else:
        start_index = (game_state.dealer_seat_index + 1) % len(seats)
        for i in range(len(seats)):
            next_index = (start_index + i) % len(seats)
            if seats[next_index].is_occupied:
                game_state.dealer_seat_index = next_index
                break
    
    print(f"Dealer button is at seat {game_state.dealer_seat_index}")

def get_next_active_player_index(game_state: GameState, start_index: int) -> int:
    """指定したインデックスの次に行動可能なプレイヤーのインデックスを返す"""
    seats = game_state.table.seats
    for i in range(1, len(seats) + 1):
        next_index = (start_index + i) % len(seats)
        if seats[next_index].status == SeatStatus.ACTIVE:
            return next_index
    return start_index

def assign_positions(game_state: GameState):
    """各プレイヤーにポジション（SB, BBなど）を割り当てる"""
    dealer_idx = game_state.dealer_seat_index
    if dealer_idx is None:
        return

    occupied_seats = get_occupied_seats(game_state)
    num_players = len(occupied_seats)
    
    if num_players < 2:
        return
        
    if num_players == 2:
        position_order = [Position.BTN, Position.BB]
    else:
        positions_for_6max = [Position.LJ, Position.HJ, Position.CO, Position.BTN, Position.SB, Position.BB]
        position_order = positions_for_6max[-num_players:]

    try:
        dealer_seat = next(s for s in occupied_seats if s.index == dealer_idx)
        dealer_pos_in_list = occupied_seats.index(dealer_seat)
    except StopIteration:
        return 

    btn_index_in_order = position_order.index(Position.BTN)

    for i, seat in enumerate(occupied_seats):
        # ディーラーからの相対的な距離を計算 (ディーラー自身は0, 次の人は1, ...)
        distance_from_dealer = (i - dealer_pos_in_list + num_players) % num_players
        # BTNのインデックスに距離を足して、正しいポジションを決定
        pos_index = (btn_index_in_order + distance_from_dealer) % len(position_order)
        seat.position = position_order[pos_index]
        print(f"Seat {seat.index} ({seat.player.name}) is {seat.position.name}")

def get_seat_by_position(game_state: GameState, position: Position) -> Seat | None:
    """指定したポジションの座席を返す"""
    for seat in get_occupied_seats(game_state):
        if seat.position == position:
            return seat
    return None

def get_first_to_act_index(game_state: GameState) -> int:
    """そのラウンドで最初にアクションするプレイヤーのインデックスを返す"""
    dealer_idx = game_state.dealer_seat_index
    
    if game_state.current_round == Round.PREFLOP:
        num_players = len(get_occupied_seats(game_state))
        if num_players == 2:
            return dealer_idx
        
        bb_seat = get_seat_by_position(game_state, Position.BB)
        if bb_seat:
             return get_next_active_player_index(game_state, bb_seat.index)
        return get_next_active_player_index(game_state, dealer_idx)
    else:
        return get_next_active_player_index(game_state, dealer_idx)

