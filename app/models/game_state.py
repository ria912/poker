# models/game_state.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .player import Player
from .enum import Round, State

class GameState(BaseModel):
    """ゲーム全体の進行状態を管理するモデル"""

    round: Round = Round.PREFLOP
    state: State = State.WAITING  # WAITING, IN_PROGRESS, SHOWDOWN, GAME_OVER
    current_turn: Optional[int] = None
    dealer_index: Optional[int] = None

    small_blind: int = 50
    big_blind: int = 100
    min_raise: int = 100
    current_bet: int = 0
    last_aggressor: Optional[int] = None

    round_bets: Dict[int, int] = Field(default_factory=dict)  # プレイヤーID -> 今ラウンドのベット額

    def reset_for_new_hand(self) -> None:
        """新しいハンドに向けて初期化"""
        self.round = Round.PREFLOP
        self.state = State.WAITING
        self.min_raise = self.big_blind
        self.current_bet = 0
        self.last_aggressor = None
        self.round_bets.clear()
    
    def reset_round_bets(self, active_seat_indices: List[int]) -> None:
        """現在のラウンドのベット額をリセット"""
        self.round_bets = {i: 0 for i in active_seat_indices}
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.last_aggressor = None
