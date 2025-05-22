from models.table import Table
from models.round_manager import RoundManager

class GameState:
    def __init__(self):
        self.table = Table()
        self.table.seat_assign_players()
        self.round_manager = RoundManager(self.table)
        self.is_hand_started = False

    def start_new_hand(self):
        self.table.reset_for_new_hand()
        self.table.start_hand()
        self.round_manager._start_betting_round()
        self.is_hand_started = True

    def get_state(self, show_all_hands=False):
        """現在のゲーム状態を辞書で返す"""
        state = self.table.to_dict(show_all_hands=show_all_hands)
        state.update({
            "round": self.table.round.title(),
            "waiting_for_human": self.round_manager.waiting_for_human,
            "hand_started": self.is_hand_started,
        })
        return state

    def proceed_game(self):
        """AIまたは次のアクションを進める。
        人間の入力待ちの場合は例外が上がる。
        """
        if not self.is_hand_started:
            self.start_new_hand()

        result = self.round_manager.proceed_one_action()
        return result

    def human_action(self, action_dict):
        """人間プレイヤーのアクションを受け取る"""
        human = next(p for p in self.table.seats if p and getattr(p, 'is_human', False))
        human.set_action(action_dict)
        result = self.round_manager.resume_after_human_action()
        return result
