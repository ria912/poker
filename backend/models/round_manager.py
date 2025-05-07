# models/round_manager.py
from models.table import Table
from models.position import ASSIGNMENT_ORDER
from models.action import get_legal_actions, apply_action

class RoundManager:
    def __init__(self, table: Table):
        self.table = table  # テーブルの情報を保持
        self.street = 'preflop'  # 最初はプリフロップ
        self.action_index = 0  # アクションを開始するプレイヤーのインデックス
        self.last_raiser = None  # 最後にレイズしたプレイヤー

    def proceed(self):
        """
        現在のストリートにおけるプレイヤーのアクションを処理し、
        次のストリートへ進む。
        """
        if self.street == 'preflop':
            self._start_betting_round()
        elif self.street == 'flop':
            self._deal_flop()
            self._start_betting_round()
        elif self.street == 'turn':
            self._deal_turn()
            self._start_betting_round()
        elif self.street == 'river':
            self._deal_river()
            self._start_betting_round()
        elif self.street == 'showdown':
            self._showdown()

    def get_action_order(street, seats):
        # 起点ポジション
        start_pos = 'BB' if street == 'preflop' else 'BTN'
        # プレイヤーをポジションで辞書化（欠員対策）
        pos_to_player = {
            p.position: p for p in seats if p and not p.has_folded and not p.has_left and p.stack > 0
        }
        # 起点の次から1周分のアクション順を作成
        start_index = ASSIGNMENT_ORDER.index(start_pos)
        action_order = [
            ASSIGNMENT_ORDER[(start_index + 1 + i) % len(ASSIGNMENT_ORDER)]
            for i in range(len(ASSIGNMENT_ORDER))
        ]
        # 実際に存在するプレイヤーだけを返す
        return [pos_to_player[pos] for pos in action_order if pos in pos_to_player]

    def _start_betting_round(self):
        action_order = self.get_action_order()
        self.action_index = 0

        while not self.is_betting_round_over():
            current_player = action_order[self.action_index]
            self.handle_player_action(current_player)
            self.action_index = (self.action_index + 1) % len(action_order)

    def handle_player_action(self, player):
        legal_actions = get_legal_actions(player, self.table)
        action, amount = player.decide_action({
            "legal_actions": legal_actions,
            "table": self.table.to_dict()
        })

        apply_action(player, action, self.table, amount)

        if action in ['bet', 'raise']:
            self.last_raiser = player

    def is_betting_round_over(self):
        """
        ベッティングラウンドが終了したかを判断する条件を定義
        例: すべてのプレイヤーがコールまたはフォールドした場合
        """
        pass

    def _deal_flop(self):
        for _ in range(3):
            self.table.community_cards.append(self.table.deck.draw())

    def _deal_turn(self):
        self.table.community_cards.append(self.table.deck.draw())

    def _deal_river(self):
        self.table.community_cards.append(self.table.deck.draw())

    def _showdown(self):
        """ ショーダウンでの勝者を決定する処理 """
        pass
