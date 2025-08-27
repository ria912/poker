from typing import Optional
import uuid
from .table import Table
from .enum import Round, GameStatus

class GameState:
    """ゲーム全体の進行状態を管理するクラス"""
    def __init__(self):
        self.game_id: str = str(uuid.uuid4())
        self.table: Table = Table()
        self.status: GameStatus = GameStatus.WAITING
        self.current_round: Round = Round.PREFLOP

        # アクション管理
        self.active_seat_index: Optional[int] = None  # 現在アクションすべきプレイヤーの座席index
        self.amount_to_call: int = 0                  # コールに必要な額
        self.min_raise_amount: int = 0                # ミニマムレイズ額
        self.last_raiser_seat_index: Optional[int] = None  # 最後にレイズした人の座席index

    def clear_for_new_hand(self):
        """次のハンドのためにゲーム状態をリセットする"""
        self.table.collect_bets()
        self.status = GameStatus.IN_PROGRESS
        self.current_round = Round.PREFLOP
        self.active_seat_index = None
        self.amount_to_call = 0
        self.min_raise_amount = 0
        self.last_raiser_seat_index