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
            # Showdownの処理を行う
            self.table.showdown()
            self.table.pot.get_winners() # tableにclass Potを作る？Tableに書く？

        else:
            self.table.round = next_round
            self.table.reset()
            
            if self.table.round == Round.FLOP:
                self.table.deck.deal_flop()
            elif self.table.round == Round.TURN:
                self.table.deck.deal_turn()
            elif self.table.round == Round.RIVER:
                self.table.deck.deal_river()

            self.status = Status.ROUND_CONTINUE


class OrderManager:
    """アクション管理も行うRound Manager。"""

    def __init__(self, table: Table):
        self.table = table
        self.round_logic = RoundLogic(table)
        self.active_players = self.table.get_active_players()

        self.action_order: List[Player] = self.set_action_order()
        self.action_index = 0
    
    def reset(self):
        """ラウンド開始時に呼び出して状態をリセット。"""
        self.active_players = self.table.get_active_players()
        self.action_order = self.set_action_order()
        self.action_index = 0

    def set_action_order(self) -> List[Player]:
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

    def proceed(self):
        """次のプレイヤーにアクションしてもらう。完了時に次のラウンドに移行。"""
        if self.is_round_complete():
            self.round_logic.advance_round()
            self.reset()
            return

        player = self.get_next_player()
        if player is not None:
            # ここにプレイヤーにアクションしてもらうロジック
            # 例:
            # player.act()
            player.has_acted = True
            self.action_index += 1
    
    def is_round_complete(self) -> bool:
        """現在のラウンドが完了しているかを確認。"""
        return all(player.has_acted for player in self.action_order)