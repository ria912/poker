# models/_round_manager.py
from backend.models.table import Table
from backend.models.action import ActionManager
from backend.models.enum import Round, Status, Position, Action

class RoundManager:
    """ポーカーのラウンド運用ロジック"""

    def __init__(self, table: Table):
        self.table = table
        self.action_order = []  # アクションするプレイヤーの順序
        self.action_index = 0
        self.current_player = None
        self.status = Status.RUNNING

    # ---- Public API ----

    def start_new_hand(self):
        """新しくハンドをスタートして最初のラウンドも設定する。"""
        self.table.reset_for_new_hand()
        self.table.deal_hands()
        self.table._post_blinds()
        self.start_new_round()

    def start_new_round(self):
        """次のラウンドに向けた初期化。プレイヤーのアクション順も再算出。"""
        self.table.reset_for_next_round()
        self.action_order = self.prepare_action_order()

    def step(self):
        """1アクション分ゲームを進める。途中または最後にゲーム状態も変化していく。"""
        if self.table.round == Round.SHOWDOWN:
            self.status = Status.HAND_OVER
            return self.status

        if self.all_actions_complete():
            return self.advance_round()

        self.current_player = self.action_order[self.action_index]

        if self.current_player.is_human:
            self.status = Status.WAITING_FOR_HUMAN
            return self.status
        else:
            self.status = Status.WAITING_FOR_AI
            return self.execute_ai_action(self.current_player)

    # ---- Private methods ----

    def prepare_action_order(self):
        """プレイヤーの行動順序を整理して帰す。"""
        active_unacted = [p for p in self.table.get_active_players()
                           if not p.has_acted]
        action_order = sorted(
            active_unacted,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
        )

        if self.table.round == Round.PREFLOP and action_order:
            # BBの後からスタート
            try:
                bb_index = next(
                    i for i, p in enumerate(action_order) if p.position == Position.BB
                )
                return action_order[bb_index + 1:] + action_order[:bb_index + 1]
            except Exception as e:
                raise RuntimeError(f"BB を取得して行動順序を整理に失敗: {e}")

        return action_order

    def all_actions_complete(self):
        """すべてのプレイヤーがアクション済みまたはフォールドしているか。"""
        return all(
            p.has_acted or not p.is_active
            for p in self.table.seats if p
        )

    def execute_ai_action(self, player):
        """AIプレイヤーのアクションを実行して次に移る。"""
        try:
            action, amount = player.decide_action(self.table)
        except Exception as e:
            raise RuntimeError(f"AIのアクション取得失敗: {e}")

        if action is None or amount is None:
            self.status = Status.WAITING_FOR_AI
            return self.status

        ActionManager.apply_action(self.table, player, action, amount)
        self.log_action(player, action, amount)

        if action in Action.betting_actions():
            self.table.last_raiser = player
            for p in self.table.seats:
                if p and p.is_active and p is not player:
                    p.has_acted = False

        self.action_index += 1
        self.status = Status.AI_ACTED
        return self.status

    def advance_round(self):
        """次のラウンドに移行。最後ならハンドも終わる。"""
        next_round = Round.next(self.table.round)
        if not next_round:
            self.table.round = Round.SHOWDOWN
            self.table.showdown()
            self.status = Status.HAND_OVER
            return self.status

        self.table.round = next_round

        if self.table.round == Round.FLOP:
            self.table.deal_flop()
        elif self.table.round == Round.TURN:
            self.table.deal_turn()
        elif self.table.round == Round.RIVER:
            self.table.deal_river()

        self.start_new_round()
        self.status = Status.RUNNING
        return self.status

    # ---- その他ユーティリティ ----

    def get_pending_players(self):
        """まだアクションしてないプレイヤー。"""
        return [
            p for p in self.action_order
            if p.is_active and p.bet_total != self.table.current_bet
        ]

    def log_action(self, player, action, amount):
        """アクションログに記録。"""
        # 実装はあなたにおまかせ
        print(f'{player} -> {action}({amount})')
