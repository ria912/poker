#backend/state/single_game_state.py
from backend.models.table import Table
from backend.services.models.round import RoundManager
from backend.models.position import PositionManager
from backend.models.deck import Deck

from backend.models.human_player import HumanPlayer
from backend.models.ai_player import AIPlayer

from backend.models.enum import Status


class GameState:
    def __init__(self):
        self.table = Table()
        self.deck = Deck()
        self.round_manager = RoundManager(self.table)
        self.status = Status.ROUND_CONTINUE

    def start_game(self):
        """ゲーム開始時の初期化処理"""
        self.deck.shuffle()
        self.table.deck = self.deck

        self.table.reset()  # プレイヤー状態、ベット、ボード初期化
        self.deck.deal_hands(self.table.seats)

        PositionManager.set_btn_index(self.table)
        PositionManager.assign_positions(self.table)

        self.round_manager.reset()
        self.status = Status.ROUND_CONTINUE

    def proceed(self):
        """1アクション or ラウンド進行"""
        if self.is_game_over():
            self.status = Status.GAME_OVER
        else:
            self.status = self.round_manager.proceed()

    def get_state(self) -> GameStateSchema:
        return GameStateSchema.from_table(self.table)
        
    def is_game_over(self) -> bool:
        """アクティブプレイヤーが1人ならゲーム終了"""
        return len(self.table.get_active_seats()) <= 1

    def add_ai_players(self, num_players: int):
        """AIプレイヤーを自動配置"""
        for i in range(num_players):
            seat = self.table.seats[i]
            seat.player = AIPlayer(name=f"AI-{i}")
            seat.index = i

    def add_human_player(self, seat_index: int, name: str = "You"):
        """任意の席に人間プレイヤーを追加"""
        seat = self.table.seats[seat_index]
        seat.player = HumanPlayer(name=name)
        seat.index = seat_index