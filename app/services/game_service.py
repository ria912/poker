# app/services/game_service.py
from typing import Optional
from app.models.game_state import GameState
from app.models.enum import Action, State, Round
from app.services.player_service import PlayerService
from app.services.table_service import TableService


class GameService:
    """
    ゲーム全体の進行を管理するサービス
    - ハンド開始
    - プレイヤーアクション処理
    - ラウンド進行
    - 勝者判定
    """

    def __init__(self):
        # 他サービスを利用
        self.player_service = PlayerService()
        self.table_service = TableService()

    # -------------------------
    # ハンド開始
    # -------------------------
    def start_hand(self, game: GameState) -> None:
        """
        新しいハンドを開始
        - デッキリセット & 配札
        - ブラインド徴収
        - 最初のアクションプレイヤーを決定
        """
        # ゲーム状態リセット
        game.reset_for_new_hand()

        # ブラインド徴収
        self.table_service.post_blinds(game.table, game.dealer_index)

        # 配札
        self.table_service.deal_hole_cards(game.table)

        # 最初のプレイヤーを設定
        game.current_player_index = self.table_service.get_first_to_act(game.table, game.dealer_index)

        game.state = State.RUNNING
        game.round = Round.PREFLOP

    # -------------------------
    # アクション処理
    # -------------------------
    def proceed_action(self, game: GameState, action: Action, amount: Optional[int] = None) -> None:
        """
        現在のプレイヤーのアクションを処理
        - PlayerService に委譲
        - 次のプレイヤーを決定
        """
        current_player = game.players[game.current_player_index]

        # アクションを処理
        self.player_service.handle_action(current_player, action, amount)

        # 次のプレイヤーへ
        game.current_player_index = self.table_service.get_next_player_index(game)

        # ラウンド終了判定
        if self.table_service.is_round_finished(game):
            self.proceed_round(game)

    # -------------------------
    # ラウンド進行
    # -------------------------
    def proceed_round(self, game: GameState) -> None:
        """
        ラウンドを進める
        - ボードカード公開
        - 次のラウンドへ
        - 次のプレイヤーを決定
        """
        game.round = game.round.next()

        if game.round == Round.FLOP:
            self.table_service.deal_flop(game.table)
        elif game.round == Round.TURN:
            self.table_service.deal_turn(game.table)
        elif game.round == Round.RIVER:
            self.table_service.deal_river(game.table)
        elif game.round == Round.SHOWDOWN:
            self.determine_winner(game)
            return

        # アクション開始プレイヤーを設定
        game.current_player_index = self.table_service.get_first_to_act(game.table, game.dealer_index)

    # -------------------------
    # 勝者判定
    # -------------------------
    def determine_winner(self, game: GameState) -> None:
        """
        ショーダウン → 勝者決定 → ポット配分
        """
        winners = game.table.determine_winner()
        self.table_service.distribute_pot(game.table, winners)
        game.state = State.FINISHED

    # -------------------------
    # ディーラー交代
    # -------------------------
    def next_dealer(self, game: GameState) -> None:
        """次のディーラーを決定"""
        game.dealer_index = self.table_service.get_next_dealer_index(game.table, game.dealer_index)