from typing import Optional
from .deck import Deck
from .table import Table
from .enum import Round, GameStatus
class GameState:
    """ゲーム全体の進行状態を管理するクラス"""
    def __init__(self, seat_count: int = 6, big_blind: int = 100, small_blind: int = 50):
        self.table: Table = Table(seat_count=seat_count)
        self.big_blind: int = big_blind
        self.small_blind: int = small_blind
        self.status: GameStatus = GameStatus.WAITING
        self.current_round: Round = Round.PREFLOP

        # アクション管理
        self.current_seat_index: Optional[int] = None
        self.dealer_seat_index: Optional[int] = None
        self.amount_to_call: int = 0
        self.min_raise_amount: int = 0
        self.last_raiser_seat_index: Optional[int] = None

    def clear_for_new_hand(self):
        """次のハンドのためにゲーム状態をリセットする"""
        self.table.reset()

        self.status = GameStatus.WAITING
        self.current_round = Round.PREFLOP
        self.active_seat_index = None
        self.amount_to_call = 0
        self.min_raise_amount = 0
        self.last_raiser_seat_index = None