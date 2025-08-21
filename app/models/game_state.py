# models/game_state.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .player import Player
from .table import Table
from .enum import Round, GameStatus

class GameState(BaseModel):
    """ゲーム全体の進行状態を管理するモデル"""
    small_blind: int = 50
    big_blind: int = 100
    table: Table

    round: Round = Round.PREFLOP
    status: GameStatus = GameStatus.WAITING  # WAITING, IN_PROGRESS, SHOWDOWN, GAME_OVER

    current_player_index: Optional[int] = None
    dealer_index: Optional[int] = None
    
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
        self.state = GameStatus.WAITING
