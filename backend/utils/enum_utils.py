# backend/utils/enum_utils.py

from backend.models.enum import Position, Round, Action
from typing import List, TypeVar, Callable, Optional

T = TypeVar('T')

ALL_POSITIONS = [Position.BTN, Position.SB, Position.BB, Position.CO, Position.HJ, Position.LJ]
ASSIGN_ORDER = [Position.SB, Position.BB, Position.LJ, Position.HJ, Position.CO, Position.BTN, Position.BTN_SB]

ROUND_ORDER = [Round.PREFLOP, Round.FLOP, Round.TURN, Round.RIVER, Round.SHOWDOWN]


def get_circular_order(
    items: List[T],
    start_index: int,
    condition: Optional[Callable[[T], bool]] = None,
    exclude: Optional[T] = None
) -> List[T]:
    """
    リストを start_index から時計回りに回しながら、
    条件を満たすものだけを順番に返す（exclude は除外対象）

    例：
    get_circular_order([A, B, C], start_index=1, condition=lambda x: x != B)
    → [C, A]
    """
    if condition is None:
        # デフォルト：すべて対象とする
        condition = lambda x: True

    result = []
    n = len(items)

    for i in range(n):
        idx = (start_index + i) % n
        item = items[idx]

        # 条件を満たし、除外対象でなければ追加
        if condition(item) and item != exclude:
            result.append(item)

    return result


def get_next_index(
    items: List[T],
    start_index: int,
    condition: Callable[[T], bool]
) -> int:
    """
    リストを start_index から時計回りに走査し、
    条件を満たす最初の index を返す

    条件に合う要素がない場合は RuntimeError
    """
    n = len(items)

    for i in range(n):
        idx = (start_index + i) % n
        if condition(items[idx]):
            return idx

    raise RuntimeError("条件に合致する要素が見つかりませんでした。")

def next_round(current: Round) -> Round:
    i = ROUND_ORDER.index(current)
    return ROUND_ORDER[i + 1]

def betting_actions() -> list[Action]:
    return [Action.BET, Action.RAISE]

def passive_actions() -> list[Action]:
    return [Action.FOLD, Action.CHECK]
