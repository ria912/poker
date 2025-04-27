
class Action:
    FOLD = 'fold'
    CALL = 'call'
    CHECK = 'check'
    RAISE = 'raise'
    ALL_IN = 'all-in'

    @staticmethod
    def get_legal_actions(player, current_bet, min_raise, pot):
        """プレイヤーに許されるアクションのリストを返す"""
        actions = []

        if player.current_bet < current_bet:
            if player.stack > (current_bet - player.current_bet):
                actions.append(Action.CALL)
            else:
                actions.append(Action.ALL_IN)
            actions.append(Action.FOLD)
        else:
            actions.append(Action.CHECK)

        if player.stack > (current_bet - player.current_bet + min_raise):
            actions.append(Action.RAISE)
        elif player.stack > 0:
            actions.append(Action.ALL_IN)

        return actions

    @staticmethod
    def apply_action(player, action, current_bet, raise_amount=0):
        """アクションを適用してプレイヤーの状態を更新"""
        if action == Action.FOLD:
            player.has_folded = True

        elif action == Action.CALL:
            call_amount = current_bet - player.current_bet
            actual_call = min(player.stack, call_amount)
            player.stack -= actual_call
            player.current_bet += actual_call

        elif action == Action.CHECK:
            # 何もしない
            pass

        elif action == Action.RAISE:
            total_bet = current_bet + raise_amount
            raise_amount = total_bet - player.current_bet
            player.stack -= raise_amount
            player.current_bet += raise_amount

        elif action == Action.ALL_IN:
            player.current_bet += player.stack
            player.stack = 0

