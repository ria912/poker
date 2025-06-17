# backend/models/round.py
from typing import List, Optional
from backend.models.table import Table
from backend.models.player import Player
from backend.models.enum import Round, Status, Position

class RoundLogic:
    """ラウンドの状態管理も行います。"""

    def __init__(self, table: Table):
        self.table = table
        self.round = self.table.round
        self.status = Status.ROUND_CONTINUE

    def advance_round(self):
        """次のベットラウンドに移行します。 showdown時にラウンド完了。"""
        next_round = Round.next(self.table.round)
        if next_round == Round.SHOWDOWN:
            self.table.round = Round.SHOWDOWN
            self.status = Status.ROUND_OVER
        else:
            self.table.round = next_round
            self.table.reset()
            self.status = Status.ROUND_CONTINUE

            if self.table.round == Round.FLOP:
                self.table.deck.deal_flop()
            elif self.table.round == Round.TURN:
                self.table.deck.deal_turn()
            elif self.table.round == Round.RIVER:
                self.table.deck.deal_river()


class RoundManager:
    """アクション管理も行うRound Manager。"""

    def __init__(self, table: Table):
        self.table = table
        self.round_logic = RoundLogic(table)
        self.active_players = self.table.get_active_players()

        self.action_order: List[Player] = self.get_action_order()
        self.action_index = 0
    
    def reset(self):
        """ラウンド開始時に呼び出して状態をリセット。"""
        self.round_logic = RoundLogic(self.table)
        self.action_order = self.get_action_order()
        self.action_index = 0

    def get_action_order(self) -> List[Player]:
        # is_active かつ has_acted == False のプレイヤーを取得
        active_unacted_players = [
            p for p in self.table.get_active_players() if not p.has_acted
        ]
        # ASSIGN_ORDER順にソート
        sorted_order = sorted(
            active_unacted_players,
            key=lambda p: Position.ASSIGN_ORDER.index(p.position)
            if p.position in Position.ASSIGN_ORDER else 999
        )
        self.action_index = 0

        if self.table.round == Round.PREFLOP and not self.action_order:
            # BBの次からアクション開始（ASSIGN_ORDER内でのBBの次）
            try:
                bb_index = next(
                    i for i, p in enumerate(sorted_order) if p.position == Position.BB
                )
                # BBの次（UTG）スタートに並べ直して返す
                self.action_order = sorted_order[bb_index + 1:] + sorted_order[:bb_index + 1]
            except Exception as e:
                raise RuntimeError(f"bb_indexを取得できません。: {e}")
        # ポストフロップ,None以外はそのまま返す
        self.action_order = sorted_order

    def get_next_player(self) -> Optional[Player]:
        """次にアクションすべきプレイヤーを取得。全員完了時に帰 None。"""
        while self.action_index < len(self.action_order):
            player = self.action_order[self.action_index]
            if not player.has_acted:
                return player
            self.action_index += 1
        
        return None

    def reset_actions(self):
        """プレイヤーのアクション状態もリセット。次のラウンドに備えて。"""
        for player in self.active_players:
            player.has_acted = False
        self.active_players = self.table.get_active_players()
        self.action_index = 0

    def is_round_complete(self) -> bool:
        """現在のベット額に対して全プレイヤーがアクション済みならTRUE。"""
        for player in self.table.get_active_players():
            if not player.has_acted or player.bet_total < self.table.current_bet:
                return Status.ROUND_CONTINUE
        return Status.ROUND_OVER

    def proceed(self):
        """次のプレイヤーにアクションしてもらう。完了時に次のラウンドに移行。"""
        if self.is_round_complete():
            self.round_logic.advance_round()
            self.reset_actions()
            return

        player = self.get_next_player()
        if player is not None:
            # ここにプレイヤーにアクションしてもらうロジック
            # 例:
            # player.act()
            player.has_acted = True
            self.action_index += 1