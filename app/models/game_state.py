# models/game_state.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .table import Table
from .enum import Round, GameStatus
import uuid

class GameState(BaseModel):
    """ゲーム全体の進行状態を管理するモデル"""
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table: Table

    round: Round = Round.PREFLOP
    status: GameStatus = GameStatus.WAITING  # WAITING, RUNNING, SHOWDOWN, FINISHED

    current_index: Optional[int] = None
    dealer_index: Optional[int] = None
    small_blind: int = 50
    big_blind: int = 100

    @property
    def players(self) -> List[Player]:
        return [s.player for s in self.table.seats if s.player is not None]

    def next_round(self) -> None:
        """次のラウンドに進める"""
        self.round = self.round.next()

    def reset_for_new_hand(self) -> None:
        """新しいハンドに向けて初期化"""
        self.table.reset_for_new_hand()
        self.round = Round.PREFLOP
        self.state = State.WAITING
