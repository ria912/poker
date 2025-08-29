from treys import Card as TreysCard, Evaluator
from ..models.game_state import GameState
from ..models.enum import GameState as GameStatusEnum, Position, Round, SeatState
from . import round_service

def start_hand(game_state: GameState):
    """新しいハンドを開始する"""
    game_state.clear_for_new_hand()
    
    # アクティブなプレイヤーが2人未満なら開始しない
    active_seats = [s for s in game_state.table.seats if s.is_occupied and s.stack > 0]
    if len(active_seats) < 2:
        game_state.status = GameStatusEnum.WAITING
        return

    game_state.status = GameStatusEnum.IN_PROGRESS
    
    # ディーラーボタンを移動
    game_state.dealer_btn_index = round_service.find_next_player_index(
        game_state, game_state.dealer_btn_index
    )

    # ポジションの割り当てとブラインドの徴収
    _assign_positions_and_post_blinds(game_state)
    
    # カードを配る
    _deal_hole_cards(game_state)
    
    # プリフロップのアクション開始プレイヤーを決定
    utg_index = round_service.find_next_player_index(game_state, game_state.big_blind_index)
    game_state.active_seat_index = utg_index


def _assign_positions_and_post_blinds(game_state: GameState):
    """ポジションを割り当て、ブラインドを強制ベットさせる"""
    sb_index = round_service.find_next_player_index(game_state, game_state.dealer_btn_index)
    bb_index = round_service.find_next_player_index(game_state, sb_index)
    
    sb_seat = game_state.table.seats[sb_index]
    bb_seat = game_state.table.seats[bb_index]
    
    sb_seat.position = Position.SB
    bb_seat.position = Position.BB

    sb_amount = sb_seat.bet(game_state.small_blind)
    bb_amount = bb_seat.bet(game_state.big_blind)

    game_state.amount_to_call = bb_amount
    game_state.min_raise_amount = bb_amount
    game_state.last_raiser_seat_index = bb_index
    game_state.big_blind_index = bb_index # BBの位置を記憶

def _deal_hole_cards(game_state: GameState):
    """各プレイヤーに手札を2枚ずつ配る"""
    seats = game_state.table.seats
    num_seats = len(seats)
    start_index = game_state.dealer_btn_index
    
    # SBから時計回りに配る
    deal_order = [(start_index + i) % num_seats for i in range(1, num_seats + 1)]
    
    for _ in range(2): # 2枚配る
        for seat_index in deal_order:
            seat = seats[seat_index]
            if seat.is_occupied and seat.state != SeatState.OUT:
                seat.hole_cards.extend(game_state.table.deck.draw(1))

def determine_winner_and_distribute_pot(game_state: GameState):
    """勝者を判定し、ポットを分配する"""
    game_state.table.collect_bets() # 最終ベットをポットへ
    
    showdown_players = [
        s for s in game_state.table.seats if s.state in [SeatState.ACTIVE, SeatState.ALL_IN]
    ]

    # 生き残りが一人の場合
    if len(showdown_players) == 1:
        winner = showdown_players[0]
        winner.stack += game_state.table.pot
        print(f"Winner is {winner.player.name}, wins {game_state.table.pot}")
        return

    # ショーダウンの場合
    evaluator = Evaluator()
    board = [c.to_treys_int() for c in game_state.table.community_cards]
    scores = {}

    for player_seat in showdown_players:
        hand = [c.to_treys_int() for c in player_seat.hole_cards]
        score = evaluator.evaluate(board, hand)
        scores[player_seat.index] = score
        print(f"{player_seat.player.name} has hand rank: {evaluator.get_rank_class(score)}")

    # 最も良いスコア（値が小さい）を探す
    best_score = min(scores.values())
    winners = [idx for idx, score in scores.items() if score == best_score]
    
    # ポットを分配
    win_amount = game_state.table.pot // len(winners)
    for winner_idx in winners:
        winner_seat = game_state.table.seats[winner_idx]
        winner_seat.stack += win_amount
        print(f"Winner is {winner_seat.player.name}, wins {win_amount}")

    game_state.status = GameStatusEnum.HAND_COMPLETE