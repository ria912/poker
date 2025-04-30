import models.action as Action
class Player:
    def __init__(self, name="player", is_human=False, stack=10000):
        self.name = name
        self.is_human = is_human
        self.stack = stack
        self.hand = []
        self.position = None
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.has_left = False

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.has_folded = False
        self.last_action = None
        self.position = None

    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "current_bet": self.current_bet,
            "hand": self.hand if self.is_human else ["X", "X"],
            "position": self.position,
            "has_folded": self.has_folded,
            "last_action": self.last_action,
            "has_left": self.has_left
        }
    
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

        return selected, amount