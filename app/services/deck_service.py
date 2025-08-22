from typing import List
from treys import Card as TreysCard, Deck as TreysDeck
from app.models.deck import Card, Deck


class DeckService:
    """treys を利用してデッキを操作するサービス"""

    def __init__(self):
        self._treys_deck = TreysDeck()

    def reset_deck(self) -> Deck:
        """新しいデッキを生成してシャッフル"""
        self._treys_deck = TreysDeck()
        self._treys_deck.shuffle()
        return Deck(cards=[self._from_treys(c) for c in self._treys_deck.cards])

    def draw(self, num: int = 1) -> List[Card]:
        """カードを指定枚数ドロー"""
        treys_cards = [self._treys_deck.draw(1) for _ in range(num)]
        return [self._from_treys(c) for c in treys_cards]

    def remaining_cards(self) -> int:
        """残りカード枚数"""
        return len(self._treys_deck.cards)

    # --- 内部 util ---

    @staticmethod
    def _from_treys(card_int: int) -> Card:
        """treys の整数カードをアプリの Card に変換"""
        rank = TreysCard.get_rank_int(card_int)
        suit = TreysCard.get_suit_int(card_int)
        return Card(rank=rank, suit=suit)

    @staticmethod
    def to_treys(card: Card) -> int:
        """アプリの Card を treys の整数カードに変換"""
        return TreysCard.new(f"{DeckService._rank_to_str(card.rank)}{DeckService._suit_to_str(card.suit)}")

    @staticmethod
    def _rank_to_str(rank: int) -> str:
        mapping = {11: "J", 12: "Q", 13: "K", 14: "A"}
        return mapping.get(rank, str(rank))

    @staticmethod
    def _suit_to_str(suit: int) -> str:
        return ["c", "d", "h", "s"][suit]