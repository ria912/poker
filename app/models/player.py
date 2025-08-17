from pydantic import BaseModel, Field
from typing import List
import uuid

from .deck import Card
from .enum import PlayerState, Position


class Player(BaseModel):
    """プレイヤー（財布＝stackを管理）"""

    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)
    position: Position | None = None
    state: PlayerState = PlayerState.WAITING

    def pay(self, amount: int) -> int:
        """スタックから指定額を支払う"""
        if amount > self.stack:
            raise ValueError("スタック不足")
        self.stack -= amount
        return amount

    def receive_card(self, card: Card) -> None:
        """カードを受け取る"""
        self.hand.append(card)

    def clear_hand(self) -> None:
        """ハンドをリセット"""
        self.hand.clear()
        self.state = PlayerState.WAITING