from typing import Optional
from ..models.game_state import GameState
from ..models.enum import Round, SeatState

def find_next_player_index(game_state: GameState, start_index: Optional[int] = None) -> Optional[int]:
    """指定したインデックスから次のアクティブなプレイヤーを探す"""
    seats = game_state.table.seats
    num_seats = len(seats)
    
    if start_index is None:
        start_index = game_state.dealer_btn_index

    for i in range(1, num_seats + 1):
        index = (start_index + i) % num_seats
        if seats[index].is_active:
            return index
    return None

def find_next_action_player_index(game_state: GameState) -> Optional[int]:
    """次のアクションプレイヤーのインデックスを見つける"""
    seats = game_state.table.seats
    num_seats = len(seats)
    start_index = game_state.active_seat_index
    
    if start_index is None: return None

    for i in range(1, num_seats + 1):
        index = (start_index + i) % num_seats
        seat = seats[index]
        if seat.is_active and not seat.acted:
            return index
            
    return None

def is_betting_round_over(game_state: GameState) -> bool:
    """現在のベッティングラウンドが終了したかどうかを判定する"""
    active_players = [s for s in game_state.table.seats if s.state == SeatState.ACTIVE]
    
    # アクティブプレイヤーが1人以下なら終了
    if len(active_players) <= 1:
        return True
    
    # 全員がアクション済みかチェック
    all_acted = all(seat.acted for seat in active_players)
    if not all_acted:
        return False
        
    # 全員が同額をベットしているかチェック
    first_bet = active_players[0].current_bet
    all_same_bet = all(seat.current_bet == first_bet for seat in active_players)
    
    # BBがチェックで回った場合も考慮
    is_bb_option = (
        game_state.current_round == Round.PREFLOP and
        game_state.table.seats[game_state.last_raiser_seat_index].position == "BB" and
        game_state.amount_to_call == game_state.big_blind
    )

    return all_acted and all_same_bet and not is_bb_option


def start_next_street(game_state: GameState):
    """次のストリート（フロップ、ターン、リバー）へ移行する"""
    game_state.table.collect_bets()
    
    # プレイヤーのアクション状態をリセット
    for seat in game_state.table.seats:
        if seat.is_active:
            seat.acted = False

    game_state.amount_to_call = 0
    game_state.min_raise_amount = game_state.big_blind
    game_state.last_raiser_seat_index = None

    # SBからアクション開始
    game_state.active_seat_index = find_next_player_index(game_state, game_state.dealer_btn_index)

    if game_state.current_round == Round.PREFLOP:
        game_state.current_round = Round.FLOP
        game_state.table.community_cards.extend(game_state.table.deck.draw(3))
    elif game_state.current_round == Round.FLOP:
        game_state.current_round = Round.TURN
        game_state.table.community_cards.extend(game_state.table.deck.draw(1))
    elif game_state.current_round == Round.TURN:
        game_state.current_round = Round.RIVER
        game_state.table.community_cards.extend(game_state.table.deck.draw(1))
    elif game_state.current_round == Round.RIVER:
        game_state.current_round = Round.SHOWDOWN