import unittest
from models.table import Table
from models.player import Player
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer

class TestTable(unittest.TestCase):

    def setUp(self):
        # テストの前に実行されるセットアップコード
        self.table = Table(small_blind=50, big_blind=100)

    def test_create_players(self):
        # プレイヤーが6人いるか
        self.assertEqual(len(self.table.players), 6)

        # 1人目はHumanPlayer（YOU）であること
        self.assertIsInstance(self.table.players[0], HumanPlayer)
        self.assertEqual(self.table.players[0].name, "YOU")

        # 残りはAIPlayerであること
        for i in range(1, 6):
            self.assertIsInstance(self.table.players[i], AIPlayer)
            self.assertEqual(self.table.players[i].name, f"AI{i}")

    def test_post_blinds(self):
        # ブラインドが正しく投稿されているか
        self.table.start_hand()
        
        # SB と BB のプレイヤーがブラインドを投稿
        sb_player = next(p for p in self.table.players if p.position == 'SB')
        bb_player = next(p for p in self.table.players if p.position == 'BB')

        self.assertEqual(sb_player.current_bet, self.table.small_blind)
        self.assertEqual(bb_player.current_bet, self.table.big_blind)
        self.assertEqual(self.table.pot, self.table.small_blind + self.table.big_blind)

    def test_deal_cards(self):
        # プレイヤーに2枚のカードが配られるか
        self.table.start_hand()
        
        for player in self.table.players:
            if not player.has_left:
                self.assertEqual(len(player.hand), 2)

    def test_rotate_players(self):
        # プレイヤーが正しくローテーションされるか
        initial_positions = [p.position for p in self.table.players]
        self.table.start_hand()
        self.table.players.append(self.table.players.pop(0))  # ローテーションを模擬
        rotated_positions = [p.position for p in self.table.players]

        self.assertNotEqual(initial_positions, rotated_positions)

    def test_assign_positions(self):
        # ポジションが正しく割り当てられるか
        self.table.start_hand()

        positions = [p.position for p in self.table.players if not p.has_left]
        self.assertEqual(sorted(positions), sorted(['BTN', 'SB', 'BB', 'CO', 'HJ', 'LJ']))

    def test_reset_players(self):
        # ゲーム終了後にプレイヤーがリセットされるか
        self.table.start_hand()

        for player in self.table.players:
            player.stack -= 500  # ダミーのアクションを加える
            player.current_bet = 500

        self.table.reset_players()

        for player in self.table.players:
            self.assertEqual(player.current_bet, 0)
            self.assertEqual(player.stack, 10000)  # 初期スタックにリセット

if __name__ == "__main__":
    unittest.main()
