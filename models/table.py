from models.card import Deck
from models.position import rotate_players, assign_positions
from models.player import Player
from models.ai_player import AIPlayer

def create_players():
    """
    プレイヤー1人とAI1〜5人を生成
    """
    players = [Player(name="YOU", is_human=True)]  # プレイヤー1人（人間）
    player_names = ["AI1", "AI2", "AI3", "AI4", "AI5"]
    
    # AIプレイヤーの生成（5人）
    for name in player_names:
        players.append(AIPlayer(name=name))
    
    return players


class Table:
    def __init__(self, small_blind=50, big_blind=100):
        self.players = create_players()
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_bet = big_blind
        self.big_blind = big_blind
        self.small_blind = small_blind
    
    def start_hand(self):
        self.deck.shuffle()
        self.reset_players()
        rotate_players(self.players)
        assign_positions(self.players)
        self.post_blinds()
        self.deal_cards()
        self.pot = 0
        self.current_bet = 0

    def reset_players(self):
        for player in self.players:
            player.reset_for_new_hand()
    
    def post_blinds(self, small_blind=50, big_blind=100):
        for player in self.players:
            if player.position == 'SB':
                blind = min(small_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.pot += blind

            elif player.position == 'BB':
                blind = min(big_blind, player.stack)
                player.stack -= blind
                player.current_bet = blind
                self.pot += blind
                self.current_bet = big_blind
                self.min_bet = big_blind

    def deal_cards(self):
        for player in self.players:
            if not player.has_left:
                player.hand = [self.deck.draw(), self.deck.draw()]

    def to_dict(self):
        return {
            "community_cards": self.community_cards,
            "pot": self.pot,
            "players": [p.to_dict() for p in self.players]
        }
