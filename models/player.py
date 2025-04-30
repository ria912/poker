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
    
    def decide_action(self, legal_info):
        legal_actions = legal_info["actions"]
        current_bet = legal_info["current_bet"]
        min_bet = legal_info["min_bet"]
    
        print(f"\n{self.name}, it's your turn!")
        print(f"Pot: {legal_info['pot']}")
        print(f"Your stack: {self.stack}")
        print(f"Current bet: {current_bet}, Your bet: {self.current_bet}")
        
        print("Legal actions you can choose:")
        for action in legal_actions:
            print(f"- {action}")
    
        while True:
            action = input("Choose your action: ").strip().lower()
            if action not in legal_actions:
                print("Invalid action. Try again.")
                continue
    
            amount = 0
            if action in [Action.BET, Action.RAISE, Action.ALL_IN]:
                try:
                    amount = int(input("Enter the amount: "))
                    if amount > self.stack:
                        print("You don't have enough chips.")
                        continue
                    if action in [Action.BET, Action.RAISE] and amount < min_bet:
                        print(f"Minimum {action} is {min_bet}.")
                        continue
                except ValueError:
                    print("Invalid amount.")
                    continue
    
            self.last_action = action
            return action, amount