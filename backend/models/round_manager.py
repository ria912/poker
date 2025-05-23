# models/round_manager.py
from models.table import Table
from models.position import ACTION_ORDER
from models.action import Action
from models.human_player import WaitingForHumanAction
from models.utils import get_active_players, get_ordered_active_players

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.action_index = 0
        self.action_order = self.get_action_order()
        self.waiting_for_human = False

    def get_action_order(self):
        # アクティブプレイヤーをBTNの次から取得
        players_in_order = get_ordered_active_players(self.table.seats, self.table.btn_index)
        # 
        if self.table.round == 'preflop':
            return players_in_order[2:] + players_in_order[:2]  # BBの次から回す
        return players_in_order

    def _start_betting_round(self):
        self.action_order = self.get_action_order()
        self.action_index = 0
        self.waiting_for_human = False
        for p in self.action_order:
            p.has_acted = False

    def proceed_one_action(self):
        """
        1アクション進行する。
        人間プレイヤーの入力待ちになる場合は Exception を投げる。
        """
        if self.table.round == 'showdown':
            self._showdown()
            return "hand_over"

        if self.is_betting_round_over():
            return self._advance_round()

        if self.action_index >= len(self.action_order):
            if self.is_betting_round_over():
                return self._advance_round()
            else:
                raise RuntimeError("アクションインデックスが範囲外だがラウンドが終了していない")

        current_player = self.action_order[self.action_index]

        try:
            action, amount = current_player.decide_action(self.table)
        except WaitingForHumanAction:
            self.waiting_for_human = True
            raise  # 呼び出し元で "waiting_for_human" を返す
        except Exception:
            raise  # その他の予期しない例外はそのまま投げる

        Action.apply_action(current_player, self.table, action, amount)

        if action in [Action.BET, Action.RAISE]:
            self.table.last_raiser = current_player
            for p in get_active_players(self.table.seats):
                if p != current_player:
                    p.has_acted = False

        self.action_index += 1

        if self.is_betting_round_over():
            return self._advance_round()
        
        return "ai_acted"

    def is_betting_round_over(self):
        active_players = get_active_players(self.table.seats)

        if len(active_players) <= 1:
            return True

        for p in active_players:
            if not p.has_acted or p.current_bet != self.table.current_bet:
                return False

        return True

    def _advance_round(self):
        if self.table.round == 'preflop':
            self.table.round = 'flop'
            self.table.deal_flop()
        elif self.table.round == 'flop':
            self.table.round = 'turn'
            self.table.deal_turn()
        elif self.table.round == 'turn':
            self.table.round = 'river'
            self.table.deal_river()
        elif self.table.round == 'river':
            self.table.round = 'showdown'
            self.table.award_pot_to_winner()
            self.table.is_hand_in_progress = False # 状態反映フラグ
            return "hand_over"

        self._start_betting_round()
        return "round_over"
    
    # 仮置き
    def log_action(self, player, action, amount):
        self.table.action_log.append({
            "player": player.name,
            "action": action,
            "amount": amount,
            "round": self.table.round
    })

    # 人間アクション関連 -----------------------------------

    def resume_after_human_action(self):
        """人間アクションを受け取ったあと再開"""
        self.waiting_for_human = False
        try:
            return self.proceed_one_action()
        except WaitingForHumanAction:
            self.waiting_for_human = True
            return "waiting_for_human"
        except Exception:
            raise