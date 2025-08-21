from models.game_state import GameState
from models.enum import Action, PlayerState

class ActionService:
    """プレイヤーのアクションを処理するサービス"""

    def handle_player_action(
        self, 
        game_state: GameState, 
        player_index: int, 
        action: Action, 
        amount: int = 0
    ) -> GameState:
        """プレイヤーのアクションを処理し、ゲーム状態を更新する"""
        
        if game_state.current_player_index != player_index:
            raise ValueError("It is not this player's turn.")

        player_seat = game_state.table.seats[player_index]
        player = player_seat.player
        
        # アクションの処理 (主要なロジックはここに記述)
        if action == Action.FOLD:
            player_seat.state = PlayerState.FOLDED

        elif action == Action.CALL:
            # 現在のラウンドでの最高ベット額を計算
            max_bet = max(s.bet_total for s in game_state.table.seats)
            call_amount = max_bet - player_seat.bet_total
            
            # all-inの場合
            if call_amount >= player.stack:
                player_seat.bet_total += player.stack
                player.stack = 0
                player.state = PlayerState.ALL_IN
            else:
                player.stack -= call_amount
                player_seat.bet_total += call_amount
                player.state = PlayerState.ACTED

        # ... BET, RAISEなどのロジックも同様に実装 ...

        # 次のアクションプレイヤーを決定するロジック
        next_player_index = self._find_next_active_player(game_state, player_index)
        
        # 全員のアクションが完了したかチェック -> ラウンド進行
        if self._is_betting_round_over(game_state):
             # game_service を呼び出してラウンドを次に進める
             pass
        else:
            game_state.current_player_index = next_player_index
            
        return game_state

    def _find_next_active_player(self, game_state: GameState, current_index: int) -> int:
        """次のアクション可能なプレイヤーのインデックスを見つける"""
        num_players = len(game_state.table.seats)
        for i in range(1, num_players + 1):
            next_index = (current_index + i) % num_players
            player = game_state.table.seats[next_index].player
            if player and player.state in [PlayerState.ACTIVE, PlayerState.ACTED]: # 要調整
                return next_index
        return -1 # エラーまたはハンド終了

    def _is_betting_round_over(self, game_state: GameState) -> bool:
        """ベッティングラウンドが終了したか判定する"""
        # ここにラウンド終了条件を記述
        # (例: 全員が同じ額をベットしたか、フォールド/オールイン以外が1人になった)
        return False # 仮