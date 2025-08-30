# holdem_app/app/services/ai_strategy.py
from app.models.deck import Card
from app.models.enum import Position

def get_hand_representation(cards: list[Card]) -> str:
    """
    2枚のカードをポーカーで一般的な文字列表現（例: "AKs", "T9o", "77"）に変換する
    """
    if len(cards) != 2:
        return ""

    card1, card2 = cards
    
    rank_order = "AKQJT98765432"
    rank1 = card1.rank
    rank2 = card2.rank

    # ランクを強い順に並べる
    if rank_order.index(rank1) > rank_order.index(rank2):
        rank1, rank2 = rank2, rank1

    # スーテッドかオフスーテッドか
    suited_suffix = "s" if card1.suit == card2.suit else "o"
    
    # ポケットペアの場合
    if rank1 == rank2:
        return f"{rank1}{rank2}"
    
    return f"{rank1}{rank2}{suited_suffix}"

# 6-maxテーブル用のシンプルなオープンレンジ表
# キー: ポジション, バリュー: オープンレイズするハンドのセット
OPENING_RANGES = {
    # アーリーポジション (LJ) は非常にタイト
    Position.LJ: {
        "AA", "KK", "QQ", "JJ", "TT", "99", "88",
        "AKs", "AQs", "AJs", "ATs", "KQs", "KJs",
        "AKo", "AQo"
    },
    # ミドルポジション (HJ)
    Position.HJ: {
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77",
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s",
        "KQs", "KJs", "KTs",
        "QJs", "QTs",
        "JTs",
        "AKo", "AQo", "AJo"
    },
    # レイトポジション (CO) は広くなる
    Position.CO: {
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55",
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
        "KQs", "KJs", "KTs", "K9s",
        "QJs", "QTs", "Q9s",
        "JTs", "J9s",
        "T9s",
        "98s",
        "87s",
        "AKo", "AQo", "AJo", "ATo",
        "KQo", "KJo"
    },
    # 最も広いBTN
    Position.BTN: {
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
        "KQs", "KJs", "KTs", "K9s", "K8s",
        "QJs", "QTs", "Q9s",
        "JTs", "J9s",
        "T9s", "T8s",
        "98s", "97s",
        "87s",
        "76s",
        "AKo", "AQo", "AJo", "ATo", "A9o",
        "KQo", "KJo", "KTo",
        "QJo", "QTo",
        "JTo"
    },
    # SBは少し特殊だが、BTNよりはタイトに
    Position.SB: {
        "AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66",
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s",
        "KQs", "KJs", "KTs",
        "QJs", "QTs",
        "JTs",
        "T9s",
        "AKo", "AQo", "AJo", "KQo"
    }
}
