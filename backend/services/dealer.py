# backend/services/dealer.py

from backend.models.table import Table
from backend.models.enum import Position, Status, Round
from backend.models.player import Player

class Dealer:
    def __init__(self, table: Table):
        self.table = table

    def run_hand(self):
        self.post_blinds()
        self.deal_hole_cards()
        for round_name in [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER]:
            self.table.round = Round(round_name)
            self.run_betting_round()
            if self.table.status == Status.HAND_OVER:
                break
            self.deal_board_cards(round_name)
        self.run_showdown()
        self.award_pot()

    def post_blinds(self):
        """スモール/ビッグブラインドを投稿し、pot, current_bet を更新"""
        for seat in self.table.seats:
            player = seat.player
            if not player:
                continue

            if player.position in (Position.SB, Position.BTN_SB):
                blind = min(self.table.small_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                self.table.pot += blind
                if player.stack == 0:
                    player.has_all_in = True

            elif player.position == Position.BB:
                blind = min(self.table.big_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                player.all_in = player.stack == 0
                self.table.pot += blind
                self.table.current_bet = blind
                self.table.min_bet = blind

    def deal_hole_cards(self):
        self.table.deck.deal_hands(self.table.seats)

    def deal_board_cards(self, round_name):
        ...

    def run_betting_round(self):
        ...

    def run_showdown(self):
        ...

    def award_pot(self):
        ...

class Dealer:
    @staticmethod
    def post_blinds(table: Table):
        """スモール/ビッグブラインドを投稿し、pot, current_bet を更新"""
        for seat in table.seats:
            player = seat.player
            if not player:
                continue

            if player.position in (Position.SB, Position.BTN_SB):
                blind = min(table.small_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                table.pot += blind
                if player.stack == 0:
                    player.has_all_in = True

            elif player.position == Position.BB:
                blind = min(table.big_blind, player.stack)
                player.stack -= blind
                player.bet_total = blind
                player.all_in = player.stack == 0
                table.pot += blind
                table.current_bet = blind
                table.min_bet = blind
                

    @staticmethod
    def deal_hole_cards(table: Table):
        """各プレイヤーに2枚ずつ配布"""
        table.deck.deal_hands(table.seats)

    @staticmethod
    def distribute_pot(table: Table):
        """
        ショーダウン後、勝者にポットを分配する。
        （現在はランダムまたは最初のプレイヤーに渡す仮実装）
        """
        from random import choice

        # アクティブプレイヤーを取得
        active_players = [seat.player for seat in table.get_active_seats() if seat.player]

        if not active_players:
            return Status.ERROR

        # 仮：ランダムな勝者
        winner = choice(active_players)
        winner.stack += table.pot

        # ログに記録（UI表示用に残すなども検討可能）
        table.action_log.append(f"{winner.name} wins the pot of {table.pot}")

        # ポットクリア
        table.pot = 0

        # 次のハンドに備えてラウンドをSHOWDOWNに設定
        return Status.HAND_OVER
