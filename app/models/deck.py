from pydantic import BaseModel, Field
from typing import List
import random
from treys import Card as TreysCard, Deck as TreysDeck


class Card(BaseModel):
    """アプリ側のカード表現（rank, suit を保持）"""

    rank: int  # 2-14 (11=J, 12=Q, 13=K, 14=A)
    suit: int  # 0=クラブ, 1=ダイヤ, 2=ハート, 3=スペード

    def __str__(self):
        rank_str = {11: "J", 12: "Q", 13: "K", 14: "A"}.get(self.rank, str(self.rank))
        suit_str = ["♣", "♦", "♥", "♠"][self.suit]
        return f"{rank_str}{suit_str}"

    def to_treys(self) -> int:
        """treys の int カードに変換"""
        rank_map = {14: "A", 13: "K", 12: "Q", 11: "J",
                    10: "T", 9: "9", 8: "8", 7: "7", 6: "6",
                     5: "5", 4: "4", 3: "3", 2: "2"}
        suit_map = {0: "c", 1: "d", 2: "h", 3: "s"}
        treys_str = f"{rank_map[self.rank]}{suit_map[self.suit]}"
        return TreysCard.new(treys_str)

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


class Deck(BaseModel):
    """treys を内部的に利用するデッキ"""

    cards: List[int] = Field(default_factory=lambda: TreysDeck().cards)

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        if len(self.cards) < n:
            raise ValueError("山札が不足しています")
        drawn, self.cards = self.cards[:n], self.cards[n:]
        return [Card.from_treys(c) for c in drawn]