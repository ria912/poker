from models.player import Player
from models.table import Table
from models.action import Action
from ai import CPUPlayer

class PokerGame:
    def __init__(self):
        self.players = [Player("You", is_human=True)] + [CPUPlayer(f"CPU{i}") for i in range(1, 6)]
        self.table = Table(self.players)
        self.action_log = []

    # プレイヤーのアクションを処理するメソッド
    def process_action(self, player, action_type, amount=0):
        action = Action(player, action_type, amount)
        action.apply(self.table)
        self.action_log.append(action)
        self.table.next_player()

    # プレイヤーのアクションを処理するメソッド
    def handle_player_action(self, player, action_name, current_bet, min_raise):
        Action.apply_action(player, action_name, current_bet, min_raise)

    def start_hand(self):
        self.table.button_index = (self.table.button_index + 1) % len(self.players)
        self.table.deal_cards()  # ← この中でassign_positions()も呼ばれる
        self.table.start_round()

    def process_turn(self):
        result = self.table.proceed_to_next_turn()

        if result == 'end_hand':
            self.end_hand()
        elif result == 'continue':
            current_player = self.table.players[self.table.active_player_index]
            # AIか人間かで分岐処理する場所（例：AIなら即Action、HumanならUI待機）

    def end_betting_round(self):
        self.table.pot += sum(p.current_bet for p in self.table.players)
        self.table.advance_stage()
        self.table.start_betting_round()

    def end_hand(self):
        # 勝者判定やリセット処理
        pass

    def to_dict(self):
        # ゲーム状態を辞書化してセッションに保存
        return {
            "players": [p.to_dict() for p in self.players],
            "table": self.table.to_dict()
        }
