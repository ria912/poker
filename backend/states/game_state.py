from backend.models.table import Table
from backend.models.enum import Action, Status, Round
from backend.services.game.dealer import Dealer
from backend.services.game.round_manager import RoundManager
from backend.services.game.position_manager import PositionManager
from backend.services.game.action_manager import ActionManager

class GameState:
    def __init__(self, player_num: int):
        # プレイヤー数に応じてテーブルを初期化
        self.table = Table(player_num=player_num)
        self.dealer = Dealer()
        self.round_manager = RoundManager(self.table)
        self.position_manager = PositionManager(self.table)

        self.status = Status.WAITING

    def reset(self):
        """
        ゲームの状態をリセット（新しい1ハンドを開始する準備）
        """
        self.table.reset_hand()  # スタック、ポジションなどリセット
        self.dealer.shuffle_deck()
        self.dealer.deal_hole_cards(self.table)
        self.position_manager.assign_positions()
        self.round_manager.start_new_round()
        self.status = Status.GAME_CONTINUE

    def step(self, action: Action, amount: int = 0):
        """
        アクションを適用し、次のプレイヤー or ラウンドへ進める
        """
        ActionManager.apply_action(self.table, action, amount)
        self.status = self.round_manager.advance_round(self.table)

    def get_observation(self) -> dict:
        """
        現在のゲーム状態を辞書形式で返す（フロントエンドへ）
        """
        return {
            "board": self.table.board,
            "pot": self.table.pot,
            "players": [seat.to_dict() for seat in self.table.seats],
            "current_turn": self.table.get_current_seat().name,
            "legal_actions": self.get_legal_actions()
        }

    def get_legal_actions(self) -> list:
        """
        現在のプレイヤーが実行可能なアクションを返す
        """
        return ActionManager.get_legal_actions_info(self.table)

    def is_hand_over(self) -> bool:
        """
        ハンドが終了しているか確認（例：1人だけが残った、またはリバー終了）
        """
        return self.status == Status.GAME_OVER

    def get_winner_info(self) -> dict:
        """
        勝者情報を返す（終了後のみ）
        """
        return self.dealer.get_result(self.table)
