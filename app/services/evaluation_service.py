# holdem_app/app/services/evaluation_service.py
from typing import List
from treys import Evaluator, Card as TreysCard

from ..models.deck import Card

evaluator = Evaluator()

def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> int:
    """
    ホールカード2枚とコミュニティカード3〜5枚から、最も強い役のスコアを返す。
    スコアが小さいほど強い役 (例: 1=ロイヤルフラッシュ)。
    """
    if not (3 <= len(community_cards) <= 5):
        raise ValueError("Community cards must be 3, 4, or 5.")

    hand = [card.to_treys_int() for card in hole_cards]
    board = [card.to_treys_int() for card in community_cards]
    
    return evaluator.evaluate(hand, board)

def get_hand_rank_name(score: int) -> str:
    """treysのスコアから役名を返す"""
    return evaluator.class_to_string(evaluator.get_rank_class(score))

def determine_winners(game_state) -> List[int]:
    """
    ショーダウンに進んだプレイヤーの中から勝者のseat_indexリストを返す。
    (サイドポットは未考慮のシンプルな実装)
    """
    showdown_players = [
        s for s in game_state.table.seats 
        if s.is_occupied and s.status not in ["FOLDED", "OUT"]
    ]

    if not showdown_players:
        return []

    if len(showdown_players) == 1:
        return [showdown_players[0].index]

    best_score = float('inf')
    winners = []

    for seat in showdown_players:
        score = evaluate_hand(seat.hole_cards, game_state.table.community_cards)
        if score < best_score:
            best_score = score
            winners = [seat.index]
        elif score == best_score:
            winners.append(seat.index)
            
    return winners