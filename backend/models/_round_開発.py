from backend.models.table import Table
from backend.models.action import Action
from backend.models.enum import Round, Position, Status

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_order = []  # このラウンドでのアクション順序（毎ラウンド更新）
        self.action_index = 0
        
        self.status = Status.RUNNING

    def start_new_hand(self):
        self.table.reset_for_next_hand()
        self.table.deal_hands()
        self.table._post_blinds()  # ここで投稿
        self.start_new_round()

    def start_new_round(self):
        self.table.reset_for_next_round()
        self.action_order = self.get_action_order()
        self.action_index = 0

    def get_action_order(self):
        # is_active かつ has_acted == False のプレイヤーを取得
        active_unacted_players = [
            p for p in self.table.get_active_players() if not p.has_acted
        ]
        # 位置順にソート
        sorted_players = sorted(
            active_unacted_players,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
            if p.position in Position.ASSIGN_ORDER else 999
        )
        if self.table.round == Round.PREFLOP and not self.action_order:
        # BBの次からアクション開始（ASSIGN_ORDER内でのBBの次）
        try:
            bb_index = next(
                i for i, p in enumerate(sorted_players) if p.position == Position.BB
            )
            # BBの次（UTG）からに並べ直す
            return sorted_players[bb_index + 1:] + sorted_players[:bb_index + 1]
        except StopIteration:
            # BBがいない場合はそのまま
            return sorted_players
        else:
            # ポストフロップはソート順そのまま
            return sorted_players

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
            if self.is_betting_round_over():
                return self.advance_round()
            else:
                self.reset_action_order()
    
        current_player = self.current_player
        if current_player.is_human:
            self.status = Status.WAITING_FOR_HUMAN
            return self.status
        else:
            self.status = Status.WAITING_FOR_AI
            return self.step_apply_action(current_player)

    def step_apply_action(self, current_player=None):
        if current_player is None:
            current_player = self.current_player
        try:
            action, amount = current_player.decide_action(self.table)
        except Exception as e:
            raise RuntimeError(f"アクション取得失敗: {e}")

        Action.apply_action(self.table, current_player, action, amount)
        self.log_action(current_player, action, amount)

        # レイズした場合、他プレイヤーの has_acted をリセット
        if action in [Action.BET, Action.RAISE] and current_player.bet_total == self.table.current_bet:
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
        self.action_order = self.get_action_order()
        self.action_index = 0
    
        # アクションすべきプレイヤーがいない → ラウンド終了
        if not self.action_order:
            self.status = Status.ROUND_OVER
            return self.advance_round()
    
        # アクション継続
        return self.step_one_action()
    