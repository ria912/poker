from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

# 他のモデルファイルをインポート
from .enum import PlayerState, Position
from .deck import Card

class Player(BaseModel):
    """プレイヤーの基本情報とゲーム中の状態を管理するモデル"""
    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)
    position: Optional[Position] = None
    state: Optional[PlayerState] = None
    bet_total: int = 0  # このラウンドでのベット額
    
    class Config:
        # Pydantic V2
        # from_attributes = True
        # Pydantic V1
        orm_mode = True

    def fold(self):
        if self.state != PlayerState.ACTIVE:
            raise ValueError("Player is not in an active state.")
        self.state = PlayerState.FOLDED

    def check(self):
        if self.state != PlayerState.ACTIVE:
            raise ValueError("Player is not in an active state.")

    def call(self, amount: int):
        if amount > self.stack:
            raise ValueError("amountがstackを超えています.")
        self.stack -= amount
        self.bet_total += amount
        self.update_state()
        
    def bet(self, amount: int):
        if amount > self.stack:
            raise ValueError("amountがstackを超えています.")
        self.stack -= amount
        self.bet_total += amount
        self.update_state()

    def raise_bet(self, amount: int):
        if amount > self.stack:
            raise ValueError("amountがstackを超えています.")
        self.stack -= amount
        self.bet_total += amount
        self.update_state()

    def update_state(self):
        if self.stack == 0:
            self.state = PlayerState.ALL_IN