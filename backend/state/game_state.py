# state/game_state.py
from typing import Optional
from models.table import Table
from models.round_manager import RoundManager

class GameState:
    def __init__(self):
        self.table: Optional[Table] = None
        self.round_manager: Optional[RoundManager] = None

# グローバルインスタンス
game_state = GameState()
