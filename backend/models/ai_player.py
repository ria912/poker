from models.player import Player
from models.action import Action
import random

class AIPlayer(Player):
    def __init__(self, name, stack=10000):
        super().__init__(name, stack=stack)
        self.is_human = False

    def decide_action(self, game_info):
        legal_actions = game_info.get('legal_actions', [])
        current_bet = game_info.get('current_bet', 0)
        min_bet = game_info.get('min_bet', 0)
        has_acted = game_info.get('has_acted', False)

        # 簡単なAIロジック例：
        # フォールド可能なら20%でフォールド
        if Action.FOLD in legal_actions and random.random() < 0.2:
            return Action.FOLD, 0

        # コール可能ならコール
        if Action.CALL in legal_actions:
            return Action.CALL, 0

        # ベットまたはレイズ可能なら最低額でベット/レイズ
        if Action.BET in legal_actions:
            return Action.BET, min_bet
        if Action.RAISE in legal_actions:
            return Action.RAISE, min_bet

        # その他はチェック
        if Action.CHECK in legal_actions:
            return Action.CHECK, 0

        # 万が一何もないならフォールド（安全策）
        return Action.FOLD, 0