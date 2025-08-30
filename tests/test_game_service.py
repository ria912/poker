from app.services import game_service
from app.models.deck import Card
from app.models.enum import GameState as GameStatusEnum, SeatState

def test_start_hand(game_state_with_3_players):
    """ハンドが正しく開始されるかテスト"""
    gs = game_state_with_3_players
    game_service.start_hand(gs)
    
    assert gs.status == GameStatusEnum.IN_PROGRESS
    
    sb_seat = gs.table.seats[1]
    bb_seat = gs.table.seats[3]
    
    assert sb_seat.current_bet == 10
    assert bb_seat.current_bet == 20
    assert gs.amount_to_call == 20
    assert len(gs.table.seats[0].hole_cards) == 2
    assert gs.active_seat_index == 0

def test_determine_winner_and_distribute_pot(game_state_with_3_players):
    """勝者判定とポット分配のテスト"""
    gs = game_state_with_3_players
    game_service.start_hand(gs)
    
    alice = gs.table.seats[0]
    bob = gs.table.seats[1]
    
    alice.hole_cards = [Card('A', 's'), Card('K', 's')]
    bob.hole_cards = [Card('7', 'd'), Card('7', 'h')]
    gs.table.community_cards = [
        Card('Q', 's'), Card('J', 's'), Card('T', 's'),
        Card('7', 'c'), Card('2', 'd')
    ]
    gs.table.seats[3].state = SeatState.FOLDED
    gs.table.pot = 500
    
    initial_alice_stack = alice.stack
    initial_bob_stack = bob.stack
    
    game_service.determine_winner_and_distribute_pot(gs)
    
    assert alice.stack == initial_alice_stack + 500
    assert bob.stack == initial_bob_stack