# models/human_player.py
from models.player import Player
from models.action import Action

class HumanPlayer(Player):
    def __init__(self, name="YOU", stack=10000):
        super().__init__(name=name, stack=stack)
        self.is_human = True

    def decide_action(self, context):
        actions = context["actions"]["actions"]
        pot = context["pot"]
        current_bet = context["current_bet"]
        min_bet = context["min_bet"]

        print(f"\n{self.name}'s Turn!")
        print(f"Your hand: {self.hand}")
        print(f"Pot: {pot}, Current Bet: {current_bet}, Your Bet: {self.current_bet}, Your Stack: {self.stack}")
        print("Available actions:")
        for i, act in enumerate(actions):
            print(f"{i}: {act}")

        while True:
            choice = input("Choose action by number: ")
            if choice.isdigit() and int(choice) in range(len(actions)):
                selected = actions[int(choice)]
                break
            else:
                print("Invalid input. Try again.")

        amount = 0
        if selected in ["bet", "raise"]:
            while True:
                try:
                    amount = int(input(f"Enter amount to {selected} (min {min_bet}): "))
                    if amount >= min_bet:
                        break
                    else:
                        print(f"Amount must be at least {min_bet}")
                except ValueError:
                    print("Invalid amount.")

        self.last_action = selected
        return selected, amount
