# backend/services/dealer.py
from typing import List
from backend.models.table import Table
from backend.models.player import Player
from backend.models.deck import Deck
from backend.models.enum import Position, Round, State

class Dealer:
    """
    ゲームの物理的な進行（カード配布、ブラインド徴収など）を担当するクラス。
    GameStateやGameServiceからの指示を受けて動作します。
    """
    def __init__(self, table: Table):
        """
        Dealerを初期化します。

        Args:
            table (Table): 管理対象のテーブルオブジェクト。
        """
        self.table = table
        # GameStateからアクセスできるよう、テーブルのデッキへの参照を持つ
        self.deck: Deck = self.table.deck

    def shuffle_deck(self):
        self.deck.reset()

    def post_blinds(self):
        """
        スモールブラインド(SB)とビッグブラインド(BB)をプレイヤーから徴収します。
        このメソッドは、新しいハンドが開始される際にGameStateから呼び出されます。
        """
        # プリフロップではmin_betをBBに設定
        self.table.min_bet = self.table.big_blind

        # SBプレイヤーを探してブラインドを徴収
        sb_seat = next((s for s in self.table.get_active_seats() if s.player.position == Position.SB), None)
        if sb_seat:
            self._post_blind(sb_seat.player, self.table.small_blind)

        # BBプレイヤーを探してブラインドを徴収
        bb_seat = next((s for s in self.table.get_active_seats() if s.player.position == Position.BB), None)
        if bb_seat:
            self._post_blind(bb_seat.player, self.table.big_blind)
            # BBが現在のベット基準額となる
            self.table.current_bet = self.table.big_blind

    def _post_blind(self, player: Player, amount: int):
        """
        指定されたプレイヤーからブラインド額を徴収するヘルパー関数。
        スタックがブラインド額より少ない場合は、オールインとして扱います。
        """
        bet_amount = min(player.stack, amount)
        player.stack -= bet_amount
        player.bet_total = bet_amount
        self.table.add_to_pot(bet_amount)
        if player.stack == 0:
            player.state = State.ALL_IN

    def deal_hole_cards(self):
        """アクティブな各プレイヤーにホールカードを2枚ずつ配ります。"""
        # GameState側でデッキのリセットとシャッフルが行われる想定
        active_players = [seat.player for seat in self.table.get_active_seats() if seat.player.state != State.SITTING_OUT]

        # カードを2周配ります
        for _ in range(2):
            for player in active_players:
                card = self.deck.draw()
                if card is not None:
                    player.hole_cards.append(card)

    def deal_community_cards(self, a_round: Round):
        """
        指定されたラウンドのコミュニティカードをテーブルに配ります。

        Args:
            a_round (Round): 現在のラウンド (FLOP, TURN, RIVER)。
        """
        # 1枚カードを捨て（バーン）、ラウンドに応じた枚数を配ります
        self.deck.draw()
        if a_round == Round.FLOP:
            for _ in range(3):
                card = self.deck.draw()
                if card is not None: self.table.community_cards.append(card)
        elif a_round in [Round.TURN, Round.RIVER]:
            card = self.deck.draw()
            if card is not None: self.table.community_cards.append(card)

    def award_pot(self, winners: List[Player]):
        """
        ポットを勝者に分配します。

        Args:
            winners (List[Player]): 勝者のプレイヤーリスト。
        """
        if not winners:
            return

        share = self.table.pot // len(winners)
        for winner in winners:
            winner.stack += share

        self.table.pot = 0