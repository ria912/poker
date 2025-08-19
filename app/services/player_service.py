# app/services/player_service.py
from typing import Optional
from app.models.player import Player
from app.models.enum import Action, PlayerState


class PlayerService:
    """
    プレイヤーのアクションを処理するサービス
    """

    def handle_action(self, player: Player, action: Action, amount: Optional[int] = None) -> None:
        """
        プレイヤーのアクションを処理
        """
        if action == Action.FOLD:
            self.fold(player)
        elif action == Action.CHECK:
            self.check(player)
        elif action == Action.CALL:
            self.call(player)
        elif action == Action.BET:
            if amount is None:
                raise ValueError("BET には金額が必要です")
            self.bet(player, amount)
        elif action == Action.RAISE:
            if amount is None:
                raise ValueError("RAISE には金額が必要です")
            self.raise_bet(player, amount)
        else:
            raise ValueError(f"未対応のアクション: {action}")

    # -------------------------
    # 個別アクション処理
    # -------------------------

    def fold(self, player: Player) -> None:
        """フォールド"""
        player.state = PlayerState.FOLDED

    def check(self, player: Player) -> None:
        """チェック"""
        # チェックは「現在の最大ベット額と同額をすでに出していること」が前提
        # ルール判定は TableService 側で行うのが適切
        player.state = PlayerState.ACTED

    def call(self, player: Player) -> None:
        """コール"""
        # 実際の支払い処理は TableService 側で行うのが自然
        player.state = PlayerState.ACTED

    def bet(self, player: Player, amount: int) -> None:
        """ベット"""
        # プレイヤーからチップを支払わせる
        player.pay(amount)
        player.state = PlayerState.ACTED

    def raise_bet(self, player: Player, amount: int) -> None:
        """レイズ"""
        # ベットと同じだが「現在のベット額より多い」ことを TableService が保証
        player.pay(amount)
        player.state = PlayerState.ACTED