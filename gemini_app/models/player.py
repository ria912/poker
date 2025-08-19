from pydantic import BaseModel, Field
from typing import List, Optional
from .enum import Position, Action
from .deck import Card

class Player(BaseModel):
    """プレイヤーの状態を管理するクラス"""
    uuid: str
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)
    position: Optional[Position] = None
    
    # ハンドごとの状態
    is_active: bool = True  # フォールドしていないか
    is_all_in: bool = False
    bet_amount_in_round: int = 0  # 現在のラウンドでの合計ベット額

    def clear_for_new_hand(self):
        """次のハンドのためにプレイヤーの状態をリセットする"""
        self.hand = []
        self.is_active = True
        self.is_all_in = False
        self.bet_amount_in_round = 0

    def to_dict_for_public(self):
        """他のプレイヤーに公開して良い情報のみを辞書として返す"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "stack": self.stack,
            "position": self.position.value if self.position else None,
            "is_active": self.is_active,
            "is_all_in": self.is_all_in,
            "bet_amount_in_round": self.bet_amount_in_round,
        }