# services/player_service.py
from models.game_state import GameState
from models.enum import Action, PlayerState
# from exceptions import InvalidActionException # 必要に応じてカスタム例外を定義

class PlayerService:
    """プレイヤーのアクションを処理するサービス"""

    def take_action(self, game_state: GameState, action: Action, amount: int = 0) -> None:
        """
        現在のアクティブプレイヤーのアクションを実行し、ゲーム状態を更新します。
        """
        # NOTE: アクションの妥当性検証ロジックが必須です。
        # self._validate_action(game_state, action, amount)
        
        player_seat = game_state.table.seats[game_state.current_player_index]

        if action == Action.FOLD:
            player_seat.state = PlayerState.FOLDED
        elif action == Action.CHECK:
            # ベット額の変更なし
            pass
        # TODO: CALL, BET, RAISE, ALL_IN のロジックを実装
        # スタックの増減、ベット額の更新など
        
        player_seat.acted = True