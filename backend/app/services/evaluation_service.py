# holdem_app/app/services/evaluation_service.py
from typing import List, Tuple
from collections import defaultdict
from treys import Evaluator
from app.models.game_state import GameState
from app.models.seat import Seat
from app.models.deck import Card
from app.models.enum import SeatStatus

def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> int:
    """
    ホールカードとコミュニティカードから役の強さを評価する。
    """
    evaluator = Evaluator()
    
    treys_hole = [c.to_treys_int() for c in hole_cards]
    treys_community = [c.to_treys_int() for c in community_cards]
    
    return evaluator.evaluate(treys_community, treys_hole)

def find_winners(game_state: GameState, verbose: bool = True) -> List[Tuple[Seat, int]]:
    """
    ショウダウン時に勝者を決定し、ポットを分配する。
    """
    # bet_total > 0 の条件を削除
    showdown_seats = [
        s for s in game_state.table.seats 
        if s.status not in [SeatStatus.FOLDED, SeatStatus.OUT]
    ]

    # 生き残ったプレイヤーが1人なら、その人がポットを総取り
    if len(showdown_seats) <= 1:
        if showdown_seats:
            winner = showdown_seats[0]
            if verbose:
                print(f"Winner is {winner.player.name} (everyone else folded)")
            return [(winner, game_state.table.pot)]
        return []

    # 各プレイヤーの役を評価
    if verbose:
        print("--- Showdown ---")
    for seat in showdown_seats:
        seat.hand_score = evaluate_hand(seat.hole_cards, game_state.table.community_cards)
        if verbose:
            evaluator = Evaluator()
            hand_class = evaluator.get_rank_class(seat.hand_score)
            print(f"Seat {seat.index} ({seat.player.name}) has cards {[str(c) for c in seat.hole_cards]} with hand: {evaluator.class_to_string(hand_class)}")


    all_in_amounts = sorted(list(set(s.bet_total for s in showdown_seats if s.bet_total > 0)))
    
    pots = []
    last_amount = 0
    
    # メインポット、サイドポットを計算
    for amount in all_in_amounts:
        pot_size = 0
        for seat in game_state.table.seats:
            if seat.bet_total > last_amount:
                contribution = min(seat.bet_total, amount) - last_amount
                pot_size += contribution
        
        if pot_size > 0:
            eligible_players = [s for s in showdown_seats if s.bet_total >= amount]
            pots.append({"size": pot_size, "eligible": eligible_players})
        last_amount = amount

    # まだポットに分配されていないベットがあれば、それもポットに加える
    total_in_pots = sum(p['size'] for p in pots)
    remaining_pot = game_state.table.pot - total_in_pots
    if remaining_pot > 0:
        # これは通常、誰もオールインしていないときのメインポット
        eligible_players = [s for s in showdown_seats]
        pots.append({"size": remaining_pot, "eligible": eligible_players})


    winnings = defaultdict(int)
    for i, pot in enumerate(pots):
        best_score = min(s.hand_score for s in pot["eligible"])
        winners = [s for s in pot["eligible"] if s.hand_score == best_score]
        
        win_amount_per_winner = pot["size"] // len(winners)
        if verbose:
            pot_name = f"Main Pot" if i == 0 else f"Side Pot {i}"
            print(f"{pot_name} ({pot['size']}) winners: {[w.player.name for w in winners]}")

        for winner in winners:
            winnings[winner.index] += win_amount_per_winner

    # 端数を最初の勝者に渡す
    total_distributed = sum(winnings.values())
    remainder = game_state.table.pot - total_distributed
    if remainder > 0 and winnings:
         first_winner_idx = list(winnings.keys())[0]
         winnings[first_winner_idx] += remainder

    return [(game_state.table.seats[idx], amount) for idx, amount in winnings.items()]
