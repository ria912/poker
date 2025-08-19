# tests/test_game_flow.py
import pytest
from app.models.player import Player
from app.models.table import Table, Seat
from app.models.game_state import GameState
from app.services.game_service import GameService


@pytest.fixture
def setup_game():
    """テーブルとプレイヤーを準備"""
    players = [Player(name=f"Player{i+1}", stack=1000) for i in range(4)]
    seats = [Seat(number=i, player=players[i]) for i in range(4)]
    table = Table(seats=seats)

    game_state = GameState(table=table)
    game_service = GameService()
    return game_service, game_state


def test_full_game_flow(setup_game):
    game_service, game_state = setup_game

    # -----------------
    # ハンド開始
    # -----------------
    game_service.start_new_hand(game_state)
    assert game_state.round.name == "PREFLOP"
    assert game_state.state.name == "IN_PROGRESS"
    print("=== Start Hand ===")
    for seat in game_state.table.seats:
        if seat.player:
            print(f"{seat.player.name}: stack={seat.player.stack}, hand={seat.player.hand}")

    # -----------------
    # ラウンド進行
    # -----------------
    while game_state.state.name != "FINISHED":
        game_service.proceed_to_next_round(game_state)

        print(f"\n--- Round: {game_state.round.name} ---")
        print(f"Board: {game_state.table.board}")
        print(f"Pot: {game_state.table.pot}")

    # -----------------
    # 勝者確認
    # -----------------
    print("\n=== Showdown ===")
    for seat in game_state.table.seats:
        if seat.player:
            print(f"{seat.player.name}: stack={seat.player.stack}")

    assert game_state.state.name == "FINISHED"