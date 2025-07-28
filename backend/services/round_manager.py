# backend/services/round_manager.py
from typing import Optional

from backend.game_state import GameState
from backend.models.enum import Round, Position
from backend.models.player import Player
from backend.utils.order_utils import get_next_index

class RoundManager:
    """
    ベッティングラウンドの進行を管理するクラス。
    アクションの順番決定、ラウンド終了判定、次のラウンドへの移行を担当します。
    """
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.table = game_state.table
        # このラウンドで最後に攻撃的なアクション（ベットまたはレイズ）をしたプレイヤーを記録します。
        # これがアクションの終了地点を決定するために重要になります。
        self.last_aggressor: Optional[Player] = None

    def start_betting_round(self):
        """
        新しいベッティングラウンドを開始します。
        ラウンドベット額のリセット、アクション開始プレイヤーの決定を行います。
        """
        self.table.reset_round()
        self.last_aggressor = None

        # アクティブプレイヤーが1人以下の場合は即座にラウンドをスキップ
        if len(self.table.get_active_seats()) <= 1:
            return

        if self.game_state.current_round == Round.PREFLOP:
            # プリフロップでは、BBの次のアクティブプレイヤー(UTG/LJ)からアクションが始まります。
            bb_seat = next((s for s in self.table.seats if s.player and s.player.position == Position.BB), None)
            start_index = get_next_index(self.table.seats, (bb_seat.index + 1) % len(self.table.seats), lambda s: s.is_active())
            
            # プリフロップでは、BBのブラインドベットが最初のベットと見なされるため、
            # アクションを締めくくる基準となるのはBBプレイヤーです。
            self.last_aggressor = bb_seat.player

        else: # フロップ、ターン、リバー
            # ポストフロップでは、ボタンの次のアクティブプレイヤー(SB相当)からアクションが始まります。
            button_index = self.game_state.position_manager.button_index
            start_index = get_next_index(self.table.seats, (button_index + 1) % len(self.table.seats), lambda s: s.is_active())
        
        self.game_state.active_player_index = start_index

    def is_round_over(self) -> bool:
        """
        現在のベッティングラウンドが終了したかどうかを判定します。
        """
        active_seats = [s for s in self.table.get_active_seats() if s.player.stack > 0]

        # アクティブなプレイヤー（オールインを除く）が1人以下ならラウンド終了です。
        if len(active_seats) <= 1:
            return True

        # アクションを締めくくるプレイヤー（last_aggressor）までアクションが戻ってきたか
        current_player = self.table.seats[self.game_state.active_player_index].player
        if self.last_aggressor and current_player == self.last_aggressor:
            return True

        # 全員がチェックして回った場合
        # last_aggressorが設定されておらず、全員がアクション済みならラウンド終了
        if not self.last_aggressor and all(s.player.last_action is not None for s in active_seats):
            return True
            
        return False

    def advance_to_next_player(self):
        """
        次のアクティブなプレイヤーにアクションの順番を移します。
        """
        current_index = self.game_state.active_player_index
        # 現在のプレイヤーの次から見て、フォールドしておらず、オールインでもないプレイヤーを探します。
        next_index = get_next_index(
            self.table.seats,
            (current_index + 1) % len(self.table.seats),
            lambda s: s.is_active() and s.player.stack > 0
        )
        self.game_state.active_player_index = next_index

    def proceed_to_next_round(self):
        """
        現在のラウンドを終了し、次のラウンドに進みます。
        リバーが終わったらショーダウンに進みます。
        """
        current_round_value = self.game_state.current_round.value
        
        # 最終ラウンドより前の場合
        if current_round_value < Round.RIVER.value:
            next_round = Round(current_round_value + 1)
            self.game_state.current_round = next_round
            # コミュニティカードを配ります。
            self.game_state.dealer.deal_community_cards(next_round.name)
            # 次のベッティングラウンドを開始します。
            self.start_betting_round()
        else:
            # リバーが終わったらショーダウンへ
            self.game_state.current_round = Round.SHOWDOWN
            self.game_state.dealer.distribute_pot() # 簡易的なポット分配
            print("ショーダウンに進みます。")