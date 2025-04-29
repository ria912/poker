from action import Action
from collections import deque

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.players = [p for p in table.players if not p.has_folded and not p.has_left]
        self.action_queue = deque()
        self.phase = 'preflop'
        self.community_index = 0  # 0: flop, 1: turn, 2: river

    def start_round(self):
        self.update_action_order()
        self.run_phase_loop()

    def update_action_order(self):
        """
        現在のフェーズとポジションに応じて行動順を設定
        """
        if self.phase == 'preflop':
            # プリフロップはBBの次から開始
            bb_index = next((i for i, p in enumerate(self.players) if p.position == 'BB'), 0)
            start_index = (bb_index + 1) % len(self.players)
        else:
            # フロップ以降はSBの次から
            sb_index = next((i for i, p in enumerate(self.players) if p.position == 'SB'), 0)
            start_index = (sb_index + 1) % len(self.players)

        self.action_queue = deque(self.players[start_index:] + self.players[:start_index])

    def run_phase_loop(self):
        """
        各フェーズ内のアクションループ（全員のアクションが終了するまで）
        """
        while True:
            player = self.action_queue.popleft()

            if player.has_folded or player.stack == 0:
                continue  # 行動できないプレイヤーはスキップ

            legal_actions = Action.get_legal_actions(player, self.table)
            action, amount = player.decide_action(legal_actions)  # AIまたはUI入力
            Action.apply_action(player, action, self.table, amount)

            self.print_action(player, action, amount)

            if self.all_players_have_acted():
                break
            else:
                self.action_queue.append(player)

        self.advance_phase()

    def all_players_have_acted(self):
        """
        全員が同額を出すか、フォールド済みかチェック
        """
        active = [p for p in self.players if not p.has_folded and p.stack > 0]
        if len(active) <= 1:
            return True  # 残り1人

        highest_bet = max(p.current_bet for p in active)
        return all(p.current_bet == highest_bet for p in active)

    def advance_phase(self):
        """
        次のフェーズへ移行（カード公開とベットリセット）
        """
        self.table.current_bet = 0
        for p in self.table.players:
            p.current_bet = 0

        if self.phase == 'preflop':
            self.deal_community_cards(3)
            self.phase = 'flop'
        elif self.phase == 'flop':
            self.deal_community_cards(1)
            self.phase = 'turn'
        elif self.phase == 'turn':
            self.deal_community_cards(1)
            self.phase = 'river'
        elif self.phase == 'river':
            self.phase = 'showdown'
            return

        self.update_action_order()
        self.run_phase_loop()

    def deal_community_cards(self, count):
        for _ in range(count):
            card = self.table.deck.draw()
            self.table.community_cards.append(card)

    def print_action(self, player, action, amount):
        print(f"{player.name} -> {action} ({amount})")
