#backend/services/player_service.py
class PlayerService:
    def act(self, player: Player, action: Action, amount: int = 0):
        if action == Action.FOLD:
            player.last_action = Action.FOLD
            player.state = State.FOLDED

        elif action == Action.CHECK:
            player.last_action = Action.CHECK
            player.state = State.ACTED

        elif action == Action.CALL:
            player.last_action = Action.CALL
            player.stack -= amount
            player.bet_total += amount
            player.state = State.ALL_IN if player.stack == 0 else State.ACTED

        elif action in {Action.BET, Action.RAISE}:
            player.last_action = action
            player.stack -= amount
            player.bet_total += amount
            player.state = State.ALL_IN if player.stack == 0 else State.ACTED

    def reset_for_new_round(self, player: Player):
        if player.state == State.ACTED:
            player.state = None
        player.bet_total = 0
        player.last_action = None

    def reset_for_new_hand(self, player: Player):
        if player.state != State.OUT:
            player.state = None
        player.hole_cards = []
        player.bet_total = 0
        player.last_action = None