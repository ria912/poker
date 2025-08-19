from pydantic import BaseModel
from treys import Deck as TreysDeck, Card as TreysCard

class Card(BaseModel):
    """カード情報（表示用に文字列変換対応）"""
    rank: str
    suit: str

    @classmethod
    def from_treys(cls, treys_card: int) -> "Card":
        """treys の int から自作 Card に変換"""
        str_repr = TreysCard.int_to_str(treys_card)  # 例: 'As'
        rank_map = {"A": 14, "K": 13, "Q": 12, "J": 11,
                    "T": 10, "9": 9, "8": 8, "7": 7, "6": 6,
                     "5": 5, "4": 4, "3": 3, "2": 2}
        suit_map = {"c": 0, "d": 1, "h": 2, "s": 3}
        rank, suit = str_repr[0], str_repr[1]
        return cls(rank=rank_map[rank], suit=suit_map[suit])

class Deck:
    """カードデッキ"""
    def __init__(self):
        self._deck = TreysDeck()

    def draw(self, n: int = 1) -> list[int]:
        return [self._deck.draw(1) for _ in range(n)]
