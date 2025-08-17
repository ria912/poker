# models/game_state.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .table import Table
from .enum import Round, State
import uuid

class GameState(BaseModel):
    """ゲーム全体の進行状態を管理するモデル"""
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table: Table

    round: Round = Round.PREFLOP
    state: State = State.WAITING  # WAITING, RUNNING, SHOWDOWN, FINISHED
    
    current_player_index: Optional[int] = None
    dealer_index: Optional[int] = None
    small_blind: int = 50
    big_blind: int = 100

    @property
    def players(self) -> List[Player]:
        """座っているプレイヤーだけを返す"""
        return [seat.player for seat in self.table.seats if seat.is_occupied]

    @property
    def deck(self) -> Deck:
        return self.table.deck