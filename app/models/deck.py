from pydantic import BaseModel
from treys import Deck as TreysDeck, Card as TreysCard
from typing import Protocol, List

# --- 改善案2: 依存関係の注入(DI)のためのインターフェース定義 ---
class DeckInterface(Protocol):
    """デッキの振る舞いを定義するインターフェース"""
    def draw(self, n: int = 1) -> List[int] | int:
        ...

# --- 改善案3: デバッグと可読性向上のための __str__ 実装 ---
class Card(BaseModel):
    """カード情報（表示用に文字列変換対応）"""
    rank: int
    suit: int

    @classmethod
    def from_treys(cls, treys_card: int) -> "Card":
        """treys の int から自作 Card に変換"""
        str_repr = TreysCard.int_to_str(treys_card)
        rank_map = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                    "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
        suit_map = {"s": 3, "h": 2, "d": 1, "c": 0} # treys suits: spades, hearts, diamonds, clubs
        rank_char, suit_char = str_repr[0], str_repr[1]
        return cls(rank=rank_map[rank_char], suit=suit_map[suit_char])

    def to_treys(self) -> int:
        """自作 Card から treys の int に変換"""
        rank_map_inv = {v: k for k, v in Card._get_rank_map().items()}
        suit_map_inv = {v: k for k, v in Card._get_suit_map().items()}
        card_str = f"{rank_map_inv.get(self.rank)}{suit_map_inv.get(self.suit)}"
        return TreysCard.new(card_str)

    def __str__(self) -> str:
        rank_map_inv = {14: "A", 13: "K", 12: "Q", 11: "J", 10: "T",
                        9: "9", 8: "8", 7: "7", 6: "6", 5: "5", 4: "4", 3: "3", 2: "2"}
        suit_map_inv = {3: "s", 2: "h", 1: "d", 0: "c"}
        return f"{rank_map_inv.get(self.rank, '?')}{suit_map_inv.get(self.suit, '?')}"

    def __repr__(self) -> str:
        return f"<Card: {self}>"
    
    @staticmethod
    def _get_rank_map():
        return {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}

    @staticmethod
    def _get_suit_map():
        return {"s": 3, "h": 2, "d": 1, "c": 0}


class Deck:
    """カードデッキ"""
    def __init__(self, deck_impl: DeckInterface = TreysDeck()):
        self._deck = deck_impl

    def draw(self, n: int = 1) -> list[Card]:
        """指定した枚数のカードをCardモデルのリストとして引く"""
        if n == 1:
            return [Card.from_treys(self._deck.draw(1))]
        return [Card.from_treys(card_int) for card_int in self._deck.draw(n)]