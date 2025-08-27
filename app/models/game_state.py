from pydantic import BaseModel, Field
from typing import Optional
from .seat import Table
from .enum import Round, GameStatus

class GameState(BaseModel):
    """ゲーム全体の進行状態を管理するクラス"""
    game_id: str
    table: Table = Field(default_factory=Table)
    status: GameStatus = GameStatus.WAITING
    current_round: Round = Round.PREFLOP
    
    # アクション管理
    active_seat_index: Optional[int] = None # 現在アクションすべきプレイヤーの座席index
    amount_to_call: int = 0 # コールに必要な額
    min_raise_amount: int = 0 # ミニマムレイズ額
    last_raiser_seat_index: Optional[int] = None # 最後にレイズした人の座席index

    def clear_for_new_hand(self):
        """次のハンドのためにゲーム状態をリセットする"""
        self.table.clear_for_new_hand()
        self.status = GameStatus.IN_PROGRESS
        self.current_round = Round.PREFLOP
        self.active_seat_index = None
        self.amount_to_call = 0
        self.min_raise_amount = 0
        self.last_raiser_seat_index = None