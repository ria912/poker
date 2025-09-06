# holdem_app/app/services/hand_manager.py
from app.models.game_state import GameState
from app.models.enum import Round, SeatStatus, ActionType, GameStatus
from app.models.action import Action
from app.services import position_service, action_service, evaluation_service, round_manager
from typing import Callable, Any

def start_new_hand(game_state: GameState):
    """新しいハンドを開始する準備を行う"""
    game_state.clear_for_new_hand()

    for seat in game_state.table.seats:
        if seat.is_occupied:
            seat.starting_stack = seat.stack
    
    active_players = position_service.get_occupied_seats(game_state)
    if len(active_players) < 2:
        game_state.status = GameStatus.WAITING
        return

    game_state.status = GameStatus.IN_PROGRESS
    
    # 1. ディーラーボタンを回す
    position_service.rotate_dealer_button(game_state)
    
    # 2. ポジションを割り当てる
    position_service.assign_positions(game_state)

    # 3. ブラインドを支払う
    _post_blinds(game_state)

    # 4. カードを配る
    _deal_hole_cards(game_state)
    
    # <<< 修正点: プリフロップで最初にアクションするプレイヤーを設定 >>>
    game_state.current_seat_index = position_service.get_first_to_act_index(game_state)

def _post_blinds(game_state: GameState):
    """SBとBBを強制的に支払わせる"""
    sb_seat = position_service.get_seat_by_position(game_state, "SB")
    bb_seat = position_service.get_seat_by_position(game_state, "BB")

    if sb_seat and sb_seat.player:
        sb_amount = min(game_state.small_blind, sb_seat.stack)
        action = Action(sb_seat.player.player_id, ActionType.POST_SB, sb_amount)
        action_service.process_action(game_state, action)

    if bb_seat and bb_seat.player:
        bb_amount = min(game_state.big_blind, bb_seat.stack)
        action = Action(bb_seat.player.player_id, ActionType.POST_BB, bb_amount)
        action_service.process_action(game_state, action)

def _deal_hole_cards(game_state: GameState):
    """各プレイヤーにホールカードを2枚ずつ配る"""
    seats_to_deal = position_service.get_occupied_seats(game_state)
    for seat in seats_to_deal:
        cards = game_state.table.deck.draw(2)
        seat.receive_cards(cards)

def proceed_to_next_round(game_state: GameState, verbose: bool = True):
    """次のラウンドのカードを配る"""
    if _is_hand_over(game_state):
        _conclude_hand(game_state, verbose)
        return

    if game_state.current_round == Round.FLOP:
        game_state.table.community_cards.extend(game_state.table.deck.draw(3))
    elif game_state.current_round == Round.TURN:
        game_state.table.community_cards.extend(game_state.table.deck.draw(1))
    elif game_state.current_round == Round.RIVER:
        game_state.table.community_cards.extend(game_state.table.deck.draw(1))

def _is_hand_over(game_state: GameState) -> bool:
    """ハンドが終了したかどうかを判定する"""
    # FOLDもOUTもしていないプレイヤー（ALL_IN状態のプレイヤーを含む）をリストアップ
    eligible_players = [s for s in game_state.table.seats if s.status not in [SeatStatus.FOLDED, SeatStatus.OUT]]
    
    # そのようなプレイヤーが1人以下であれば、他のプレイヤーは全員フォールドしているため、
    # ハンドはショウダウンを待たずに終了する。
    if len(eligible_players) <= 1:
        return True
        
    return False

def _conclude_hand(game_state: GameState, verbose: bool = True):
    """ハンドを終了し、勝者にポットを分配する"""
    winners_with_amounts = evaluation_service.find_winners(game_state, verbose)
    for seat, amount in winners_with_amounts:
        seat.stack += amount
    game_state.status = GameStatus.HAND_COMPLETE
