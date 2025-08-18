# app/services/table_service.py
from typing import List
from models import GameState, Player, Position, PlayerState, Seat

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
        active_players = self.table.active_players
        if len(active_players) < 2:
            raise ValueError("プレイヤーが2人未満のため、ゲームを開始できません")

        # ハンド、ボード、ポット、デッキをリセット
        self.table.reset_hand()
        self.table.deck.shuffle()

        # ディーラーボタンを決定または移動
        if self.game_state.dealer_index is None:
            self.game_state.dealer_index = 0
        else:
            self.game_state.dealer_index = (self.game_state.dealer_index + 1) % len(self.table.seats)

        # ポジションの割り当て
        positions = get_positions(len(active_players), self.game_state.dealer_index)
        for i, player in enumerate(active_players):
            player.position = positions[i]

        # SBとBBからブラインドを強制ベットさせる
        self._post_blinds(active_players)
        
        # 全員にカードを配る
        for seat in self.table.seats:
            if seat.player and seat.player.state != PlayerState.OUT:
                self.table.deal_to_player(seat)
    
    def _post_blinds(self, players: List[Player]):
        """スモールブラインドとビッグブラインドを支払わせる"""
        sb_player = next((p for p in players if p.position == Position.SB), None)
        bb_player = next((p for p in players if p.position == Position.BB), None)

        # 2人プレイ（ヘッズアップ）の場合の特別処理
        if len(players) == 2:
            dealer_player = players[self.game_state.dealer_index]
            other_player = players[(self.game_state.dealer_index + 1) % 2]
            sb_player = dealer_player # ディーラーがSB
            bb_player = other_player
            # ポジションも修正
            dealer_player.position = Position.SB
            other_player.position = Position.BB

        if sb_player:
            seat = self._find_seat_by_player(sb_player)
            seat.place_bet(self.game_state.small_blind)
        
        if bb_player:
            seat = self._find_seat_by_player(bb_player)
            seat.place_bet(self.game_state.big_blind)