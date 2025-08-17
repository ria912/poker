# services/game_service.py
from models.game_state import GameState
from models.enum import Round, GameStatus, PlayerState
from models.table import Seat
from typing import Optional


class GameService:
    """
    ゲーム全体を統括するサービス
    - ハンド開始（ブラインド、カード配布、最初のアクション設定）
    - ラウンド進行
    - ハンド終了（勝者判定、チップ移動）
    """

    def __init__(self, game_state: GameState):
        self.state = game_state

    def start_hand(self):
        """
        ハンド開始処理
        - ディーラー移動
        - ブラインド強制ベット
        - カード配布
        - 最初のアクションプレイヤーを設定
        """
        table = self.state.table

        # デッキをシャッフル
        table.deck.shuffle()

        # ディーラー位置を決定
        if self.state.dealer_index is None:
            self.state.dealer_index = 0
        else:
            self.state.dealer_index = (self.state.dealer_index + 1) % len(table.seats)

        # SB, BB を決定
        sb_index = (self.state.dealer_index + 1) % len(table.seats)
        bb_index = (self.state.dealer_index + 2) % len(table.seats)

        sb_seat = table.seats[sb_index]
        bb_seat = table.seats[bb_index]

        if sb_seat.player:
            sb_seat.place_bet(self.state.small_blind)
        if bb_seat.player:
            bb_seat.place_bet(self.state.big_blind)

        # 各プレイヤーにカードを配る
        for seat in table.seats:
            if seat.player:
                table.deal_to_player(seat)

        # アクションプレイヤー（BBの次からスタート）
        self.state.current_player_index = (bb_index + 1) % len(table.seats)

        self.state.round = Round.PREFLOP
        self.state.state = GameStatus.RUNNING

    def proceed_round(self):
        """
        ラウンド進行
        - コミュニティカード配布
        - ラウンド遷移
        """
        table = self.state.table

        if self.state.round == Round.PREFLOP:
            table.deal_to_board(3)  # FLOP
            self.state.round = Round.FLOP
        elif self.state.round == Round.FLOP:
            table.deal_to_board(1)  # TURN
            self.state.round = Round.TURN
        elif self.state.round == Round.TURN:
            table.deal_to_board(1)  # RIVER
            self.state.round = Round.RIVER
        elif self.state.round == Round.RIVER:
            self.state.round = Round.SHOWDOWN
            self.state.state = GameStatus.SHOWDOWN

    def end_hand(self) -> Optional[str]:
        """
        ハンド終了処理
        - 勝者判定
        - ポット配分
        - 次ハンド準備
        """
        table = self.state.table

        winner_id = table.determine_winner()
        if winner_id:
            # 勝者にポットを渡す
            for seat in table.seats:
                if seat.player and seat.player.player_id == winner_id:
                    seat.player.stack += table.pot
                    break

        # 次ハンド準備
        for seat in table.seats:
            if seat.player:
                seat.player.reset_for_new_hand()
        table.board.clear()
        table.pot = 0
        table.deck.reset()

        self.state.state = GameStatus.GAME_OVER
        return winner_id