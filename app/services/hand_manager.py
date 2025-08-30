# holdem_app/app/services/hand_manager.py
from typing import List
from ..models.game_state import GameState
from ..models.enum import Position, SeatStatus
from . import evaluation_service

def _find_player_by_position(gs: GameState, position: Position) -> int:
    """指定されたポジションのプレイヤーのシートインデックスを返す"""
    for seat in gs.table.seats:
        if seat.position == position:
            return seat.index
    raise ValueError(f"Position {position.value} not found.")

def collect_blinds(gs: GameState) -> GameState:
    """SBとBBからブラインドを徴収する"""
    sb_index = _find_player_by_position(gs, Position.SB)
    bb_index = _find_player_by_position(gs, Position.BB)
    
    sb_seat = gs.table.seats[sb_index]
    bb_seat = gs.table.seats[bb_index]

    # SBベット
    sb_amount = min(gs.small_blind, sb_seat.stack)
    sb_seat.bet(sb_amount)
    if sb_seat.stack == 0:
        sb_seat.status = SeatStatus.ALL_IN

    # BBベット
    bb_amount = min(gs.big_blind, bb_seat.stack)
    bb_seat.bet(bb_amount)
    if bb_seat.stack == 0:
        bb_seat.status = SeatStatus.ALL_IN

    # プリフロップのコール額と最低レイズ額を設定
    gs.amount_to_call = gs.big_blind
    gs.min_raise_amount = gs.big_blind * 2
    gs.last_raiser_seat_index = bb_index
    
    return gs

def deal_hole_cards(gs: GameState) -> GameState:
    """各アクティブプレイヤーにホールカードを2枚ずつ配る"""
    active_indices = [s.index for s in gs.table.seats if s.position is not None]
    
    # SBから時計回りに配る
    sb_player_list_index = active_indices.index(_find_player_by_position(gs, Position.SB))
    
    sorted_player_indices = active_indices[sb_player_list_index:] + active_indices[:sb_player_list_index]

    for _ in range(2): # 2周配る
        for player_index in sorted_player_indices:
            card = gs.table.deck.draw(1)[0]
            if not gs.table.seats[player_index].hole_cards:
                 gs.table.seats[player_index].hole_cards = []
            gs.table.seats[player_index].hole_cards.append(card)
            
    return gs

def deal_community_cards(gs: GameState) -> GameState:
    """ラウンドに応じてコミュニティカードを配る"""
    gs.table.deck.draw(1) # バーンカード

    if gs.current_round == "FLOP":
        cards = gs.table.deck.draw(3)
    elif gs.current_round in ["TURN", "RIVER"]:
        cards = gs.table.deck.draw(1)
    else:
        cards = []
        
    gs.table.community_cards.extend(cards)
    return gs

def distribute_pot(gs: GameState) -> GameState:
    """勝者にポットを分配する (サイドポットは未実装)"""
    gs.table.collect_bets() # 最後に残ったベットをポットへ
    winners = evaluation_service.determine_winners(gs)
    
    if not winners:
        # 全員フォールドした場合など
        active_players = [s for s in gs.table.seats if s.status not in ["FOLDED", "OUT"]]
        if len(active_players) == 1:
            winners = [active_players[0].index]

    if winners:
        award = gs.table.pot / len(winners)
        for winner_index in winners:
            gs.table.seats[winner_index].stack += int(award)
    
    gs.table.pot = 0
    return gs
