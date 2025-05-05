from models.deck import Deck
from models.position import rotate_button, assign_positions
from models.player import Player
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer

class Table:
    def __init__(self, small_blind=50, big_blind=100):
        self.players = self.create_players()
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = big_blind
        self.big_blind = big_blind
        self.small_blind = small_blind
    
    def create_players(self):
        players = [HumanPlayer(name="YOU")]  # 人間プレイヤー
        for i in range(1, 6):
            players.append(AIPlayer(name=f"AI{i}"))
        return players

    def start_hand(self):
        self.deck.deck_shuffle()
        self.reset_players()
        rotate_button(self.players)
        assign_positions(self.players)
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.post_blinds()
        self.deal_cards()

    def reset_players(self):
        for player in self.players:
            player.reset_for_new_hand()
    
    def post_blinds(self):
        for player in self.players:
            if player.position == 'SB':
                # チップが足りない場合は全額（オールイン）
                blind = min(self.small_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.pot += blind

            elif player.position == 'BB':
                # チップが足りない場合は全額（オールイン）
                blind = min(self.big_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.current_bet = blind
                self.min_bet = blind
                self.pot += blind

    def deal_cards(self):
        for player in self.players:
            if not player.has_left:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def to_dict(self):
        return {
            "community_cards": self.community_cards,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "min_bet": self.min_bet,
            "players": [p.to_dict() for p in self.players]
        }
