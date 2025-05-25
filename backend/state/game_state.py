# state/game_state.py
from models.table import Table
from models.round_manager import RoundManager
from models.human_player import WaitingForHumanAction

class GameState:
    """
    ゲームの進行と状態を管理するクラス。
    外部からはこのクラス経由で操作する。
    """
    def __init__(self):
        self.table = Table()  # プレイヤー・山札などを持つテーブル
        self.round_manager = RoundManager(self.table)
        self.is_hand_started = False

    def start_new_hand(self):
        """新しい手札を開始する"""
        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager._start_betting_round()
        self.is_hand_started = True

    def get_state(self, show_all_hands=False):
        """現在のゲーム状態を辞書形式で取得"""
        state = self.table.to_dict(show_all_hands=show_all_hands)
        state.update({
            "round": self.table.round.title() if self.table.round else None,
            "waiting_for_human": self.round_manager.waiting_for_human,
            "hand_started": self.is_hand_started,
        })
        return state

    def proceed_game(self):
        """
        ゲームを1手分進める。
        AIのアクション → 次のプレイヤーへ。
        人間の番なら WaitingForHumanAction を投げる。
        """
        if not self.is_hand_started:
            self.start_new_hand()
        try:
            return self.round_manager.proceed_one_action()
        except WaitingForHumanAction:
            raise
        except Exception as e:
            raise RuntimeError(f"AI進行エラー: {e}")

    def human_action(self, action_dict):
        """人間プレイヤーのアクションを受け取ってゲームを進める"""
        try:
            human = next(
                p for p in self.table.seats
                if p and getattr(p, 'is_human', False) and not getattr(p, 'has_left', False)
            )
        except StopIteration:
            raise RuntimeError("人間プレイヤーが見つかりません")

        human.set_action(action_dict)

        try:
            return self.round_manager.resume_after_human_action()
        except WaitingForHumanAction:
            raise
        except Exception as e:
            raise RuntimeError(f"人間アクション処理エラー: {e}")
