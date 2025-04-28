from models.card import Deck
from models.position import rotate_players, assign_positions

class Table:
    
    SMALL_BLIND = 50
    BIG_BLIND =100
    
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = 20  # 初期ビッグブラインド
        self.big_blind = 20  # （必要なら変数に持っておくと便利）

    def start_hand(self):
        """
        新しいハンドを開始する処理
        """
        self.deck.shuffle()
        self.reset_players()
        self.rotate_players()
        self.assign_positions()
        self.deal_cards()
        self.pot = 0
        self.current_bet = 0

    def reset_players(self):
        """
        各プレイヤーの一時情報をリセットする
        """
        for player in self.players:
            player.hand = []
            player.current_bet = 0
            player.has_folded = False
            player.position = None  # ハンドごとにポジションもリセット

    def rotate_players(self):
        """
        プレイヤーの並びを時計回りに1つずらす（離席者も含む）
        """
        self.players.append(self.players.pop(0))

    def assign_positions(self):
        """
        離席していないプレイヤーにポジションを割り当てる
        """
        full_positions = ['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']
        assignment_order = ['SB', 'BB', 'LJ', 'HJ', 'CO', 'BTN']

        active_players = [p for p in self.players if not p.has_left]

        available = full_positions[:len(active_players)]
        assigned = [p for p in assignment_order if p in available]

        for player in self.players:
            player.position = None  # 全員リセット

        for player, pos in zip(active_players, assigned):
            player.position = pos

    def deal_cards(self):
        """
        各プレイヤーに2枚ずつ手札を配る
        """
        for player in self.players:
            if not player.has_left:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def to_dict(self):
        """
        テーブルの状態を辞書で返す（セッション保存用など）
        """
        return {
            "community_cards": self.community_cards,
            "pot": self.pot,
            "players": [p.to_dict() for p in self.players]
        }