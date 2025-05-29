#models/showdown.py
from itertools import combinations
from collections import Counter

RANK_ORDER = '23456789TJQKA'
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER, start=2)}

def card_rank(card):
    return card[0]

def card_suit(card):
    return card[1]

def get_hand_rank(cards):
    ranks = sorted([RANK_VALUE[card_rank(c)] for c in cards], reverse=True)
    suits = [card_suit(c) for c in cards]
    rank_counter = Counter(ranks)
    suit_counter = Counter(suits)

    is_flush = max(suit_counter.values()) >= 5
    is_straight, straight_high = detect_straight(ranks)

    if is_straight and is_flush:
        return (8, straight_high)  # ストレートフラッシュ
    if 4 in rank_counter.values():
        return (7, get_kicker(ranks, rank_counter, 4))  # フォーカード
    if 3 in rank_counter.values() and 2 in rank_counter.values():
        return (6, get_kicker(ranks, rank_counter, 3, 2))  # フルハウス
    if is_flush:
        return (5, ranks)  # フラッシュ
    if is_straight:
        return (4, straight_high)  # ストレート
    if 3 in rank_counter.values():
        return (3, get_kicker(ranks, rank_counter, 3))  # スリーカード
    if list(rank_counter.values()).count(2) >= 2:
        return (2, get_kicker(ranks, rank_counter, 2, 2))  # ツーペア
    if 2 in rank_counter.values():
        return (1, get_kicker(ranks, rank_counter, 2))  # ワンペア
    return (0, ranks)  # ハイカード

def detect_straight(ranks):
    unique = sorted(set(ranks), reverse=True)
    if 14 in unique:
        unique.append(1)  # A-2-3-4-5対策
    for i in range(len(unique) - 4):
        if unique[i] - unique[i + 4] == 4:
            return True, unique[i]
    return False, None

def get_kicker(ranks, counter, *target_counts):
    # 役のrank（ペアやスリーなど）を優先し、残りを kicker に
    result = []
    for count in target_counts:
        for rank, cnt in counter.items():
            if cnt == count:
                result.extend([rank] * count)
    for rank in ranks:
        if rank not in result:
            result.append(rank)
    return result[:5]


def evaluate_best_hand(cards7):
    best_rank = (-1, [])  # (役ランク, tiebreaker)
    for combo in combinations(cards7, 5):
        rank = get_hand_rank(combo)
        if rank > best_rank:
            best_rank = rank
    return best_rank  # 例: (6, [13, 13, 13, 12, 12]) → フルハウス