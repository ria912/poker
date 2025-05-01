# round_manager.py

from models.action import Action

class RoundManager:
    def __init__(self, table):
        self.table = table
        self.players = [p for p in table.players if not p.has_left]
        self.active_players = [p for p in self.players if not p.has_folded and p.stack > 0]
        self.phase = 'preflop'

    def play_round(self):
        """
        ラウンド全体を順に進行（プリフロップ→リバーまで）
        """
        self.betting_round()
        if self.is_hand_over():
            return

        self.deal_community_cards(3)  # フロップ
        self.betting_round()
        if self.is_hand_over():
            return

        self.deal_community_cards(1)  # ターン
        self.betting_round()
        if self.is_hand_over():
            return

        self.deal_community_cards(1)  # リバー
        self.betting_round()
        # ショーダウン処理は未実装

    def betting_round(self):
        """
        1フェーズ内のベッティングラウンドを実行
        """
        self.reset_current_bets()
        players_in_round = [p for p in self.players if not p.has_folded and p.stack > 0]
        idx = self.get_first_to_act_index()

        num_players = len(players_in_round)
        acted = set()
        while True:
            player = players_in_round[idx]

            # AI or Human の処理
            if player.is_human:
                legal = Action.get_legal_actions(player, self.table)
                print(f"\n{player.name}'s turn. Stack: {player.stack}")
                print("Community Cards:", self.table.community_cards)
                print("Your Hand:", player.hand)
                print("Pot:", self.table.pot)
                print("Legal Actions:", legal['actions'])
                action = input("Choose action: ").strip().lower()
                amount = 0
                if action in [Action.BET, Action.RAISE]:
                    amount = int(input("Enter amount: "))
                Action.apply_action(player, action, self.table, amount)
            else:
                action, amount = player.decide_action(self.table)
                Action.apply_action(player, action, self.table, amount)
                print(f"{player.name} chooses {action} ({amount if amount else ''})")

            acted.add(player)
            idx = (idx + 1) % num_players

            # アクションが終わる条件：すべてのプレイヤーが同額ベットか、フォールド済み
            if self.betting_complete(players_in_round, acted):
                break

    def get_first_to_act_index(self):
        """
        プリフロップ：BBの左
        以降：SBの左
        """
        positions = [p.position for p in self.players]
        if self.phase == 'preflop':
            try:
                bb_index = positions.index('BB')
                return (bb_index + 1) % len(self.players)
            except ValueError:
                return 0
        else:
            try:
                sb_index = positions.index('SB')
                return (sb_index + 1) % len(self.players)
            except ValueError:
                return 0

    def reset_current_bets(self):
        """
        各プレイヤーのベット状態をリセット（次フェーズのため）
        """
        self.table.current_bet = 0
        self.table.min_bet = self.table.big_blind
        for player in self.players:
            player.current_bet = 0

    def betting_complete(self, players, acted):
        """
        全員が同じ額までコール or オールイン or フォールドしているかどうか
        """
        active = [p for p in players if not p.has_folded and p.stack > 0]
        if len(active) <= 1:
            return True
        target_bet = max(p.current_bet for p in active)
        return all(p.current_bet == target_bet or p.stack == 0 for p in active)

    def deal_community_cards(self, count):
        for _ in range(count):
            self.table.community_cards.append(self.table.deck.draw())
        # 次のフェーズへ
        if count == 3:
            self.phase = 'flop'
        elif self.phase == 'flop':
            self.phase = 'turn'
        elif self.phase == 'turn':
            self.phase = 'river'

    def is_hand_over(self):
        remaining = [p for p in self.players if not p.has_folded]
        return len(remaining) <= 1
    