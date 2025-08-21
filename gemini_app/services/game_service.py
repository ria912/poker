from models.game_state import GameState, GameStatus
from models.enum import Action, PlayerState, Round
from services.action_service import ActionService
from typing import Dict, Any, Tuple

class GameService:
    """
    強化学習環境としての役割を担うゲームサービス。
    ゲームの状態を内部で保持し、step関数でゲームを進行させる。
    """
    def __init__(self, initial_game_state: GameState):
        self.game_state = initial_game_state
        self.action_service = ActionService()
        self._initial_stacks = {} # 報酬計算用にハンド開始時のスタックを記録

    def reset(self) -> Dict[str, Any]:
        """新しいハンドを開始し、最初の観測を返す"""
        self._start_new_hand()
        # 最初のプレイヤーのための観測を返す
        return self._make_observation()

    def step(self, action: Action, amount: int = 0) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """
        現在のアクション番のプレイヤーのアクションを適用し、
        (次状態の観測, 報酬, ハンド終了フラグ, 追加情報) を返す
        """
        current_player_index = self.game_state.current_player_index
        
        # 1. アクションを適用し、ゲーム状態を更新
        self.game_state = self.action_service.handle_player_action(
            self.game_state, current_player_index, action, amount
        )

        # 2. ハンドが終了したか判定
        done = self._is_hand_finished()
        
        reward = 0.0
        if done:
            # 3. ハンド終了時、報酬を計算
            reward = self._calculate_reward(current_player_index)
            # (オプション) ここでポットの分配処理などを行う
        
        # 4. 次の状態の観測を作成
        observation = self._make_observation()
        
        # OpenAI Gymのインターフェースに準拠した返り値
        return observation, reward, done, {}

    def _start_new_hand(self):
        """内部的に新しいハンドを開始する"""
        # (前回の回答で示した `start_new_hand` のロジックをここに統合)
        self.game_state.table.reset_for_new_hand()
        # ... ブラインド徴収、カード配布などの処理 ...
        
        # 報酬計算のために、全プレイヤーの初期スタックを記録
        self._initial_stacks = {p.player_id: p.stack for p in self.game_state.players}
        self.game_state.status = GameStatus.IN_PROGRESS

    def _make_observation(self) -> Dict[str, Any]:
        """現在のプレイヤーから見た観測（AIへの入力）を作成する"""
        if self.game_state.status == GameStatus.FINISHED:
            return {"status": "hand_over"}

        player = self.game_state.players[self.game_state.current_player_index]
        observation = {
            "hand": [str(card) for card in player.hand],
            "board": [str(card) for card in self.game_state.table.board],
            "pot": self.game_state.table.pot,
            "my_stack": player.stack,
            "my_bet": self.game_state.table.seats[self.game_state.current_player_index].bet_total,
            "opponent_stacks": [
                p.stack for i, p in enumerate(self.game_state.players) 
                if i != self.game_state.current_player_index
            ],
            # ... その他、ポジション、アクション履歴などAIの判断材料となる情報を追加 ...
        }
        return observation

    def _calculate_reward(self, player_index: int) -> float:
        """指定されたプレイヤーの報酬（スタックの変化量）を計算する"""
        player = self.game_state.players[player_index]
        initial_stack = self._initial_stacks.get(player.player_id, player.stack)
        # ここでポット分配後の最終スタックを取得する必要がある (簡略化)
        final_stack = player.stack # 本来はポット分配後のスタック
        return float(final_stack - initial_stack)

    def _is_hand_finished(self) -> bool:
        """ハンドが終了したかどうかを判定する"""
        active_players = [p for p in self.game_state.players if p.state not in [PlayerState.FOLDED, PlayerState.OUT]]
        
        if len(active_players) <= 1:
            self.game_state.status = GameStatus.FINISHED
            return True
            
        if self.game_state.round == Round.SHOWDOWN and self.action_service._is_betting_round_over(self.game_state):
            self.game_state.status = GameStatus.FINISHED
            return True
            
        return False