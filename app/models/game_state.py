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

    current_player_index: Optional[int] = None
    dealer_index: Optional[int] = None
    small_blind: int = 50
    big_blind: int = 100