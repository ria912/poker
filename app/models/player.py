from pydantic import BaseModel, Field
from typing import List
import uuid

from .deck import Card

class Player(BaseModel):
    """プレイヤー（stackを管理）"""

    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)

    def pay(self, amount: int) -> None:
        """指定した金額を支払う"""
        self.stack -= amount

    def receive_card(self, card: Card) -> None:
        """カードを受け取る"""
        self.hand.append(card)

    def clear_hand(self) -> None:
        """ハンドをリセット"""
        self.hand.clear()