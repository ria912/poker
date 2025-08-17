# services/round_manager.py
from models.enum import Round, GameStatus
from models.game_state import GameState
from utils.order_utils import get_next_player_index, compute_order


class RoundManager:
    """
    ラウンド進行＋プレイヤーターン管理を担当
    - コミュニティカード配布とラウンド遷移
    - current_player_index の管理
    """

    def __init__(self, game_state: GameState):
        self.state = game_state

    # ----------------------------
    # ラウンド進行
    # ----------------------------
    def proceed_round(self):
        """
        ラウンドを進行させる
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
            # 最終ラウンド → ショーダウンへ
            self.state.round = Round.SHOWDOWN
            self.state.state = GameStatus.SHOWDOWN

        # ラウンド開始時に最初のプレイヤーを設定
        self.set_first_player()

    # ----------------------------
    # プレイヤーターン管理
    # ----------------------------
    def set_first_player(self):
        """
        ラウンド開始時の最初のプレイヤーを設定
        - Preflop: BBの次
        - Flop以降: SBの次
        """
        table = self.state.table
        if not table.seats:
            return

        if self.state.round == Round.PREFLOP:
            bb_index = (self.state.dealer_index + 2) % len(table.seats)
            self.state.current_player_index = get_next_player_index(self.state, bb_index)
            table.action_start_index = bb_index  # order計算の基準
        else:
            sb_index = (self.state.dealer_index + 1) % len(table.seats)
            self.state.current_player_index = get_next_player_index(self.state, sb_index)
            table.action_start_index = sb_index

    def next_turn(self):
        """
        現在のプレイヤーから次のプレイヤーへターンを進める
        """
        if self.state.current_player_index is None:
            return None

        next_index = get_next_player_index(self.state, self.state.current_player_index)
        self.state.current_player_index = next_index
        return next_index

    def get_action_order(self):
        """
        このラウンドにおける行動順リストを返す
        """
        return compute_order(self.state)