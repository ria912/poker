# holdem_app/app/services/round_manager.py
from app.models.game_state import GameState
from app.models.enum import Round, SeatStatus
from . import position_service

def start_betting_round(game_state: GameState):
    """
    新しいベッティングラウンドを開始する。
    - アクション済みフラグのリセット
    - アクション開始プレイヤーの設定
    """
    print(f"\n--- Starting Round: {game_state.current_round.name} ---")
    
    # テーブルのベット額をポットに集める
    game_state.table.collect_bets()

    # ラウンドに応じてコミュニティカードをめくる
    if game_state.current_round == Round.FLOP:
        game_state.table.community_cards.extend(game_state.table.deck.draw(3))
    elif game_state.current_round in [Round.TURN, Round.RIVER]:
        game_state.table.community_cards.extend(game_state.table.deck.draw(1))

    # 各プレイヤーのアクション済みフラグ等をリセット
    for seat in game_state.table.seats:
        if seat.status not in [SeatStatus.FOLDED, SeatStatus.ALL_IN, SeatStatus.OUT]:
            seat.acted = False
    
    # アクションを開始するプレイヤーを決定する
    start_seat_index = position_service.get_first_to_act(game_state)
    game_state.current_seat_index = start_seat_index
    game_state.last_raiser_seat_index = start_seat_index
    
    # コール額とミニマムレイズ額をリセット
    game_state.amount_to_call = 0
    game_state.min_raise_amount = game_state.big_blind


def advance_to_next_round(game_state: GameState):
    """次のラウンドへ進める"""
    round_order = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]
    current_idx = round_order.index(game_state.current_round)
    
    if current_idx + 1 < len(round_order):
        next_round = round_order[current_idx + 1]
        game_state.current_round = next_round
        if next_round != Round.SHOWDOWN:
            start_betting_round(game_state)
    else:
        # ゲーム終了
        pass

def is_round_over(game_state: GameState) -> bool:
    """現在のベッティングラウンドが終了したかを判定する"""
    # 全員がアクション済みで、かつベット額が等しい状態かなどをチェック
    # ... 実装 ...
    return False # 仮
