from typing import List

# modelsから必要なクラスとEnumをインポートします
from models import (
    GameState,
    Player,
    Round,
    PlayerState,
    GameStatus,
    Position,
    game_state,  # グローバルなゲーム状態インスタンス
)


class GameService:
    """
    ゲームの進行ロジックを担当するサービスクラス。
    ハンドの開始、ラウンドの遷移、終了処理などを統括します。
    """

    def __init__(self, state: GameState):
        """
        コンストラクタ。操作対象のゲーム状態を受け取ります。
        これにより、テスト時に特定の状態を注入しやすくなります。
        """
        self.game_state = state

    def start_new_hand(self, big_blind_amount: int = 20):
        """
        新しいハンドを開始します。
        
        - プレイヤーの状態をリセット
        - ディーラーボタンの移動
        - ポジションの割り当てとブラインドの強制徴収
        - デッキのシャッフルとカードの配布
        - プリフロップのアクション開始
        """
        print("--- 新しいハンドを開始します ---")
        table = self.game_state.table
        active_players = self._get_active_players_for_new_hand()

        # ゲーム開始に必要な最低人数をチェック
        if len(active_players) < 2:
            print("プレイヤーが2人未満のため、ゲームを開始できません。")
            self.game_state.game_status = GameStatus.WAITING
            return

        # 1. テーブルとプレイヤーの状態をリセット
        self._reset_table_and_players(active_players)

        # 2. ディーラーボタンを次のアクティブプレイヤーに移動
        self._move_dealer_button(active_players)

        # 3. ポジションを割り当て、ブラインドを支払う
        #    (本来は PositionManager が担当)
        small_blind_amount = big_blind_amount // 2
        self._assign_positions_and_post_blinds(active_players, small_blind_amount, big_blind_amount)

        # 4. デッキをシャッフルし、各プレイヤーにホールカードを配る
        self._deal_hole_cards(active_players)
        
        # 5. プリフロップのアクションを開始するプレイヤーを決定
        #    (本来は RoundManager が担当)
        self._set_preflop_starter()
        
        self.game_state.game_status = GameStatus.ROUND_CONTINUE
        print(f"プリフロップを開始します。アクションは {self.game_state.table.get_player_by_id(self.game_state.active_player_id).name} からです。")


    def advance_to_next_round(self):
        """
        次のベッティングラウンドに進みます (フロップ -> ターン -> リバー)。
        """
        table = self.game_state.table
        current_round = table.current_round
        
        # 最終ラウンドならショーダウンへ
        if current_round == Round.RIVER:
            self.game_state.game_status = GameStatus.SHOWDOWN
            print("--- ショーダウン ---")
            # ここで勝者判定ロジック (evaluter) を呼び出す
            return

        # 次のラウンドへ進める
        next_round_enum = current_round.next()
        table.current_round = next_round_enum
        print(f"--- {next_round_enum.value} に進みます ---")
        
        # 1. 各プレイヤーのラウンドベット額をリセット
        for player in self.game_state.players:
            if player.state == PlayerState.ACTIVE:
                player.current_bet = 0

        # 2. コミュニティカードをディール
        deck = self.game_state.deck
        if next_round_enum == Round.FLOP:
            table.community_cards.extend(deck.deal(3))
        elif next_round_enum in [Round.TURN, Round.RIVER]:
            table.community_cards.extend(deck.deal(1))

        # 3. ポストフロップのアクションを開始するプレイヤーを決定
        self._set_postflop_starter()
        
        self.game_state.game_status = GameStatus.ROUND_CONTINUE
        print(f"コミュニティカード: {[card.treys_str for card in table.community_cards]}")
        print(f"アクションは {self.game_state.table.get_player_by_id(self.game_state.active_player_id).name} からです。")


    ### 以下は内部的に使われるヘルパーメソッドです ###

    def _get_active_players_for_new_hand(self) -> List[Player]:
        """新しいハンドに参加資格のあるプレイヤー（スタックが0より大きい）を取得します。"""
        return [
            seat.player for seat in self.game_state.table.seats 
            if seat.is_occupied and seat.player.stack > 0
        ]

    def _reset_table_and_players(self, players: List[Player]):
        """テーブルとプレイヤーの状態を新しいハンドのために初期化します。"""
        self.game_state.table.pot = 0
        self.game_state.table.community_cards = []
        self.game_state.table.current_round = Round.PREFLOP
        self.game_state.deck.reset_and_shuffle()
        
        for player in players:
            player.hand = []
            player.state = PlayerState.ACTIVE
            player.current_bet = 0
            player.position = None
        print("テーブルとプレイヤーの状態をリセットしました。")


    def _move_dealer_button(self, active_players: List[Player]):
        """ディーラーボタンを次のアクティブなプレイヤーに移動させます。"""
        table = self.game_state.table
        
        # 現在のディーラーの次の席から探索を開始
        current_dealer_seat_index = table.dealer_position
        num_seats = table.seat_count
        
        # 無限ループを避けるため、探索は1周だけ
        for i in range(1, num_seats + 1):
            next_seat_index = (current_dealer_seat_index + i) % num_seats
            seat = table.seats[next_seat_index]
            if seat.is_occupied and seat.player in active_players:
                table.dealer_position = next_seat_index
                print(f"ディーラーボタンは {seat.player.name} (シート{next_seat_index}) に移動しました。")
                return


    def _assign_positions_and_post_blinds(self, active_players: List[Player], sb_amount: int, bb_amount: int):
        """ポジションを割り当て、SBとBBからブラインドを徴収します。"""
        # このロジックは本来 PositionManager に実装されるべきものです
        table = self.game_state.table
        dealer_idx = table.dealer_position
        player_seats = {p.player_id: s.seat_index for s in table.seats if s.is_occupied for p in [s.player]}

        # ディーラーからの相対位置でプレイヤーをソート
        sorted_players = sorted(
            active_players,
            key=lambda p: (player_seats[p.player_id] - dealer_idx + table.seat_count) % table.seat_count
        )
        
        # SBとBBを決定（ヘッズアップも考慮）
        sb_player = sorted_players[1] if len(sorted_players) > 2 else sorted_players[0]
        bb_player = sorted_players[2] if len(sorted_players) > 2 else sorted_players[1]
        
        # SBの支払い
        sb_player.position = Position.SB
        sb_player.stack -= sb_amount
        sb_player.current_bet = sb_amount
        table.pot += sb_amount
        print(f"{sb_player.name} がSBとして {sb_amount} を支払いました。")

        # BBの支払い
        bb_player.position = Position.BB
        bb_player.stack -= bb_amount
        bb_player.current_bet = bb_amount
        table.pot += bb_amount
        print(f"{bb_player.name} がBBとして {bb_amount} を支払いました。")


    def _deal_hole_cards(self, active_players: List[Player]):
        """アクティブな各プレイヤーに2枚のカードを配ります。"""
        # SBから時計回りに配るのが一般的なルール
        sb_player = self.game_state.table.get_player_by_position(Position.SB)
        sb_seat_index = next(s.seat_index for s in self.game_state.table.seats if s.player == sb_player)

        sorted_players_for_deal = sorted(
            active_players,
            key=lambda p: (
                next(s.seat_index for s in self.game_state.table.seats if s.player == p) - sb_seat_index + self.game_state.table.seat_count
            ) % self.game_state.table.seat_count
        )
        
        for player in sorted_players_for_deal:
            player.hand = self.game_state.deck.deal(2)
            print(f"{player.name} にカードを配りました。")


    def _set_preflop_starter(self):
        """プリフロップで最初にアクションするプレイヤー（UTG/BBの次）を設定します。"""
        # このロジックは本来 RoundManager に実装されるべきものです
        bb_player = self.game_state.table.get_player_by_position(Position.BB)
        bb_seat_index = next(s.seat_index for s in self.game_state.table.seats if s.player == bb_player)
        
        active_players = self._get_active_players_for_new_hand()
        
        for i in range(1, len(active_players) + 1):
            next_seat_index = (bb_seat_index + i) % self.game_state.table.seat_count
            seat = self.game_state.table.seats[next_seat_index]
            if seat.player in active_players:
                self.game_state.active_player_id = seat.player.player_id
                return


    def _set_postflop_starter(self):
        """フロップ以降で最初にアクションするプレイヤー（ディーラーの次のアクティブプレイヤー）を設定します。"""
        # このロジックは本来 RoundManager に実装されるべきものです
        dealer_seat_index = self.game_state.table.dealer_position
        active_players = [p for p in self.game_state.players if p.state == PlayerState.ACTIVE]
        
        for i in range(1, self.game_state.table.seat_count + 1):
            next_seat_index = (dealer_seat_index + i) % self.game_state.table.seat_count
            seat = self.game_state.table.seats[next_seat_index]
            if seat.player in active_players:
                self.game_state.active_player_id = seat.player.player_id
                return

# シングルトンとしてサービスインスタンスを作成
# FastAPIのDIシステムを利用する場合は、このインスタンスを依存関係として提供します。
game_service = GameService(game_state)