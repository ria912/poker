# tests/test_round_service.py
import pytest
import sys
import os

# プロジェクトのルートをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.table import Table, Seat
from app.models.player import Player
from app.models.game_state import GameState
from app.models.enum import Round, State, PlayerState
from app.services.round_service import RoundService
from app.services.player_service import PlayerService
from app.models.deck import Deck # Deckを直接利用するためインポート

# --- テスト用の設定値 ---
PLAYER_COUNT = 6
INITIAL_STACK = 10000
SB = 50
BB = 100

# --- テストのセットアップ ---
@pytest.fixture
def setup_table():
    """6人プレイのテーブルとプレイヤーを準備する共通処理"""
    table = Table(seats=[Seat(index=i) for i in range(PLAYER_COUNT)])
    gs = GameState(small_blind=SB, big_blind=BB)
    
    player_service = PlayerService()

    # プレイヤーを作成して着席させる
    players = [Player(name=f"Player {i+1}", initial_stack=INITIAL_STACK) for i in range(PLAYER_COUNT)]
    for i, player in enumerate(players):
        player_service.sit_down(table, i, player.player_id, player.initial_stack)

    # RoundServiceのインスタンスも返す
    round_service = RoundService()
    
    return table, gs, round_service

# --- RoundServiceのテストケース ---

def test_start_new_hand_positions_and_blinds(setup_table):
    """start_new_hand: ディーラー位置、ブラインド、最初のアクションプレイヤーが正しいかテスト"""
    table, gs, round_service = setup_table
    
    # Dealerを0番としてハンド開始
    dealer_index = 0
    deck = Deck()
    round_service.start_new_hand(table, gs, deck, dealer_index)

    # 1. 各プレイヤーの状態を確認
    for seat in table.seats:
        assert seat.state == PlayerState.ACTIVE
        assert len(seat.hole_cards) == 2
        assert seat.bet_total > 0 if seat.index in [1, 2] else seat.bet_total == 0

    # 2. ブラインドの支払いを確認
    sb_seat = table.get_seat(1) # Dealer(0)の次
    bb_seat = table.get_seat(2) # SB(1)の次
    assert gs.round_bets[sb_seat.index] == SB
    assert sb_seat.stack == INITIAL_STACK - SB
    assert gs.round_bets[bb_seat.index] == BB
    assert bb_seat.stack == INITIAL_STACK - BB
    
    # 3. GameStateの状態を確認
    assert gs.dealer_index == dealer_index
    assert gs.current_bet == BB
    assert gs.state == State.IN_PROGRESS
    assert gs.round == Round.PREFLOP
    
    # 4. プリフロップの最初のアクションはBB(2)の次 -> UTG(3)
    assert gs.current_turn == 3

def test_start_new_hand_dealer_rotation(setup_table):
    """start_new_hand: ディーラーが正しく次のプレイヤーに移動するかテスト"""
    table, gs, round_service = setup_table
    deck = Deck()

    # 最初のハンド (gs.dealer_indexはNone)
    round_service.start_new_hand(table, gs, deck)
    assert gs.dealer_index == 0 # 最初のアクティブプレイヤー

    # 次のハンド (前回のdealer_indexから次に進む)
    round_service.start_new_hand(table, gs, deck)
    assert gs.dealer_index == 1 # 次のアクティブプレイヤー
    
    # さらに次のハンド
    round_service.start_new_hand(table, gs, deck)
    assert gs.dealer_index == 2

def test_deal_next_street_to_flop(setup_table):
    """deal_next_street: PREFLOPからFLOPへの遷移をテスト"""
    table, gs, round_service = setup_table
    
    # プリフロップの状態を模倣
    gs.round = Round.PREFLOP
    gs.dealer_index = 0
    for seat in table.seats:
        seat.acted = True # 全員アクション済み
    
    deck = Deck()
    deck_initial_size = len(deck.cards)

    round_service.deal_next_street(table, gs, deck)
    
    # 1. ボードとデッキの状態
    assert len(table.board) == 3
    # 1枚バーン + 3枚フロップ = 4枚消費
    assert len(deck.cards) == deck_initial_size - 3
    
    # 2. GameStateの更新
    assert gs.round == Round.FLOP
    assert gs.current_bet == 0 # ラウンドベットはリセットされる
    assert gs.round_bets == {i: 0 for i in range(PLAYER_COUNT)}
    
    # 3. アクションプレイヤーの更新 (Post-FlopはSBから)
    # Dealer(0)の次 -> SB(1)
    assert gs.current_turn == 1
    
    # 4. actedフラグのリセット
    for seat in table.seats:
        assert not seat.acted

def test_deal_next_street_through_river(setup_table):
    """deal_next_street: FLOP -> TURN -> RIVER -> SHOWDOWN への遷移をテスト"""
    table, gs, round_service = setup_table
    deck = Deck()
    gs.dealer_index = 0

    # FLOPへ
    gs.round = Round.PREFLOP
    round_service.deal_next_street(table, gs, deck)
    assert gs.round == Round.FLOP
    assert len(table.board) == 3
    
    # TURNへ
    round_service.deal_next_street(table, gs, deck)
    assert gs.round == Round.TURN
    assert len(table.board) == 4
    
    # RIVERへ
    round_service.deal_next_street(table, gs, deck)
    assert gs.round == Round.RIVER
    assert len(table.board) == 5

    # SHOWDOWNへ
    round_service.deal_next_street(table, gs, deck)
    assert gs.state == State.SHOWDOWN