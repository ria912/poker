from ..models.game_state import GameState
from ..models.enum import GameRound
from . import table_service, deck_service

def start_new_hand(game_state: GameState):
    """新しいハンドを開始"""
    table_service.reset_table(game_state)
    deck_service.reset_deck(game_state)
    # 各プレイヤーに2枚配る
    for i, seat in enumerate(game_state.table.seats):
        if seat.is_occupied:
            deck_service.deal_to_player(game_state, i)

def next_round(game_state: GameState):
    """ラウンド進行"""
    if game_state.table.current_round == GameRound.PREFLOP:
        deck_service.deal_to_table(game_state, 3)  # Flop
        game_state.table.current_round = GameRound.FLOP
    elif game_state.table.current_round == GameRound.FLOP:
        deck_service.deal_to_table(game_state, 1)  # Turn
        game_state.table.current_round = GameRound.TURN
    elif game_state.table.current_round == GameRound.TURN:
        deck_service.deal_to_table(game_state, 1)  # River
        game_state.table.current_round = GameRound.RIVER
    elif game_state.table.current_round == GameRound.RIVER:
        game_state.table.current_round = GameRound.SHOWDOWN