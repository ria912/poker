from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from .enum import PlayerState, Position
from .deck import Card


class InvalidActionError(Exception):
    """ゲームにおける無効なアクションを表す例外"""
    pass


class Player(BaseModel):
    """プレイヤーの状態と振る舞いを管理するモデル"""

    player_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stack: int
    hand: List[Card] = Field(default_factory=list)
    position: Optional[Position] = None
    state: PlayerState = PlayerState.WAITING  # 初期状態
    bet_total: int = 0
    has_acted: bool = False  # このラウンドで既に行動したか

    class Config:
        orm_mode = True

    # ----------------------
    # Public Actions
    # ----------------------
    def fold(self):
        self._ensure_active()
        self.state = PlayerState.FOLDED
        self.has_acted = True

    def check(self):
        self._ensure_active()
        # チェック可能条件はサービス層で判定する想定
        self.has_acted = True

    def call(self, amount: int):
        self._ensure_active()
        self._place_bet(amount)
        self.has_acted = True

    def bet(self, amount: int):
        self._ensure_active()
        self._place_bet(amount)
        self.has_acted = True

    def raise_bet(self, amount: int):
        self._ensure_active()
        self._place_bet(amount)
        self.has_acted = True

    # ----------------------
    # Internal Helpers
    # ----------------------
    def _ensure_active(self):
        if self.state != PlayerState.ACTIVE:
            raise InvalidActionError("Player is not in an active state.")

    def _place_bet(self, amount: int):
        if amount > self.stack:
            raise InvalidActionError("Bet amount exceeds player's stack.")
        self.stack -= amount
        self.bet_total += amount
        self.update_state()

    def update_state(self):
        """プレイヤーの状態を最新に更新"""
        if self.stack == 0:
            self.state = PlayerState.ALL_IN
    
    def reset_bet_total(self):
        self.bet_total = 0
    
    def reset_has_acted(self):
        if self.state == PlayerState.ACTIVE:
            self.has_acted = False