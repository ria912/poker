from backend.models.table import Table
from backend.models.action import ActionManager
from backend.models.enum import Round, Status, Position, Action

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_order = []  # このラウンドでのアクション順序（毎ラウンド更新）
        self.action_index = 0
        self.current_player = None  # 現在のプレイヤー
        
        self.status = Status.RUNNING

    def start_new_hand(self):
        self.table.reset_for_new_hand()
        self.table.deal_hands()
        self.table._post_blinds()
        self.start_new_round()

    def start_new_round(self):
        self.table.reset_for_next_round()
        self.action_order = self.reset_action_order()

    def reset_action_order(self):
        # is_active かつ has_acted == False のプレイヤーを取得
        active_unacted_players = [
            p for p in self.table.get_active_players() if not p.has_acted
        ]
        # ASSIGN_ORDER順にソート
        self.action_order = sorted(
            active_unacted_players,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
            if p.position in Position.ASSIGN_ORDER else 999
        )
        self.action_index = 0
        
        if self.table.round == Round.PREFLOP and not self.action_order:
        # BBの次からアクション開始（ASSIGN_ORDER内でのBBの次）
            try:
                bb_index = next(
                    i for i, p in enumerate(self.action_order) if p.position == Position.BB
                )
                # BBの次（UTG）スタートに並べ直して返す
                self.action_order = self.action_order[bb_index + 1:] + self.action_order[:bb_index + 1]
                return self.action_order
            except Exception as e:
                raise RuntimeError(f"bb_indexを取得できません。: {e}")
        return self.action_order # ポストフロップ,None以外はそのまま返す
        

    def get_pending_players(self):
        """まだアクションが必要なプレイヤーのリスト"""
        return [
            p for p in self.action_order
            if p.is_active and p.bet_total != self.table.current_bet
        ]

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
    
    def step_one_action(self):
        if self.table.round == Round.SHOWDOWN:
            self.status = Status.HAND_OVER
            return self.status
    
        if self.action_index >= len(self.action_order):
            if self.check_next_action_or_end():
                return self.advance_round()
            else:
                self.reset_action_order()

        current_player = self.action_order[self.action_index]
        if current_player.is_human:
            self.status = Status.WAITING_FOR_HUMAN
            return self.status
        else:
            self.status = Status.WAITING_FOR_AI
            return self.step_apply_action(current_player)

    def step_apply_action(self, current_player=None):
        if current_player is None:
            current_player = self.current_player
        action, amount = current_player.decide_action(self.table)
        if action is None or amount is None:
            if current_player.is_human:
                self.status = Status.WAITING_FOR_HUMAN
            else:
                self.status = Status.WAITING_FOR_AI
                return self.status

        Action.apply_action(self.table, current_player, action, amount)
        self.log_action(current_player, action, amount)

        # レイズした場合、他プレイヤーの has_acted をリセット
        if Action.betting_actions() in [Action.BET, Action.RAISE] and current_player.bet_total == self.table.current_bet:
            self.table.last_raiser = current_player
            for p in self.table.seats:
                if p and p.is_active and p != current_player:
                    p.has_acted = False

        self.action_index += 1
        
        if current_player.is_human:
            self.status = Status.HUMAN_ACTED
        else:
            self.status = Status.AI_ACTED
        return self.status

    def check_next_action_or_end(self):
        # アクティブプレイヤーが1人 → ハンド終了
        active_players = [p for p in self.table.seats if p and p.is_active]
        if len(active_players) == 1:
            self.status = Status.HAND_OVER
            return self.status
    
        # アクション順の再取得（has_acted == False な active プレイヤー）
        self.action_order = self.reset_action_order()
        self.action_index = 0
    
        # アクションすべきプレイヤーがいない → ラウンド終了
        if not self.action_order:
            self.status = Status.ROUND_OVER
            return self.advance_round()
    
        # アクション継続
        return self.step_one_action()
    