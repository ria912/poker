from pydantic import BaseModel
from typing import List
import uuid


class Card(BaseModel):
    """アプリ側で扱うカード表現（rank, suit を保持）"""
    rank: int  # 2-14 (11=J, 12=Q, 13=K, 14=A)
    suit: int  # 0=クラブ, 1=ダイヤ, 2=ハート, 3=スペード

    def __str__(self) -> str:
        rank_str = {11: "J", 12: "Q", 13: "K", 14: "A"}.get(self.rank, str(self.rank))
        suit_str = ["♣", "♦", "♥", "♠"][self.suit]
        return f"{rank_str}{suit_str}"


class Deck(BaseModel):
    """デッキの状態を保持するモデル"""
    deck_id: str = uuid.uuid4().hex
    cards: List[Card] = []