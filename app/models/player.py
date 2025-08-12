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
    current_bet: int = 0  # このラウンドでのベット額
    is_turn: bool = False # 現在アクションする番か
    
    class Config:
        # Pydantic V2
        # from_attributes = True
        # Pydantic V1
        orm_mode = True