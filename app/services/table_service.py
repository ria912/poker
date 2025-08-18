# app/services/table_service.py
from typing import List
from models import GameState, Player, Position, PlayerState, Seat
from utils.order_utils import get_next_active_index

class TableService:
    """テーブル操作に関連するビジネスロジック"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.table = game_state.table

    def add_player(self, name: str, stack: int) -> Player:
        """新しいプレイヤーを作成し、空いている席に座らせる"""
        if len(self.table.active_players) >= 6: # max_players
            raise ValueError("テーブルは満席です")

        new_player = Player(name=name, stack=stack)
        
        # 空いている席を探す
        for seat in self.table.seats:
            if not seat.is_occupied():
                seat.sit(new_player)
                return new_player
        
        raise ValueError("空いている席がありません")

    def remove_player(self, player_id: str) -> None:
        """指定されたプレイヤーをテーブルから退席させる"""
        for seat in self.table.seats:
            if seat.player and seat.player.player_id == player_id:
                seat.leave()
                return
        raise ValueError("指定されたプレイヤーは見つかりません")

    def shuffle_and_deal(self) -> None:
        """新しいハンドの準備を行う"""
        
        # プレイヤーが2人未満の場合は開始しない
        active_seats = self.table.get_active_seats()
        if len(active_seats) < 2:
            raise ValueError("プレイヤーが2人未満のため、ゲームを開始できません")

        active_players = [seat.player for seat in active_seats if seat.player.state == PlayerState.ACTIVE]
        # ハンド、ボード、ポット、デッキをリセット
        self.table.reset_hand()
        self.table.deck.shuffle()

        # ディーラーボタンを決定または移動
        if self.game_state.dealer_index is None:
            self.game_state.dealer_index = 0
        else:
            self.game_state.dealer_index = get_next_active_index(self.game_state, self.game_state.dealer_index)
        # ポジションの割り当て
        assign_position(self.game_state)
        
        # SBとBBからブラインドを強制ベットさせる
        self._post_blinds(active_players)
        
        # 全員にカードを配る
        for seat in self.table.seats:
            if seat.player and seat.is_active():
                self.table.deal_to_player(seat)
    
    def _post_blinds(self):
        """スモールブラインドとビッグブラインドを支払わせる"""
        sb_player = next((s.player for s in self.table.get_active_seats() if s.player.position == Position.SB), None)
        bb_player = next((s.player for s in self.table.get_active_seats() if s.player.position == Position.BB), None)

        # 2人プレイ（ヘッズアップ）の場合の特別処理
        if len(self.table.get_active_seats()) == 2:
            dealer_player = self.table.seats[self.game_state.dealer_index]
            other_player = get_next_active_index(self.game_state, self.game_state.dealer_index)
            sb_player = dealer_player # ディーラーがSB
            bb_player = other_player
            # ポジションも修正
            dealer_player.position = Position.SB
            other_player.position = Position.BB

        if sb_player:
            seat = self.table.find_seat_by_player(sb_player)
            seat.place_bet(self.game_state.small_blind)
        
        if bb_player:
            seat = self.table.find_seat_by_player(bb_player)
            seat.place_bet(self.game_state.big_blind)