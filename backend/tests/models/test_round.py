# tests/models/test_round.py
import pytest
from backend.models.round import RoundManager, Round
from backend.models.enum import Status
from backend.models.table import Table, Seat
from backend.models.player import Player
from unittest.mock import MagicMock

class DummyPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = []
        self.has_acted = False

    def act(self, table):
        self.has_acted = True
        return ('fold', 0)  # テスト用固定アクション

@pytest.fixture
def simple_table():
    # Tableオブジェクトを最小限で構築
    table = MagicMock(spec=Table)
    player1 = DummyPlayer("P1")
    player2 = DummyPlayer("P2")
    player3 = DummyPlayer("P3")

    seat1 = MagicMock()
    seat2 = MagicMock()
    seat3 = MagicMock()

    seat1.player = player1
    seat2.player = player2
    seat3.player = player3

    table.seats = [seat1, seat2, seat3]
    table.get_active_seats.return_value = [seat1, seat2, seat3]
    table.round = Round.PREFLOP
    table.btn_index = 0
    table.is_round_complete.return_value = False

    return table, [seat1, seat2, seat3]

def test_compute_action_order(simple_table):
    table, seats = simple_table
    manager = RoundManager(table)

    order = manager.compute_action_order()
    # btn_index = 0 → base_index = 3 % 3 = 0 → 順番そのまま
    assert order == [seats[0], seats[1], seats[2]]

def test_proceed_player_acted(simple_table):
    table, seats = simple_table
    manager = RoundManager(table)
    manager.reset()

    status = manager.proceed()
    assert status == Status.PLAYER_ACTED
    assert seats[0].player.has_acted is True
