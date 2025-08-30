from typing import Optional
from .deck import Deck
from .table import Table
from .action import Action
from .enum import Round, GameStatus, ActionType
from .game_config import GameConfig

class GameState:
    """ゲーム全体の進行状態を管理するクラス"""
    def __init__(self, config: GameConfig):
        self.config: GameConfig = config
        self.table: Table = Table(seat_count=config.seat_count)
        self.status: GameStatus = GameStatus.WAITING
        self.current_round: Round = Round.PREFLOP
        self.history: list[Action] = []

        # アクション管理
        self.current_seat_index: Optional[int] = None
        self.dealer_seat_index: Optional[int] = None
        self.amount_to_call: int = 0
        self.min_raise_amount: int = 0
        self.last_raiser_seat_index: Optional[int] = None
    
    @property
    def big_blind(self) -> int:
        return self.config.big_blind

    @property
    def small_blind(self) -> int:
        return self.config.small_blind

    def add_action(self, player_id: str, action_type: ActionType, amount: Optional[int] = None):
        """アクションを履歴に追加する"""
        action = Action(player_id=player_id, action_type=action_type, amount=amount)
        self.history.append(action)

    def clear_for_new_hand(self):
        """次のハンドのためにゲーム状態をリセットする"""
        self.table.reset()
        self.history = []

        self.status = GameStatus.WAITING
        self.current_round = Round.PREFLOP

        self.current_seat_index = None
        self.amount_to_call = 0
        self.min_raise_amount = 0
        self.last_raiser_seat_index = None