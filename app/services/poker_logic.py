from treys import Deck, Card

def start_new_game():
    """
    新しいゲームを開始し、プレイヤーとディーラーに手札を2枚ずつ配る。
    
    Returns:
        dict: プレイヤーとディーラーの手札情報を含む辞書。
              手札は人間が読める文字列形式に変換されています。
    """
    deck = Deck()  # 新しい52枚のカードデッキを作成
    
    # 手札を配る
    player_hand_int = deck.draw(2)
    dealer_hand_int = deck.draw(2)
    
    # treysのカードは内部的に整数で表現されています。
    # Card.int_to_pretty_str() を使って、人間が読める形式（例: 'As', 'Th'）に変換します。
    player_hand_str = [Card.int_to_pretty_str(c) for c in player_hand_int]
    dealer_hand_str = [Card.int_to_pretty_str(c) for c in dealer_hand_int]
    
    return {
        "player_hand": player_hand_str,
        "dealer_hand": dealer_hand_str
    }