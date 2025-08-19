from pydantic import BaseModel, Field
from typing import List
import uuid

from .deck import Card
from .enum import PlayerState, Position


class Player(BaseModel):
    """プレイヤー（stackを管理）"""

    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)
    position: Position | None = None
    state: PlayerState = PlayerState.ACTIVE

    def receive_card(self, card: Card) -> None:
        """カードを受け取る"""
        self.hand.append(card)

    def clear_hand(self) -> None:
        """ハンドをリセット"""
        self.hand.clear()

    def is_active(self) -> bool:
        """プレイヤーがアクティブかどうかを判定"""
        return self.state == PlayerState.ACTIVE
    
    def reset_state_acted(self) -> None:
        if self.state == PlayerState.ACTED:
            self.state = PlayerState.ACTIVE

    def reset_for_new_hand(self) -> None:
        self.clear_hand()
        self.position = None
        if self.stack <= 0:
            self.state = PlayerState.OUT
        else:
            self.state = PlayerState.ACTIVE