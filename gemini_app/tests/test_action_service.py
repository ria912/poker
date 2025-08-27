# tests/test_action_service.py
import pytest
import sys
import os

# プロジェクトのルートをシステムパスに追加して、appモジュールをインポートできるようにする
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.seat import Table, Seat
from app.models.player import Player
from app.models.game_state import GameState
from app.models.enum import Action, PlayerState, Round, State
from app.services.action_service import ActionService
from app.services.player_service import PlayerService

# --- テスト用の設定値 ---
PLAYER_COUNT = 3
INITIAL_STACK = 10000
SB = 50
BB = 100

# --- テストのセットアップ (pytest fixture) ---
@pytest.fixture
def setup_game():
    """3人プレイのプリフロップ直後の状態をセットアップする共通処理"""
    table = Table(seats=[Seat(index=i) for i in range(PLAYER_COUNT)])
    gs = GameState(small_blind=SB, big_blind=BB)
    
    action_service = ActionService()
    player_service = PlayerService()

    # プレイヤーを作成して着席させる
    players = [Player(name=f"Player {i+1}", initial_stack=INITIAL_STACK) for i in range(PLAYER_COUNT)]
    for i, player in enumerate(players):
        player_service.sit_down(table, i, player.player_id, player.initial_stack)

    # ハンド開始前の状態を模倣
    gs.state = State.WAITING
    gs.round = Round.PREFLOP
    gs.dealer_index = 0

    # ブラインドを支払う
    # Dealer: 0, SB: 1, BB: 2
    sb_seat = table.get_seat(1)
    bb_seat = table.get_seat(2)
    
    sb_seat.stack -= SB
    sb_seat.bet_total += SB
    gs.round_bets[1] = SB
    
    bb_seat.stack -= BB
    bb_seat.bet_total += BB
    gs.round_bets[2] = BB
    
    gs.current_bet = BB
    gs.min_raise = BB
    
    # プリフロップのアクションはBBの次から
    gs.current_turn = 0 # UTG (Dealer)
    
    # 全員未アクションの状態にする
    for seat in table.seats:
        seat.acted = False

    return table, gs, action_service

# --- ActionServiceのテストケース ---

def test_get_legal_actions_utg_preflop(setup_game):
    """プリフロップ: UTGの合法アクションをテスト"""
    table, gs, action_service = setup_game
    
    # UTG (index 0) の番
    gs.current_turn = 0
    actions = action_service.get_legal_actions(table, gs, 0)
    
    # BBにコールするには100必要
    assert set(actions) == {Action.FOLD, Action.CALL, Action.RAISE, Action.ALL_IN}

def test_get_legal_actions_no_bet(setup_game):
    """フロップ: ベットがない状況での合法アクションをテスト"""
    table, gs, action_service = setup_game
    
    # フロップに進み、ベットがない状態を模倣
    gs.round = Round.FLOP
    gs.current_bet = 0
    gs.round_bets = {i: 0 for i in range(PLAYER_COUNT)}
    gs.current_turn = 1 # SBからアクション
    
    actions = action_service.get_legal_actions(table, gs, 1)
    
    assert set(actions) == {Action.FOLD, Action.CHECK, Action.BET, Action.ALL_IN}


def test_apply_fold(setup_game):
    """アクション: FOLD をテスト"""
    table, gs, action_service = setup_game
    
    actor_index = 0
    action_service.apply(table, gs, actor_index, Action.FOLD)
    
    actor_seat = table.get_seat(actor_index)
    assert actor_seat.state == PlayerState.FOLDED
    assert actor_seat.acted is True

def test_apply_call(setup_game):
    """アクション: CALL をテスト"""
    table, gs, action_service = setup_game
    
    actor_index = 0
    actor_seat = table.get_seat(actor_index)
    initial_stack = actor_seat.stack
    
    action_service.apply(table, gs, actor_index, Action.CALL)
    
    # BBの100にコール
    expected_stack = initial_stack - BB
    assert actor_seat.stack == expected_stack
    assert gs.round_bets[actor_index] == BB
    assert actor_seat.acted is True

def test_apply_raise(setup_game):
    """アクション: RAISE をテスト"""
    table, gs, action_service = setup_game
    
    actor_index = 0
    actor_seat = table.get_seat(actor_index)
    initial_stack = actor_seat.stack
    
    total_bet_amount = 300 # BB(100)に対して、さらに200上乗せして合計300のレイズ
    action_service.apply(table, gs, actor_index, Action.RAISE, amount=total_bet_amount)

    # 支払う額はコール分(100) + レイズ分(200) = 300
    expected_stack = initial_stack - total_bet_amount
    assert actor_seat.stack == expected_stack
    assert gs.round_bets[actor_index] == total_bet_amount
    assert gs.current_bet == total_bet_amount
    assert gs.min_raise == (total_bet_amount - BB) # min_raiseは差額で更新される
    assert gs.last_aggressor == actor_index
    
    # レイズしたので、他のプレイヤー(SB, BB)は未アクションに戻る
    assert table.get_seat(1).acted is False
    assert table.get_seat(2).acted is False

def test_raise_under_min_raise_should_fail(setup_game):
    """アクション: 最小レイズ額未満のRAISEはエラーになることをテスト"""
    table, gs, action_service = setup_game
    
    # BB(100)に対して、50だけ上乗せするレイズ (min_raiseは100)
    invalid_raise_amount = 50
    
    with pytest.raises(ValueError, match="RAISE が最小レイズ未満"):
        action_service.apply(table, gs, 0, Action.RAISE, amount=invalid_raise_amount)

def test_is_betting_round_complete(setup_game):
    """ラウンド終了判定をテスト"""
    table, gs, action_service = setup_game
    
    # 初期状態 (UTGが未アクション) では完了していない
    assert not action_service.is_betting_round_complete(table, gs)
    
    # UTGがコール
    action_service.apply(table, gs, 0, Action.CALL)
    gs.current_turn = action_service.next_to_act(table, gs, 0) # -> SB(1)
    assert not action_service.is_betting_round_complete(table, gs)
    
    # SBがコール
    action_service.apply(table, gs, 1, Action.CALL)
    gs.current_turn = action_service.next_to_act(table, gs, 1) # -> BB(2)
    assert not action_service.is_betting_round_complete(table, gs)
    
    # BBがチェック (オプション)
    # BBはすでにBBを払っているので、コール額は0 -> CHECKが合法
    gs.current_turn = 2
    legal_actions = action_service.get_legal_actions(table, gs, 2)
    assert Action.CHECK in legal_actions
    action_service.apply(table, gs, 2, Action.CHECK)
    
    # 全員のアクションが完了し、ベット額が揃ったのでラウンド終了
    assert action_service.is_betting_round_complete(table, gs)