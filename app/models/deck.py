import random
from typing import List, Tuple

class Deck:
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    def __init__(self):
        self.cards: List[Tuple[str, str]] = [(rank, suit) for suit in self.suits for rank in self.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Tuple[str, str]]:
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn