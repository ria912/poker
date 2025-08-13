from typing import Optional

# modelsから必要なクラスとEnumをインポートします
from models import (
    GameState,
    Player,
    Action,
    PlayerState,
    GameStatus,
    game_state,  # グローバルなゲーム状態インスタンス
)
# 循環参照を避けるため、サービスは関数内でインポートすることがあります
# from services.game.game_service import game_service

class ActionManager:
    """
    プレイヤーのアクション（ベット、コール、フォールドなど）を処理するサービスクラス。
    """
    def __init__(self, state: GameState):
        self.game_state = state

    def handle_action(self, player_id: str, action: Action, amount: int = 0):
        """
        プレイヤーからのアクションを受け取り、適切な処理を呼び出すメインのメソッド。
        """
        player = self.game_state.table.get_player_by_id(player_id)
        if not player or player.player_id != self.game_state.active_player_id:
            raise ValueError("It's not your turn.")
        
        # 最高ベット額（コールに必要な額）を取得
        highest_bet = max(p.current_bet for p in self.game_state.players)

        print(f"\n[{player.name}] のアクション: {action.value}, 金額: {amount}")

        # アクションの種類に応じて処理を分岐
        if action == Action.FOLD:
            self._handle_fold(player)
        elif action == Action.CHECK:
            self._handle_check(player, highest_bet)
        elif action == Action.CALL:
            self._handle_call(player, highest_bet)
        elif action == Action.BET:
            self._handle_bet(player, amount, highest_bet)
        elif action == Action.RAISE:
            self._handle_raise(player, amount, highest_bet)
        
        # アクション後に、ラウンドが終了したか、次のプレイヤーに移るかを決定する
        self._check_round_end_or_move_to_next_player()

    def _handle_fold(self, player: Player):
        """フォールド処理"""
        player.state = PlayerState.FOLDED
        print(f"{player.name} がフォールドしました。")

    def _handle_check(self, player: Player, highest_bet: int):
        """チェック処理"""
        if player.current_bet < highest_bet:
            raise ValueError("Cannot check, a bet has been made.")
        print(f"{player.name} がチェックしました。")

    def _handle_call(self, player: Player, highest_bet: int):
        """コール処理"""
        call_amount = highest_bet - player.current_bet
        if call_amount <= 0:
            raise ValueError("No bet to call.") # or can be treated as check
        
        # スタックが足りなければオールイン
        if player.stack <= call_amount:
            call_amount = player.stack
            player.state = PlayerState.ALL_IN
            print(f"{player.name} がオールインしました。")

        player.stack -= call_amount
        player.current_bet += call_amount
        self.game_state.table.pot += call_amount
        print(f"{player.name} が {call_amount} をコールしました。")

    def _handle_bet(self, player: Player, amount: int, highest_bet: int):
        """ベット処理"""
        if highest_bet > 0:
            raise ValueError("Cannot bet, use raise instead.")
        if amount <= 0:
            raise ValueError("Bet amount must be positive.")
        
        if player.stack <= amount:
            amount = player.stack
            player.state = PlayerState.ALL_IN
            print(f"{player.name} がオールインしました。")

        player.stack -= amount
        player.current_bet = amount
        self.game_state.table.pot += amount
        print(f"{player.name} が {amount} をベットしました。")

    def _handle_raise(self, player: Player, amount: int, highest_bet: int):
        """レイズ処理"""
        if highest_bet == 0:
            raise ValueError("Cannot raise, use bet instead.")
        
        # レイズ額は最低でも前のベット額との差額以上であるべき（ミニマムレイズの考慮）
        min_raise_amount = highest_bet * 2
        if amount < min_raise_amount:
            raise ValueError(f"Raise amount must be at least {min_raise_amount}.")
            
        if player.stack <= amount - player.current_bet:
            amount = player.stack + player.current_bet
            player.state = PlayerState.ALL_IN
            print(f"{player.name} がオールインしました。")

        required_payment = amount - player.current_bet
        player.stack -= required_payment
        player.current_bet = amount
        self.game_state.table.pot += required_payment
        print(f"{player.name} が {amount} にレイズしました。")

    def _check_round_end_or_move_to_next_player(self):
        """
        ラウンドが終了したかを確認し、終了していなければ次のプレイヤーにアクションを移す。
        非常に重要なロジック。
        """
        active_players = [p for p in self.game_state.players if p.state == PlayerState.ACTIVE]
        
        # アクティブなプレイヤーが1人しかいなければ、その人がポットを獲得してハンド終了
        if len(active_players) <= 1 and len([p for p in self.game_state.players if p.state != PlayerState.FOLDED]) <=1:
            self.game_state.game_status = GameStatus.GAME_OVER
            print("ハンドが終了しました。")
            # ここでポット獲得処理を呼び出す
            return

        # 全員のアクションが終わったか（ベット額が揃ったか）を確認
        highest_bet = max(p.current_bet for p in self.game_state.players if p.state != PlayerState.FOLDED)
        
        # オールインでないアクティブプレイヤー全員が最高ベット額に達しているか
        is_round_over = all(
            p.current_bet == highest_bet for p in active_players
        )

        if is_round_over:
            self.game_state.game_status = GameStatus.ROUND_OVER
            print(f"--- ベッティングラウンド終了 --- ポット: {self.game_state.table.pot} ---")
            # この後、game_service.advance_to_next_round() が呼び出される
            return
        
        # ラウンドが継続する場合、次のプレイヤーを探す
        current_player_id = self.game_state.active_player_id
        current_seat_index = next(s.seat_index for s in self.game_state.table.seats if s.player and s.player.player_id == current_player_id)
        
        for i in range(1, self.game_state.table.seat_count + 1):
            next_seat_index = (current_seat_index + i) % self.game_state.table.seat_count
            next_seat = self.game_state.table.seats[next_seat_index]
            
            # 次のプレイヤーは「アクティブ」状態でなければならない
            if next_seat.is_occupied and next_seat.player.state == PlayerState.ACTIVE:
                self.game_state.active_player_id = next_seat.player.player_id
                print(f"次のアクションは {next_seat.player.name} です。")
                return

# シングルトンとしてサービスインスタンスを作成
action_manager = ActionManager(game_state)