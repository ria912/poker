from models.table import Table
from models.round_manager import RoundManager

def main():
    print("=== Texas Hold'em Practice App ===\n")

    table = Table()
    round_manager = RoundManager(table)

    while True:
        round_manager.start_new_hand()

        again = input("\nPlay another hand? (y/n): ").lower()
        if again != 'y':
            break

    print("Thanks for playing!")

if __name__ == "__main__":
    main()
