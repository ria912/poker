from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
import random


SUITS = ["s", "h", "d", "c"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]


class Card(BaseModel):
    """トランプカード（treys互換文字列で表現）"""
    label: str  # 例: "As", "Td"

    def model_post_init(self, __context):
        if len(self.label) != 2:
            raise ValueError(f"invalid card label: {self.label}")
        rank, suit = self.label[0], self.label[1]
        if rank not in RANKS or suit not in SUITS:
            raise ValueError(f"invalid card label: {self.label}")

    def to_treys_int(self) -> int:
        """treys 互換の int へ変換"""
        try:
            from treys import Card as TCard  # type: ignore
        except Exception as e:
            raise ImportError("treys がインストールされていません") from e
        return TCard.new(self.label)


class Deck(BaseModel):
    """シャッフル済みデッキ管理"""
    cards: List[Card] = Field(default_factory=list)
    seed: Optional[int] = None

    def model_post_init(self, __context):
        if not self.cards:
            self.reset(self.seed)

    def reset(self, seed: Optional[int] = None) -> None:
        rng = random.Random(seed)
        self.cards = [Card(label=r + s) for s in SUITS for r in RANKS]
        rng.shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        if n < 1:
            raise ValueError("deal n must be >= 1")
        if len(self.cards) < n:
            raise ValueError("not enough cards in deck")
        out = self.cards[:n]
        self.cards = self.cards[n:]
        return out

    def burn(self) -> None:
        self.deal(1)
