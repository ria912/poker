# app/services/hand_evaluator.py
from typing import List, Tuple
from treys import Evaluator, Card as TreysCard
from ..models.deck import Card
from ..models.seat import Seat

class HandEvaluator:
    """treysライブラリを使用してハンドの評価を行うクラス"""

    def __init__(self):
        self.evaluator = Evaluator()

    def evaluate_hand(self, hole_cards: List[Card], community_cards: List[Card]) -> int:
        """
        ホールカードとコミュニティカードから役の強さを評価します。
        treysの仕様に基づき、戻り値が小さいほど強い役となります。
        
        Args:
            hole_cards (List[Card]): プレイヤーのホールカード2枚。
            community_cards (List[Card]): 場に出ているコミュニティカード。

        Returns:
            int: 役の強さを示すスコア。
        """
        if not hole_cards or len(hole_cards) != 2:
            raise ValueError("Hole cards must contain exactly 2 cards.")
            
        # treysが扱える整数形式にカードを変換
        hand = [card.to_treys_int() for card in hole_cards]
        board = [card.to_treys_int() for card in community_cards]
        
        return self.evaluator.evaluate(hand, board)

    def determine_winners(self, seats_in_hand: List[Seat], community_cards: List[Card]) -> List[List[Seat]]:
        """
        ショウダウンに参加するプレイヤーの中から勝者を決定します。
        チョップ（引き分け）を考慮し、ポットを分け合うプレイヤーのリストのリストを返します。
        
        Note:
            この実装はサイドポットを考慮していません。メインポットの勝者のみを返します。
            AI開発の初期段階ではこの仕様で十分ですが、将来的には拡張が必要です。

        Args:
            seats_in_hand (List[Seat]): ショウダウンに参加するプレイヤーのSeatオブジェクトリスト。
            community_cards (List[Card]): コミュニティカード。

        Returns:
            List[List[Seat]]: 勝者(Seat)のリスト。チョップの場合は複数要素になります。
                                 [[seat1], [seat2, seat3]] のような形式はサイドポット用です。
        """
        if not seats_in_hand:
            return []

        board = [card.to_treys_int() for card in community_cards]
        
        scores = []
        for seat in seats_in_hand:
            if not seat.hole_cards:
                continue
            hand = [card.to_treys_int() for card in seat.hole_cards]
            score = self.evaluator.evaluate(hand, board)
            scores.append((seat, score))
            
        # スコアでソート (値が小さい方が強い)
        scores.sort(key=lambda x: x[1])

        if not scores:
            return []
            
        best_score = scores[0][1]
        
        # 最も良いスコアを持つプレイヤーを勝者とする
        main_pot_winners = [seat for seat, score in scores if score == best_score]
        
        # サイドポットを考慮しないため、勝者リストは1つだけ
        return [main_pot_winners]
        
    def get_rank_string(self, score: int) -> str:
        """スコアから役名を文字列で返します (例: 'Full House')"""
        return self.evaluator.class_to_string(self.evaluator.get_rank_class(score))