from pydantic import BaseModel, Field
from typing import List
import treys

# treysライブラリのCardを内部的に利用
# treys.Card.new('Ah') -> hand=[1]
# treys.Card.int_to_str(hand[0]) -> 'Ah'

class Card(BaseModel):
    """カード情報を保持するモデル"""
    rank: str  # e.g., 'A', 'K', 'Q', 'J', 'T', '9'...'2'
    suit: str  # e.g., 's' (spades), 'h' (hearts), 'd' (diamonds), 'c' (clubs)
    
    # treysで扱える形式の文字列表現を返すプロパティ
    @property
    def treys_str(self) -> str:
        # treysでは 'T' を使うので '10' を変換
        rank_str = self.rank if self.rank != '10' else 'T'
        return f"{rank_str}{self.suit}"

class Deck(BaseModel):
    """デッキ情報を保持するモデル"""
    cards: List[Card] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.cards:
            self.shuffle()

    def shuffle(self):
        """デッキをシャッフルして52枚のカードを生成する"""
        treys_deck = treys.Deck()
        self.cards = []
        for card_int in treys_deck.cards:
            card_str = treys.Card.int_to_str(card_int)
            rank = card_str[0]
            suit = card_str[1]
            self.cards.append(Card(rank=rank, suit=suit))
    
    def deal(self, num_cards: int) -> List[Card]:
        """指定された枚数のカードをデッキから配る"""
        if len(self.cards) < num_cards:
            # エラーハンドリングは呼び出し元(service層)で行うのが一般的
            raise ValueError("Not enough cards in the deck")
        
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards