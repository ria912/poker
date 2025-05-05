#models/round_manager.py
from models.action import Action
from models.position import ASSIGNMENT_ORDER


class RoundManager:
    def __init__(self, table):
        self.table = table
        self.stage = 'preflop'  # preflop, flop, turn, river, showdown

    def start_new_hand(self):
        self.table.start_hand()
        self.stage = 'preflop'
        self.run_betting_round()
        if self.more_than_one_active():
            self.proceed_to_next_stage()

    def run_betting_round(self):
        players = self.get_action_order()
        last_raiser = None
        while True:
            action_occurred = False
            for player in players:
                if player.has_folded or player.stack == 0:
                    continue
                if self.only_one_active():
                    return

                # context にステージ情報を追加
                context = Action.get_legal_actions(player, self.table)
                context.update({
                    "stage": self.stage,  # 現在のステージを追加
                    "players": [p.to_dict() for p in self.table.players]  # プレイヤー情報
                })

                if player.is_human:
                    action, amount = player.decide_action(context)
                else:
                    action, amount = player.decide_action(context)

                Action.apply_action(player, action, self.table, amount)

                if action in [Action.BET, Action.RAISE, Action.ALL_IN]:
                    last_raiser = player
                    players = self.reorder_from(player)
                    break  # アクションがあったので再ループ
                action_occurred = True

            if self.betting_round_should_end(last_raiser):
                break

    def proceed_to_next_stage(self):
        for p in self.table.players:
            p.current_bet = 0

        if self.stage == 'preflop':
            self.table.community_cards += [self.table.deck.draw() for _ in range(3)]
            self.stage = 'flop'
        elif self.stage == 'flop':
            self.table.community_cards.append(self.table.deck.draw())
            self.stage = 'turn'
        elif self.stage == 'turn':
            self.table.community_cards.append(self.table.deck.draw())
            self.stage = 'river'
        elif self.stage == 'river':
            self.stage = 'showdown'
            self.showdown()
            return

        self.run_betting_round()
        if self.more_than_one_active() and self.stage != 'showdown':
            self.proceed_to_next_stage()


    def get_action_order(self):
        """現在のステージに応じて正しいアクション順を返す"""
        active_players = [p for p in self.table.players if not p.has_folded]

        if self.stage == 'preflop':
            # BBの次から始まるようにASSIGNMENT_ORDERを回転
            order = self._rotate_assignment_order_from('BB')
        else:
            # BTNの次から始まる
            order = self._rotate_assignment_order_from('BTN')

        # 順番にプレイヤーを取得
        ordered_players = []
        for pos in order:
            for p in active_players:
                if p.position == pos:
                    ordered_players.append(p)
                    break  # 同じポジションが複数いない前提
        return ordered_players

    def _rotate_assignment_order_from(self, position):
        """ASSIGNMENT_ORDERを指定位置の次から時計回りに回転させたリストを返す"""
        idx = ASSIGNMENT_ORDER.index(position)
        return ASSIGNMENT_ORDER[idx+1:] + ASSIGNMENT_ORDER[:idx+1]

    def betting_round_should_end(self, last_raiser):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        if len(active) <= 1:
            return True
        return all(p.current_bet == self.table.current_bet for p in active)

    def only_one_active(self):
        active = [p for p in self.table.players if not p.has_folded and p.stack > 0]
        return len(active) <= 1

    def more_than_one_active(self):
        return not self.only_one_active()

    def showdown(self):
        print("Showdown! (ハンド評価ロジックは未実装)")