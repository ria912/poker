# backend/services/game_manager.py
from backend.models.table import Table
from backend.services.dealer import Dealer
from backend.services.position_manager import PositionManager

class GameManager:
    def __init__(self, table: Table):
        self.table = table
        self.dealer = Dealer(table)
        self.position_manager = PositionManager(table)

    def start_new_hand(self):
        """新しいハンドの準備（ボタン回転、ポジション割当、デッキ準備）"""
        self.position_manager.rotate_button()
        self.position_manager.assign_positions()
        self.dealer.shuffle_deck()

    def preflop(self):
        """プリフロップの処理（ブラインド、ホールカード配布）"""
        self.dealer.post_blinds()
        self.dealer.deal_hole_cards()

    def deal_flop(self):
        """フロップの配布"""
        self.dealer.deal_community_cards("FLOP")

    def deal_turn(self):
        """ターンの配布"""
        self.dealer.deal_community_cards("TURN")

    def deal_river(self):
        """リバーの配布"""
        self.dealer.deal_community_cards("RIVER")

    def showdown(self):
        """ショーダウン処理（簡易版：1人ならポット獲得）"""
        self.dealer.distribute_pot()
