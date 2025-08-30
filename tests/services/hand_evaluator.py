# tests/services/test_hand_evaluator.py
import pytest
from app.models.deck import Card
from app.models.seat import Seat
from app.models.player import Player
from app.services.hand_evaluator import HandEvaluator

@pytest.fixture
def evaluator():
    return HandEvaluator()

def test_evaluate_royal_flush(evaluator):
    """ロイヤルフラッシュの判定テスト"""
    hole_cards = [Card('A', 's'), Card('K', 's')]
    community_cards = [Card('Q', 's'), Card('J', 's'), Card('T', 's'), Card('3', 'h'), Card('2', 'd')]
    score = evaluator.evaluate_hand(hole_cards, community_cards)
    rank_string = evaluator.get_rank_string(score)
    assert rank_string == "Straight Flush" # treysではロイヤルもストレートフラッシュとして扱われる
    assert score < 20 # ストレートフラッシュは非常に強い役（スコアが低い）

def test_evaluate_full_house(evaluator):
    """フルハウスの判定テスト"""
    hole_cards = [Card('A', 's'), Card('A', 'c')]
    community_cards = [Card('K', 's'), Card('K', 'h'), Card('K', 'd'), Card('3', 'h'), Card('2', 'd')]
    score = evaluator.evaluate_hand(hole_cards, community_cards)
    rank_string = evaluator.get_rank_string(score)
    assert rank_string == "Full House"

def test_determine_winners_single_winner(evaluator):
    """勝者が1人の場合の判定テスト"""
    community_cards = [Card('A', 's'), Card('K', 'd'), Card('5', 'c'), Card('6', 'h'), Card('7', 's')]
    
    seat1 = Seat(0, Player("p1"))
    seat1.hole_cards = [Card('A', 'c'), Card('K', 'h')] # Two Pair (A, K)

    seat2 = Seat(1, Player("p2"))
    seat2.hole_cards = [Card('5', 's'), Card('6', 'd')] # Two Pair (6, 5)

    seats_in_hand = [seat1, seat2]
    winners_by_pot = evaluator.determine_winners(seats_in_hand, community_cards)

    assert len(winners_by_pot) == 1
    assert len(winners_by_pot[0]) == 1
    assert winners_by_pot[0][0] == seat1

def test_determine_winners_chop(evaluator):
    """引き分け（チョップ）の場合の判定テスト"""
    community_cards = [Card('A', 's'), Card('K', 'd'), Card('Q', 'c'), Card('J', 'h'), Card('2', 's')]

    seat1 = Seat(0, Player("p1"))
    seat1.hole_cards = [Card('T', 'c'), Card('3', 'h')] # Straight (A high)

    seat2 = Seat(1, Player("p2"))
    seat2.hole_cards = [Card('T', 's'), Card('4', 'd')] # Straight (A high)

    seat3 = Seat(2, Player("p3"))
    seat3.hole_cards = [Card('A', 'c'), Card('2', 'h')] # One Pair (A)

    seats_in_hand = [seat1, seat2, seat3]
    winners_by_pot = evaluator.determine_winners(seats_in_hand, community_cards)

    assert len(winners_by_pot) == 1
    assert len(winners_by_pot[0]) == 2
    assert seat1 in winners_by_pot[0]
    assert seat2 in winners_by_pot[0]
    assert seat3 not in winners_by_pot[0]