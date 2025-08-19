# app/services/game_service.py
from typing import Optional, List
from app.models.game_state import GameState
from app.models.enum import Round, State, PlayerState
from app.services.player_service import PlayerService
from app.services.table_service import TableService


class GameService:
    """
    ゲーム全体の進行を管理するサービス
    - ハンド開始
    - ラウンド遷移
    - 勝者判定
    """

    def __init__(self):
        self.player_service = PlayerService()
        self.table_service = TableService()

    # -------------------------
    # ゲーム進行
    # -------------------------

    def start_new_hand(self, game_state: GameState, small_blind: int = 50, big_blind: int = 100) -> None:
        """新しいハンドを開始"""
        table = game_state.table
        table.reset_for_new_hand()

        # ディーラーを進める
        game_state.dealer_index = (game_state.dealer_index + 1) % len(table.seats)

        # ブラインド徴収
        self.table_service.collect_blinds(table, small_blind, big_blind, game_state.dealer_index)

        # 配札
        self.table_service.deal_hole_cards(table)

        # 状態更新
        game_state.round = Round.PREFLOP
        game_state.state = State.IN_PROGRESS
        game_state.current_player_index = (game_state.dealer_index + 3) % len(table.seats)

    def proceed_to_next_round(self, game_state: GameState) -> None:
        """次のラウンドに進行"""
        table = game_state.table

        # ベットをポットに移す
        self.table_service.settle_bets_to_pot(table)

        # ラウンド進行
        if game_state.round == Round.PREFLOP:
            self.table_service.deal_community_cards(table, 3)  # フロップ
        elif game_state.round == Round.FLOP:
            self.table_service.deal_community_cards(table, 1)  # ターン
        elif game_state.round == Round.TURN:
            self.table_service.deal_community_cards(table, 1)  # リバー
        elif game_state.round == Round.RIVER:
            self.determine_winner(game_state)  # ショーダウン
            return

        # 次のラウンドへ
        game_state.round = game_state.round.next()
        game_state.current_player_index = (game_state.dealer_index + 1) % len(table.seats)

    # -------------------------
    # 勝者判定
    # -------------------------

    def determine_winner(self, game_state: GameState) -> None:
        """勝者を決定する"""
        table = game_state.table
        winners = table.determine_winner()

        # 勝者にポットを分配
        if winners:
            reward = table.pot // len(winners)
            for seat in winners:
                if seat.player:
                    seat.player.stack += reward

        # 状態更新
        game_state.state = State.FINISHED
        table.pot = 0

    # -------------------------
    # ターン管理
    # -------------------------

    def next_player(self, game_state: GameState) -> Optional[int]:
        """次のプレイヤーにターンを回す"""
        from app.utils.order_utils import get_next_player_index

        next_index = get_next_player_index(game_state, game_state.current_player_index)
        game_state.current_player_index = next_index
        return next_index