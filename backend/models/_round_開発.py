from backend.models.table import Table
from backend.models.action import Action
from backend.models.enum import Round, Position, Status

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_order = []  # このラウンドでのアクション順序（毎ラウンド更新）
        self.action_index = 0

    def start_new_hand(self):
        self.table.reset_for_next_round()  # プレイヤー状態、ベットなどリセット
        self.table.deal_hands()
        self.table._post_blinds()  # ここで投稿
        self.start_new_round()

    def start_new_round(self):
        self.table.reset_for_next_round()
        self.action_order = self.get_action_order()
        self.action_index = 0

    def get_action_order(self):
        active_players = self.table.get_active_players()
        sorted_players = sorted(
            active_players,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
        )
        if self.table.round == Round.PREFLOP:
            try:
                bb_index = next(i for i, p in enumerate(sorted_players) if p.position == Position.BB)
                return sorted_players[bb_index + 1:] + sorted_players[:bb_index + 1]
            except StopIteration:
                return sorted_players
        else:
            return sorted_players  # ポストフロップはSB起点で並び替えても良い

    def get_pending_players(self):
        """まだアクションが必要なプレイヤーのリスト"""
        return [
            p for p in self.action_order
            if p.is_active and p.bet_total != self.table.current_bet
        ]

    def process_action(self, player, action):
        # アクション適用（fold/call/raiseなど）
        player.apply_action(action, self.table)

        # AIや次のプレイヤーに進む処理
        pending = self.get_pending_players()
        if not pending:
            self.advance_round()
        else:
            # 次のプレイヤーのindexを更新（順番維持）
            self.action_index = self.action_order.index(pending[0])

    def advance_round(self):
        next_round = Round.next(self.table.round)
        if not next_round:
            self.table.round = Round.SHOWDOWN
            self.table.showdown()
            return

        self.table.round = next_round

        # ボードにカードを配る
        if self.table.round == Round.FLOP:
            self.table.deal_flop()
        elif self.table.round == Round.TURN:
            self.table.deal_turn()
        elif self.table.round == Round.RIVER:
            self.table.deal_river()

        self.start_new_round()
