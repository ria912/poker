import pytest
from backend.models.action import ActionManager
from backend.models.enum import Action


class PlayerMock:
    def __init__(self, stack, bet_total=0):
        self.stack = stack
        self.bet_total = bet_total
        self.has_folded = False
        self.has_all_in = False
        self.last_action = None


class TableMock:
    def __init__(self, current_bet=0, min_bet=100, pot=0):
        self.current_bet = current_bet
        self.min_bet = min_bet
        self.pot = pot
        self.last_raiser = None


# === get_legal_actions_info のテスト ===

def test_get_legal_actions_info_check_bet():
    player = PlayerMock(stack=1000, bet_total=0)
    table = TableMock(current_bet=0)

    result = ActionManager.get_legal_actions_info(player, table)
    assert set(result["legal_actions"]) == {Action.FOLD, Action.CHECK, Action.BET}


def test_get_legal_actions_info_call_raise():
    player = PlayerMock(stack=1000, bet_total=200)
    table = TableMock(current_bet=400)

    result = ActionManager.get_legal_actions_info(player, table)
    assert set(result["legal_actions"]) == {Action.FOLD, Action.CALL, Action.RAISE}


def test_get_legal_actions_info_check_only():
    player = PlayerMock(stack=500, bet_total=300)
    table = TableMock(current_bet=300)

    result = ActionManager.get_legal_actions_info(player, table)
    assert Action.CHECK in result["legal_actions"]
    assert Action.CALL not in result["legal_actions"]
    assert Action.BET not in result["legal_actions"]


# === apply_action のテスト ===

def test_apply_fold():
    player = PlayerMock(stack=1000)
    table = TableMock()
    ActionManager.apply_action(player, table, Action.FOLD, 0)
    assert player.has_folded is True


def test_apply_bet():
    player = PlayerMock(stack=1000)
    table = TableMock()
    ActionManager.apply_action(player, table, Action.BET, 300)

    assert player.stack == 600  # 1000 - (300 + 100 min_bet)
    assert player.bet_total == 400
    assert table.pot == 400
    assert table.current_bet == 400
    assert table.min_bet == 400


def test_apply_call():
    player = PlayerMock(stack=500, bet_total=100)
    table = TableMock(current_bet=300)
    ActionManager.apply_action(player, table, Action.CALL, 0)

    assert player.bet_total == 300
    assert player.stack == 300
    assert table.pot == 200


def test_apply_raise():
    player = PlayerMock(stack=1000, bet_total=200)
    table = TableMock(current_bet=300, min_bet=100, pot=500)
    ActionManager.apply_action(player, table, Action.RAISE, 400)

    # total = 400 (amount) + 100 (min_bet) + 100 (to_call) = 600
    assert player.stack == 400
    assert player.bet_total == 800
    assert table.pot == 1100
    assert table.current_bet == 800
    assert table.min_bet == 500  # raise_amount = 600 - 100


def test_all_in_flag():
    player = PlayerMock(stack=200)
    table = TableMock()
    ActionManager.apply_action(player, table, Action.BET, 200)

    assert player.stack == 0
    assert player.has_all_in is True
