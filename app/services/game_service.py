# app/services/game_service.py
from app.models.game_state import GameState
from app.models.enum import GameStatus, Round, PlayerState
from app.services.player_service import PlayerService
from app.services.table_service import TableService


class GameService:
    """ゲーム全体の進行を管理するサービス"""

    @staticmethod
    def start_new_hand(game_state: GameState):
        """新しいハンドを開始"""
        TableService.reset_table(game_state.table)
        game_state.deck.reset_and_shuffle()

        # 各プレイヤーに2枚配る
        for seat in game_state.table.seats:
            if seat.is_occupied:
                # Deckモデルのdealメソッドを利用
                seat.player.hand = game_state.deck.deal(2)
                seat.player.state = PlayerState.ACTIVE

        game_state.current_round = Round.PREFLOP
        game_state.game_status = GameStatus.ROUND_CONTINUE

    @staticmethod
    def next_round(game_state: GameState):
        """次のラウンドに進行"""
        TableService.advance_round(game_state.table)

        # ラウンドごとにコミュニティカードを配る
        if game_state.table.current_round == Round.FLOP:
            game_state.table.community_cards.extend(game_state.deck.deal(3))
        elif game_state.table.current_round in (Round.TURN, Round.RIVER):
            game_state.table.community_cards.extend(game_state.deck.deal(1))

        if game_state.table.current_round == Round.SHOWDOWN:
            game_state.game_status = GameStatus.ROUND_OVER

    @staticmethod
    def is_hand_over(game_state: GameState) -> bool:
        """残り1人 or SHOWDOWNならハンド終了"""
        active_players = [p for p in game_state.players if p.state == PlayerState.ACTIVE]
        return len(active_players) <= 1 or game_state.table.current_round == Round.SHOWDOWN
