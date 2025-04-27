from models.player import Player
import random

class CPUPlayer(Player):
    def decide_action(self, game_state):
        # ランダムにアクション（将来は個性追加）
        return random.choice(["fold", "call", "raise"])
