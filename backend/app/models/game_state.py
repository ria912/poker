from typing import Optional, List, Dict, Any
from .deck import Deck
from .table import Table
from .action import Action
from .enum import Round, GameStatus, ActionType

class GameState:
    """ゲーム全体の進行状態を管理するクラス"""
    def __init__(self, big_blind: int=100, small_blind: int=50, seat_count: int=6):
        self.table: Table = Table(seat_count=seat_count)
        self.status: GameStatus = GameStatus.WAITING
        self.current_round: Round = Round.PREFLOP
        self.history: list[Action] = []
        
        self.big_blind: int = big_blind
        self.small_blind: int = small_blind

        self.current_seat_index: Optional[int] = None
        self.dealer_seat_index: Optional[int] = None
        self.amount_to_call: int = 0
        self.min_raise_amount: int = 0
        self.last_raiser_seat_index: Optional[int] = None

        # ★★★ 提案1の修正点 ★★★
        # フロントエンドに勝者情報を渡すための一時的なフィールド
        self.winners: List[Dict[str, Any]] = []


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
        
        # ★★★ 提案1の修正点 ★★★
        # 新しいハンドの開始時に勝者情報をクリア
        self.winners = []
