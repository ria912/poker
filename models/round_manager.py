from models.action import Action


class RoundManager:
    def __init__(self, table):
        # RoundManagerは1ハンドの流れを管理する
        self.table = table
        self.stage = 'preflop'  # 現在のステージ（プリフロップ〜ショーダウン）

    # 新しいハンドを開始し、プリフロップのベッティングラウンドを実行
    def start_new_hand(self):
        self.table.start_hand()
        self.stage = 'preflop'
        self.run_betting_round()
        if self.more_than_one_active():
            self.proceed_to_next_stage()

    # ベッティングラウンドのロジック（レイズ対応・順番管理含む）
    def run_betting_round(self):
        players = self.table.get_action_order(self.stage)
        last_raiser = None

        while True:
            for player in players:
                if player.has_folded or player.stack == 0:
                    continue
                if self.only_one_active():
                    return

                context = Action.get_legal_actions(player, self.table)
                action, amount = self.get_player_action(player, context)
                Action.apply_action(player, action, self.table, amount)

                print(f"{player.name} -> {action.upper()} {f'({amount})' if amount else ''}")

                if action in [Action.BET, Action.RAISE, Action.ALL_IN]:
                    last_raiser = player
                    players = self.table.reorder_from(player)
                    break  # レイズがあったので順番を再調整して再ループ

            if self.betting_round_should_end(last_raiser):
                break

    # プレイヤーが人間かAIかに応じてアクションを取得（インターフェースを統一）
    def get_player_action(self, player, context):
        if player.is_human:
            return player.decide_action({
                "actions": context,
                "pot": self.table.pot,
                "current_bet": self.table.current_bet,
                "min_bet": self.table.min_bet
            })
        else:
            return player.decide_action(context)

    # 次のステージに進行し、必要なら新たなベッティングラウンドを開始
    def proceed_to_next_stage(self):
        for p in self.table.players:
            p.current_bet = 0

        if self.stage == 'preflop':
            self.table.deal_community_cards(3)  # フロップ
            self.stage = 'flop'
        elif self.stage == 'flop':
            self.table.deal_community_cards(1)  # ターン
            self.stage = 'turn'
        elif self.stage == 'turn':
            self.table.deal_community_cards(1)  # リバー
            self.stage = 'river'
        elif self.stage == 'river':
            self.stage = 'showdown'
            self.showdown()
            return

        self.run_betting_round()
        if self.more_than_one_active() and self.stage != 'showdown':
            self.proceed_to_next_stage()

    # ベッティングラウンドを終了してよいかを判定（全員がコールした場合など）
    def betting_round_should_end(self, last_raiser):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        if len(active) <= 1:
            return True
        return all(p.current_bet == self.table.current_bet for p in active)

    # アクティブなプレイヤーが1人だけか判定（ハンド終了の判定にも使う）
    def only_one_active(self):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        return len(active) <= 1

    # アクティブプレイヤーが2人以上いるか（次フェーズに進むかどうか）
    def more_than_one_active(self):
        return not self.only_one_active()

    # ショーダウン処理（現状は仮実装）
    def showdown(self):
        print("Showdown! (ハンド評価ロジックは未実装)")