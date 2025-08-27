# app/models/deck.py
import random
from typing import List
from treys import Card as TreysCard


class Card:
    
    rank_order = "23456789TJQKA"
    suit_map = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}

    def __init__(self, rank: str, suit: str):
        if rank not in self.rank_order:
            raise ValueError(f"Invalid card rank: {rank}")
        if suit not in self.suit_map:
            raise ValueError(f"Invalid card suit: {suit}")

        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        return f"{self.rank}{self.suit_map[self.suit]}"

    def to_treys_int(self) -> int:
        return TreysCard.new(self.rank + self.suit)


class Deck:

    def __init__(self):
        self.cards: List[Card] = [
            Card(rank, suit)
            for suit in Card.suit_map.keys()
            for rank in Card.rank_order
        ]
        self.shuffle()

    def shuffle(self):
        """デッキをシャッフル"""
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        """カードをn枚引く"""
        if n > len(self.cards):
            raise ValueError("Not enough cards in the deck")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn
