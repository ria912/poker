from pydantic import BaseModel, Field
from typing import List
from treys import Card as TreysCard, Deck as TreysDeck

class Card(BaseModel):
    """
    カード一枚を表現するクラス。
    treysライブラリの整数表現と、人間が読みやすい文字列表現を保持します。
    """
    rank: str  # 例: "A", "K", "7"
    suit: str  # 例: "s", "h"
    
    @classmethod
    def from_int(cls, card_int: int) -> "Card":
        """treysの整数表現からCardオブジェクトを生成する"""
        rank_str = TreysCard.int_to_rank_str(card_int)
        suit_str = TreysCard.int_to_suit_str(card_int)
        return cls(rank=rank_str, suit=suit_str)

class Deck(BaseModel):
    """
    デッキを表現するクラス。
    内部でtreysのDeckを操作します。
    """
    cards: List[int] = Field(default_factory=TreysDeck)

    def shuffle(self):
        """デッキをシャッフルする"""
        self.cards = TreysDeck() # 新しいシャッフル済みのデッキを作成

    def draw(self, n: int = 1) -> List[int]:
        """デッキからn枚のカードを引く"""
        return self.cards.draw(n)
    
    def draw_one(self) -> int:
        """デッキから1枚のカードを引く"""
        return self.cards.draw(1)