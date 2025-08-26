from dataclasses import dataclass
from typing import Optional
from .player import Player
from .enum import SeatState


@dataclass
class Seat:
    """テーブルの座席（プレイヤーを乗せて、ベットを管理）"""

    index: int                      # 座席番号（0,1,2,...）
    player: Optional[Player] = None # 座っているプレイヤー（空席なら None）
    current_bet: int = 0            # 現在のベット額
    state: SeatState = SeatState.OUT
    acted: bool = True              # このラウンドでアクションを行ったかどうか

    @property
    def is_occupied(self) -> bool:
        """プレイヤーが座っているかどうか"""
        return self.player is not None
    
    @property
    def is_active(self) -> bool:
        """この座席がアクティブかどうか"""
        return self.is_occupied and self.state == SeatState.ACTIVE
    
    def sit_down(self, player: Player) -> None:
        """プレイヤーを座席に座らせる"""
        if self.is_occupied:
            raise ValueError(f"Seat {self.index} is already occupied")
        self.player = player

    def stand_up(self) -> None:
        """プレイヤーを座席から外す"""
        self.player = None
        self.current_bet = 0

    def place_bet(self, amount: int) -> None:
        """座席にいるプレイヤーがベットする"""
        if not self.is_occupied:
            raise ValueError(f"Seat {self.index} is empty")
        if self.player.stack < amount:
            raise ValueError("Not enough chips to bet")
        self.player.stack -= amount
        self.current_bet += amount
