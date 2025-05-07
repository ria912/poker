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
            self.street = 'flop'
        elif self.street == 'flop':
            self._deal_flop()
            self._start_betting_round()
            self.street = 'turn'
        elif self.street == 'turn':
            self._deal_turn()
            self._start_betting_round()
            self.street = 'river'
        elif self.street == 'river':
            self._deal_river()
            self._start_betting_round()
            self.street = 'showdown'
        elif self.street == 'showdown':
            self._showdown()

    def get_action_order(self):
        # 起点ポジション
        start_pos = 'BB' if self.street == 'preflop' else 'BTN'
        # 実在するアクティブなプレイヤーをポジションで辞書化（欠員対策）
        pos_to_player = {
            p.position: p for p in self.table.seats if p and not p.has_folded and not p.has_left and p.stack > 0
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
        # プレイヤーのアクションを処理する
        legal_actions = get_legal_actions(player, self.table)
        action, amount = player.decide_action({
            "legal_actions": legal_actions,
            "table": self.table.to_dict(),
            "has_acted": player.has_acted
        })
        # プレイヤーがアクションを選択したら、アクションを適用する
        apply_action(player, action, self.table, amount)
        player.last_action = action
        player.has_acted = True

        if action == 'fold':
            player.has_folded = True

        if action in ['bet', 'raise']:
            self.last_raiser = player
            # 他のアクティブプレイヤーの has_acted をリセット
            for p in self.table.seats:
                if (
                    p and not p.has_folded and not p.has_left and p.stack > 0
                    and p != player # 自分以外のプレイヤー
                ):
                    p.has_acted = False

    def is_betting_round_over(self):
        """
        全プレイヤーがアクションを終えていて、
        かつ、全員が同じ額をベットしている（またはフォールドしている）状態ならラウンド終了。
        """
        active_players = [p for p in self.table.seats
                          if p and not p.has_folded and not p.has_left and p.stack > 0]

        # 1人以下なら当然終了
        if len(active_players) <= 1:
            return True

        for player in active_players:
            # まだアクションしていない → ラウンド続行
            if not player.has_acted:
                return False

            # オールインなら、それ以上のアクションはできない
            if player.stack == 0:
                continue

            # 通常のベット一致確認
            if player.current_bet != self.table.current_bet:
                return False

        return True
    
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
