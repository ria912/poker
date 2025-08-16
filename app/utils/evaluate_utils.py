# app/utils/evaluate_utils.py
from typing import List, Tuple, Dict
from treys import Evaluator
from models.deck import Card


class EvaluateUtils:
    """役判定を行うユーティリティ（treysラッパー）"""

    evaluator = Evaluator()

    @classmethod
    def evaluate_hand(cls, hand: List[Card], board: List[Card]) -> Tuple[int, str]:
        """
        役判定を行い、スコアと役名を返す
        - score: 小さいほど強い
        - name: 役名文字列
        """
        hand_t = [c.to_treys() for c in hand]
        board_t = [c.to_treys() for c in board]
        score = cls.evaluator.evaluate(hand_t, board_t)
        name = cls.evaluator.class_to_string(cls.evaluator.get_rank_class(score))
        return score, name

    @classmethod
    def compare_hands(cls, players: Dict[str, List[Card]], board: List[Card]) -> str:
        """
        複数プレイヤーの役を比較して勝者のplayer_idを返す
        """
        best_id = None
        best_score = None
        for pid, hand in players.items():
            score, _ = cls.evaluate_hand(hand, board)
            if best_score is None or score < best_score:
                best_id, best_score = pid, score
        return best_id