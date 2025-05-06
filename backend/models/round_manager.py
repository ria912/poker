# round_manager.py

from models.table import Table
from models.action import get_legal_actions, apply_action
from models.position import rotate_button, assign_positions

class RoundManager:
    def __init__(self, table: Table):
        self.table = table
        self.current_round = "pre_flop"  # 初期ラウンドはプリフロップ
        self.pot = 0  # ポット額の初期化
        self.community_cards = []  # コミュニティカードのリスト
        self.current_bet = 0  # 現在のベット額
        self.active_players = []  # アクティブなプレイヤーリスト

    def start_round(self):
        """ラウンドを開始する処理"""
        self.table.start_hand()
        self.current_round = "pre_flop"
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.active_players = [player for player in self.table.players if player.stack > 0]  # 残っているプレイヤーを選ぶ

        # ボタンとポジションの割り当て
        rotate_button(self.table.players)
        assign_positions(self.table.players)

        # ブラインドを投稿
        self.table.post_blinds()

        # プレイヤーのアクションを決定（プリフロップ）
        self.play_round()

    def play_round(self):
        """各ラウンドごとの進行を管理"""
        if self.current_round == "pre_flop":
            self.deal_community_cards(3)  # フロップ（3枚）を配る
            self.betting_round()
            self.current_round = "post_flop"
        elif self.current_round == "post_flop":
            self.deal_community_cards(1)  # ターン（1枚）を配る
            self.betting_round()
            self.current_round = "post_turn"
        elif self.current_round == "post_turn":
            self.deal_community_cards(1)  # リバー（1枚）を配る
            self.betting_round()
            self.current_round = "post_river"
        elif self.current_round == "post_river":
            self.showdown()  # ショーダウンで勝者を決める

    def deal_community_cards(self, num_cards: int):
        """コミュニティカードを配る"""
        for _ in range(num_cards):
            card = self.table.deck.draw()
            self.community_cards.append(card)

    def betting_round(self):
        """ベット、コール、レイズ、フォールドのラウンド"""
        for player in self.active_players:
            legal_actions = get_legal_actions(player, self.table)
            action = player.decide_action(legal_actions)  # プレイヤーにアクションを決定させる
            apply_action(player, action, self.table)
            self.pot += action.amount  # ポットにアクション額を追加

        # 次のラウンドに進む条件（すべてのアクションが完了した場合など）
        self.check_for_end_of_round()

    def check_for_end_of_round(self):
        """ラウンドが終了したかを確認"""
        if len(self.active_players) == 1:
            # プレイヤーが1人になった場合はラウンド終了
            self.showdown()
        else:
            # すべてのアクションが完了した場合
            # ここでポット額や最小ベット額の確認が必要
            pass

    def showdown(self):
        """ショーダウン処理：最終的に勝者を決める"""
        # 勝者の判定処理をここに追加（プレイヤーの手札とコミュニティカードで比較）
        winner = self.determine_winner()
        print(f"Winner is {winner.name}!")
        self.reset_for_new_round()

    def determine_winner(self):
        """勝者を決定するためのメソッド（仮実装）"""
        # ここで手札とコミュニティカードを比較して勝者を決めるロジックを実装
        return self.active_players[0]  # 仮実装：1人だけ残っているプレイヤーを勝者とする

    def reset_for_new_round(self):
        """次のラウンドのために状態をリセット"""
        for player in self.table.players:
            player.reset_for_new_hand()
        self.start_round()  # 新しいラウンドを開始

