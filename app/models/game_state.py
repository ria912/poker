from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

from .table import Table, Seat
from .player import Player
from .deck import Deck
from .enum import GameStatus

class GameState(BaseModel):
    """
    アプリケーションのルートとなる、ゲーム全体の状態を管理するシングルトン的なモデル。
    このモデルが全ての状態を保持する。
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table: Table = Field(default_factory=Table)
    deck: Deck = Field(default_factory=Deck)
    game_status: GameStatus = Field(default=GameStatus.WAITING)  # ゲームの状態: 'waiting', 'in_progress', 'finished'
    active_player_id: Optional[str] = None # アクション待ちのプレイヤーID

    @property
    def seats(self) -> List[Seat]:
        return self.table.seats

    @property
    def players(self) -> List[Player]:
        """テーブルに参加している全プレイヤーのリストを動的に取得する"""
        return [seat.player for seat in self.seats if seat.is_occupied]

    class Config:
        orm_mode = True

game_state = GameState()