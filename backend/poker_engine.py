from models.table import Table
from models.round_manager import RoundManager

def main():
    print("Texas Hold'em - Practice Mode\n")

    table = Table()
    manager = RoundManager(table)

    manager.play_hand()

    print("\n--- Hand Summary ---")
    for p in table.players:
        print(f"{p.name} ({p.position}): Stack = {p.stack}, Hand = {p.hand}, Folded = {p.has_folded}")
    print(f"Community Cards: {table.community_cards}")

if __name__ == "__main__":
    main()
