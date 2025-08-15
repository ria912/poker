# app/services/deck_service.py
from ..models.deck import Deck
from ..models.game_state import GameState

def reset_deck(game_state: GameState):
    game_state.deck = Deck()
    game_state.deck.reset_and_shuffle()

def deal_to_player(game_state: GameState):
    for seat in game_state.table.seats:
        if seat.is_occupied and seat.player:
            seat.player.hand = game_state.deck.deal(2)

def deal_to_table(game_state: GameState, num_cards: int):
    game_state.table.community_cards.extend(game_state.deck.deal(num_cards))