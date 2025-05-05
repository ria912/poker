from backend.models.table import Table
from backend.models.round_manager import RoundManager

class GameState:
    def __init__(self):
        self.table = Table()
        self.round_manager = RoundManager(self.table)
        self.round_manager.start_new_hand()

    def to_dict(self):
        return self.table.to_dict()

    def apply_action(self, action_data):
        # action_dataに基づいて人間プレイヤーのアクションを処理
        pass

game_state = GameState()
