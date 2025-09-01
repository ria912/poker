# tests/services/test_evaluation_service.py
from app.services import evaluation_service
from app.models.deck import Card
from app.models.enum import SeatStatus

def test_find_winners_simple_case(game_state):
    # セットアップ
    s0, s1, s2 = game_state.table.seats[0:3]
    game_state.table.community_cards = [Card('A', 's'), Card('K', 's'), Card('Q', 's'), Card('J', 's'), Card('T', 'c')]
    s0.hole_cards = [Card('2', 'c'), Card('3', 'c')] # No pair
    s1.hole_cards = [Card('A', 'h'), Card('2', 'h')] # Pair of Aces
    s2.hole_cards = [Card('T', 's'), Card('9', 's')] # Royal Flush

    s0.bet_total = 100
    s1.bet_total = 100
    s2.bet_total = 100
    game_state.table.pot = 300
    
    winners = evaluation_service.find_winners(game_state)
    
    assert len(winners) == 1
    assert winners[0][0] == s2 # s2 has Royal Flush
    assert winners[0][1] == 300

def test_find_winners_split_pot(game_state):
    # セットアップ
    s0, s1, s2 = game_state.table.seats[0:3]
    game_state.table.community_cards = [Card('A', 's'), Card('K', 'd'), Card('5', 'c'), Card('8', 'h'), Card('T', 'c')]
    s0.hole_cards = [Card('A', 'c'), Card('J', 'c')] # Pair of Aces, J kicker
    s1.hole_cards = [Card('A', 'h'), Card('J', 'h')] # Pair of Aces, J kicker
    s2.hole_cards = [Card('K', 's'), Card('Q', 's')] # Pair of Kings
    
    s0.bet_total = 200
    s1.bet_total = 200
    s2.bet_total = 200
    game_state.table.pot = 600

    winners = evaluation_service.find_winners(game_state)
    
    assert len(winners) == 2
    winner_seats = {w[0] for w in winners}
    assert s0 in winner_seats
    assert s1 in winner_seats
    assert winners[0][1] == 300
    assert winners[1][1] == 300
