from backend.models.table import Table
from backend.services.round import RoundManager
from backend.models.position import PositionManager
from backend.models.deck import Deck
from backend.models.human_player import HumanPlayer
from backend.ai.ai_player import AIPlayer
from backend.models.enum import Status
from backend.schemas.game_state_schema import GameStateSchema

class GameState:
    def __init__(self):
        self.table = Table()
        self.deck = self.table.deck  # TableがDeckを持つので参照だけ
        self.round_manager = RoundManager(self.table)
        self.status = Status.ROUND_CONTINUE

    def start_new_hand(self):
        """新しいハンドの初期化"""
        self.table.reset()
        self.table.starting_new_hand()
        self.round_manager.reset()
        self.status = Status.ROUND_CONTINUE
        return self.get_state()

    def receive_human_action(self, action: str, amount: int = 0):
        """人間プレイヤーのアクションを受けて進行"""
        # 現在のアクション順の席を取得
        seat = self.round_manager.get_current_seat()
        if not seat or not seat.player or not seat.player.is_human:
            raise ValueError("現在アクション可能な人間プレイヤーがいません")
        # actメソッドを通じてアクションを適用
        seat.player.act(action, amount, self.table)
        self.round_manager.action_index += 1
        # ラウンド進行
        self.status = self.round_manager.proceed()
        return self.get_state()

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