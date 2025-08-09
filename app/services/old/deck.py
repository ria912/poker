# backend/services/deck.py
from treys import Deck as TreysDeck

class Deck:
    def __init__(self):
        self._deck = TreysDeck()

    def draw(self, num: int = 1):
        return [self._deck.draw(1) for _ in range(num)]

    def reset(self):
        self._deck = TreysDeck()
