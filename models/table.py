from models.card import Deck
from models.action import Action
import random

class Table:

    POSITIONS = ['BTN', 'SB', 'BB', 'LJ', 'HJ', 'CO']
    ROUNDS = ['preflop', 'flop', 'turn', 'river', 'showdown']
    SMOOL_BLIND = 50
    BIG_BLIND = 100
    MAX_PLAYERS = 6

    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_round = 'preflop' # 現在のラウンド
        self.current_bet = 0 # 現在の最大ベット額
        self.min_bet = 100 # 最小ベット額
        self.min_raise = 200
        self.button_index = 0 # BTNのプレイヤーを指すプレイヤー（舞ラウンド回る？）

    # 
    def assign_positions(self):
        num_players = len(self.players)
        for i, player in enumerate(self.players):
            pos_index = (self.button_index + i) % num_players
            player.position = self.POSITIONS[pos_index]

    def deal_cards(self):
        self.assign_positions() # プレイヤーのポジションを決定
        for player in self.players:
            player.hand = [self.deck.draw(), self.deck.draw()]

    def proceed_to_next_turn(self):
        # アクション順に進行
        remaining = self.get_active_players()
        if len(remaining) == 1:
            return 'end_hand'

        # 次のプレイヤー
        while True:
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            player = self.players[self.active_player_index]
            if not player.has_folded and player.stack > 0: # フォールドしていない、スタックがある場合
                break

        return 'continue'

    def start_betting_round(self):
        self.current_bet = 0
        self.min_raise = 200 # 最小レイズ額(今は仮で200)
        for p in self.players:
            p.current_bet = 0
        self.active_player_index = (self.button_index + 1) % len(self.players)

    def get_active_players(self):
        return [p for p in self.players if not p.has_folded and p.stack > 0]

    def advance_round(self):
        if self.current_stage == 'preflop':
            self.community_cards = [self.deck.draw() for _ in range(3)]
            self.current_stage = 'flop'
        elif self.current_stage == 'flop':
            self.community_cards.append(self.deck.draw())
            self.current_stage = 'turn'
        elif self.current_stage == 'turn':
            self.community_cards.append(self.deck.draw())
            self.current_stage = 'river'
        elif self.current_stage == 'river':
            self.current_stage = 'showdown'

    def to_dict(self):
        return {
            "community_cards": self.community_cards,
            "players": [p.to_dict() for p in self.players]
        }
