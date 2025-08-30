# holdem_app/app/services/evaluation_service.py
from typing import List, Tuple
from treys import Evaluator, Card as TreysCard
from app.models.game_state import GameState
from app.models.seat import Seat
from app.models.enum import SeatStatus

def evaluate_hand(hole_cards: list, community_cards: list) -> int:
    """
    ホールカードとコミュニティカードから役の強さを評価する。
    treysライブラリを使用してスコアを返す（小さいほど強い）。
    """
    evaluator = Evaluator()
    
    # モデルのCardオブジェクトをtreysのint形式に変換
    treys_hole = [c.to_treys_int() for c in hole_cards]
    treys_community = [c.to_treys_int() for c in community_cards]
    
    return evaluator.evaluate(treys_hole, treys_community)

def find_winners(game_state: GameState) -> List[Tuple[Seat, int]]:
    """
    ショウダウン時に勝者を決定する。
    ポット分配を考慮し、複数の勝者（チョップ）も判定する。
    返り値: (勝者のSeatオブジェクト, 獲得ポット額) のリスト
    """
    print("Finding winners...")
    
    # ショウダウンに進んだプレイヤーのみを対象
    showdown_players = [
        seat for seat in game_state.table.seats 
        if seat.status not in [SeatStatus.FOLDED, SeatStatus.OUT]
    ]

    if not showdown_players:
        return []

    if len(showdown_players) == 1:
        # 他の全員がフォールドした場合
        winner_seat = showdown_players[0]
        return [(winner_seat, game_state.table.pot)]

    # 役の評価
    scores = {}
    for seat in showdown_players:
        score = evaluate_hand(seat.hole_cards, game_state.table.community_cards)
        scores[seat.index] = score

    # 最も良いスコア（最小値）を見つける
    best_score = min(scores.values())
    
    # 勝者を決定
    winners = [
        game_state.table.seats[idx] for idx, score in scores.items() 
        if score == best_score
    ]
    
    # ポットを分配
    pot_per_winner = game_state.table.pot // len(winners)
    
    # サイドポットのロジックはここに追加する必要がある
    
    return [(winner, pot_per_winner) for winner in winners]
