from models.table import Table
from models.round_manager import RoundManager

def run_single_hand():
    table = Table()
    round_manager = RoundManager(table)
    round_manager.start_new_round()

    print(f"\n=== STARTING HAND ===")
    for p in table.players:
        print(f"{p.name} | Stack: {p.stack} | Hand: {p.hand} | Pos: {p.position}")

    while round_manager.phase != 'showdown':
        while not round_manager.should_advance_phase():
            round_manager.proceed_action()
            print(f"Pot: {table.pot}")
            for p in table.players:
                print(f"{p.name} | Stack: {p.stack} | Bet: {p.current_bet} | Folded: {p.has_folded}")
            print("---")

        round_manager.advance_phase()
        print(f"\n>>> Phase: {round_manager.phase} <<<")
        print(f"Community: {table.community_cards}")
        print(f"Pot: {table.pot}")

    print("\n=== HAND RESULT ===")
    for p in table.players:
        print(f"{p.name} | Stack: {p.stack} | Folded: {p.has_folded} | Hand: {p.hand}")

if __name__ == "__main__":
    run_single_hand()
