# app/services/game_service.py
from app.models.game_state import GameState
from app.models.enum import Round, Action, PlayerState
from app.utils.order_utils import get_next_player_index
from app.utils.evaluate_utils import EvaluateUtils

class GameService:
    """ゲーム全体の進行を管理するサービス"""

    def __init__(self, game_state: GameState):
        self.state = game_state

    def start_hand(self):
        """新しいハンドを開始する処理"""
        self.state.table.reset_hand()
        self.state.table.shuffle_and_deal()
        self.state.round = Round.PREFLOP
        self.state.current_seat_index = self.state.table.action_start_index

    def proceed_round(self):
        """ラウンドを進める処理"""
        if self.state.round == Round.PREFLOP:
            self.state.round = Round.FLOP
            self.state.table.deal_community(3)
        elif self.state.round == Round.FLOP:
            self.state.round = Round.TURN
            self.state.table.deal_community(1)
        elif self.state.round == Round.TURN:
            self.state.round = Round.RIVER
            self.state.table.deal_community(1)
        elif self.state.round == Round.RIVER:
            self.state.round = Round.SHOWDOWN

    def next_action_player(self):
        """次にアクションするプレイヤーのインデックスを返す"""
        return get_next_player_index(self.state, self.state.action_index)

    def showdown(self):
        """ショーダウン処理。勝者を返す"""
        players = {
            seat.player.id: seat.player.hand
            for seat in self.state.table.seats
            if seat.is_occupied and seat.player.state != PlayerState.FOLDED
        }
        return EvaluateUtils.compare_hands(players, self.state.table.community_cards)
