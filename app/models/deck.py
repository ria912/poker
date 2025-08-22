# app/models/deck.py
import random
from typing import List, Optional
from pydantic import BaseModel


class Card(BaseModel):
    """1枚のトランプカード"""
    rank: str   # '2'〜'A'
    suit: str   # '♠', '♥', '♦', '♣'

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


class Deck:
    """52枚のカードデッキ"""

    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    SUITS = ["s", "h", "d", "c"]  # treys準拠

    def __init__(self, shuffle: bool = True):
        self.cards: List[Card] = [
            Card(rank=rank, suit=suit)
            for suit in self.SUITS
            for rank in self.RANKS
        ]
        if shuffle:
            self.shuffle()

    def shuffle(self) -> None:
        """デッキをシャッフル"""
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        """カードをn枚引く"""
        if n > len(self.cards):
            raise ValueError("Not enough cards in deck")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

    def reset(self, shuffle: bool = True) -> None:
        """デッキをリセット"""
        self.__init__(shuffle=shuffle)

    def __len__(self) -> int:
        return len(self.cards)