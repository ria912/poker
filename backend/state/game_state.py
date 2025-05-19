# state/game_state.py
from models.table import Table
from models.round_manager import RoundManager

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)

    def new_hand(self):
        self.table.start_hand()
        self.round_manager = RoundManager(self.table)  # 新しいハンド用にリセット

# グローバルに1つだけ使うインスタンス
game_state = GameState()
