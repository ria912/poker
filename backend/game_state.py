# backend/game_state.py
from typing import List, Optional

from backend.models.table import Table
from backend.models.player import Player
from backend.services.dealer import Dealer
from backend.models.position_manager import PositionManager
from backend.models.enum import Round

class GameState:
    """
    ゲーム全体の状態を管理するクラス。
    テーブル、プレイヤー、ディーラーなどの主要なオブジェクトを保持し、
    ゲームの進行状況を一元的に管理します。
    """
    def __init__(self, max_seats: int = 6):
        self.table = Table(max_seats=max_seats)
        # ボタンの初期位置は -1 としておき、最初のハンド開始時に決定します。
        self.position_manager = PositionManager(self.table, button_index=-1)
        self.dealer = Dealer(self.table)
        self.current_round: Round = Round.PREFLOP
        self.active_player_index: Optional[int] = None # 現在アクションを待っているプレイヤーのシートインデックス

    def setup_new_game(self, players: List[Player]):
        """
        新しいゲームを開始するためにプレイヤーを着席させます。
        """
        for i, player in enumerate(players):
            if i < self.table.max_seats:
                self.table.seats[i].sit(player)

        # 最初のボタン位置を決定します。
        # ここでは、最初に座ったプレイヤーをボタンとします。
        first_player_seat = next((seat for seat in self.table.seats if seat.is_occupied()), None)
        if first_player_seat:
            self.position_manager.button_index = first_player_seat.index
        else:
            # プレイヤーがいない場合はデフォルトで0番目に設定します。
            self.position_manager.button_index = 0

    def start_new_hand(self):
        """
        新しいハンドを開始します。
        ハンドごとのリセット、ポジション割り当て、カード配布、ブラインド徴収を行います。
        """
        # アクティブなプレイヤーが2人未満の場合はハンドを開始できません。
        if len(self.table.get_active_seats()) < 2:
            print("プレイヤーが2人未満のため、ハンドを開始できません。")
            return

        self.table.reset_hand()
        self.dealer.deck.reset()

        # ボタンを次のアクティブなプレイヤーに移動します。
        self.position_manager.rotate_button()
        
        # 新しいボタン位置に基づいてポジションを割り当てます。
        self.position_manager.assign_positions()

        # 全員にホールカードを配ります。
        self.dealer.deal_hole_cards()

        # SBとBBがブラインドを支払います。
        self.dealer.post_blinds()

        # ラウンドをプリフロップに設定します。
        self.current_round = Round.PREFLOP

    def get_game_view(self) -> dict:
        """
        フロントエンドやデバッグ用に、現在のゲーム状態を辞書形式で返します。
        """
        seats_info = []
        for seat in self.table.seats:
            if seat.is_occupied():
                player = seat.player
                seats_info.append({
                    "index": seat.index,
                    "player_name": player.name,
                    "stack": player.stack,
                    "position": player.position.name if player.position else None,
                    "bet_total": player.bet_total,
                    "is_folded": player.folded,
                    "last_action": player.last_action.name if player.last_action else None,
                    "hole_cards": player.hole_cards # テスト用に公開
                })
            else:
                seats_info.append({"index": seat.index, "player_name": None})

        return {
            "board": self.table.board,
            "pot": self.table.pot,
            "current_bet": self.table.current_bet,
            "min_bet": self.table.min_bet,
            "current_round": self.current_round.name,
            "active_player_index": self.active_player_index,
            "button_index": self.position_manager.button_index,
            "seats": seats_info
        }