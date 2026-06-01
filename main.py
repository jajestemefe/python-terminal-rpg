import time
import os

from engine import clear_screen, Colors, display_stats, print_anim, is_skip_intro, display_intro
from entities import Player, create_player
from save_manager import ask_if_load
from world import encounter_generator
from combat import combat_loop
from item_manager import get_item, apply_item
import save_manager


# ── Inventory helpers ─────────────────────────────────────────────────────────

def _item_tag(name: str, player: Player) -> str:
    """Return a colored tag if the item is the currently equipped weapon."""
    if name == player.equipped_weapon:
        return f" {Colors.GREEN}[EQUIPPED]{Colors.RESET}"
    return ""


def _inventory_loop(player: Player):
    """Interactive numbered inventory screen."""
    while True:
        clear_screen()
        display_stats(player)
        print_anim(f"\n{Colors.CYAN}=== {player.name}'s Inventory ==={Colors.RESET}")
        print_anim(f"Weapon equipped : {player.equipped_weapon}  |  Attack power : {player.attack_power}\n")

        # List comprehension: items the player actually carries
        carried = [(name, qty) for name, qty in sorted(player.inventory.items()) if qty > 0]

        if not carried:
            print_anim("  (your bag is empty)")
            print_anim("\nPress Enter to return...")
            input()
            break

        # Display Numbered List
        for idx, (name, qty) in enumerate(carried, 1):
            item_def = get_item(name)
            tag  = _item_tag(name, player)
            desc = f"    {Colors.CYAN}» {item_def.description}{Colors.RESET}" if item_def else ""
            print_anim(f"  [{idx}] {name} x{qty}{tag}")
            if desc:
                print_anim(desc)

        print_anim("\nEnter item number to interact with (or Enter to return)\n> ")
        raw = input().strip()

        if not raw:
            break

        if raw.isdigit() and 1 <= int(raw) <= len(carried):
            selected_name = carried[int(raw) - 1][0]
            # Since our OOP item_manager handles the logic contextually, we just pass "menu"
            success, msg = apply_item(player, selected_name, "menu")
            color = Colors.GREEN if success else Colors.RED
            print_anim(f"\n{color}{msg}{Colors.RESET}")
        else:
            print_anim(f"\n{Colors.RED}Invalid selection.{Colors.RESET}")

        time.sleep(1.8)


# ── Death and game over ───────────────────────────────────────────────────────

def _handle_game_over(player: Player, cause: str):
    """
    Show game over and offer restart or quit.
    Returns (new_player, new_rooms) on restart, or (None, None) to exit the game.
    """
    clear_screen()
    print_anim(f"\n{Colors.RED}*** GAME OVER ***{Colors.RESET}")
    print_anim(f"{Colors.YELLOW}{player.name} has fallen.{Colors.RESET}")
    print_anim(f"{cause}\n")
    print_anim(f"{Colors.CYAN}[1] Start a new adventure")
    print_anim(f"{Colors.CYAN}[2] Quit to title{Colors.RESET}")
    print_anim(f"\n{Colors.YELLOW}What will you do?")
    choice = input(f"> {Colors.RESET}").strip()

    if choice == "1":
        time.sleep(0.5)
        is_skip_intro()
        return create_player(), encounter_generator()

    print_anim(f"\n{Colors.GREEN}Thanks for playing! Goodbye.\n{Colors.RESET}")
    return None, None


def _resolve_explore_encounter(player: Player, encounter) -> bool:
    """
    Apply an explore encounter to the player.
    Returns False if the player died (trap or combat).
    """
    if isinstance(encounter, str):
        if encounter == "empty":
            print_anim("The room is cold and empty. You move on safely.")
        elif encounter == "trap":
            damage = 15
            player.take_damage(damage)
            print_anim(
                f"{Colors.RED}SNAP! You stepped on a trap and took {damage} damage!{Colors.RESET}"
            )
            print_anim(f"Current HP: {player.health}/{player.max_health}")
            if not player.is_alive():
                print_anim(
                    f"\n{Colors.RED}You collapse from your wounds. The dungeon claims another soul.{Colors.RESET}"
                )
                time.sleep(1.5)
                return False

    elif isinstance(encounter, dict):
        item = encounter["item"]
        qty = encounter["quantity"]
        print_anim(f"{Colors.GREEN}You found a chest: {qty}x {item}!{Colors.RESET}")
        player.inventory[item] = player.inventory.get(item, 0) + qty

    else:
        print_anim(f"A {encounter.name} blocks your path!")
        time.sleep(1)
        if not combat_loop(player, encounter):
            return False

    return True


# ── Main game menu ────────────────────────────────────────────────────────────

def main_menu(player: Player, rooms):
    """The main interactive loop for the game."""
    while True:
        clear_screen()
        display_stats(player)
        print_anim(f"\n{Colors.CYAN}--- MAIN MENU ---")
        print_anim("[1] Explore the Dungeon")
        print_anim("[2] Check Inventory")
        print_anim("[3] Settings")
        print_anim("[4] Save Game")
        print_anim("[5] Load Game")
        print_anim("[6] Delete Save")
        print_anim("[7] New Game")
        print_anim(f"[8] Quit{Colors.RESET}")

        print_anim(f"{Colors.YELLOW}\nWhat would you like to do?")
        choice = input(f"> {Colors.RESET}").strip()

        # ── Explore ──────────────────────────────────────────────────────────
        if choice == "1":
            if not player.is_alive():
                cause = "You cannot continue with no health remaining."
                player, rooms = _handle_game_over(player, cause)
                if player is None:
                    break
                continue

            clear_screen()
            display_stats(player)
            print_anim("\nYou step forward into the darkness...")
            time.sleep(1)

            encounter = next(rooms)

            if not _resolve_explore_encounter(player, encounter):
                cause = (
                    "The trap was your undoing."
                    if isinstance(encounter, str) and encounter == "trap"
                    else "You were slain in battle."
                )
                player, rooms = _handle_game_over(player, cause)
                if player is None:
                    break
                continue

            print_anim("\nPress Enter to return to the menu...")
            input()

        # ── Inventory ────────────────────────────────────────────────────────
        elif choice == "2":
            _inventory_loop(player)

        # ── Settings ─────────────────────────────────────────────────────────
        elif choice == "3":
            while True:
                clear_screen()
                display_stats(player)
                print_anim(f"\n{Colors.CYAN}--- SETTINGS ---")
                if save_manager.animation:
                    x = f"{Colors.GREEN}ENABLED"
                else:
                    x = f"{Colors.RED}DISABLED"
                print_anim(f"{Colors.CYAN}[1] Text animation: " + x)
                print_anim(f"{Colors.CYAN}[2] Replay intro story")
                print_anim(f"\n{Colors.YELLOW}Choose an option (or Enter to return){Colors.RESET}")
                setting = input(f"> {Colors.RESET}").strip()

                if setting == '1':
                    save_manager.animation = not save_manager.animation

                elif setting == '2':
                    clear_screen()
                    display_intro()
                    print_anim(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
                    input()

                else:
                    break

        # ── Save ─────────────────────────────────────────────────────────────
        elif choice == "4":
            print_anim(f"\nEnter a name for this save slot\n> {Colors.RESET}")
            save_slot = input().strip()
            if save_slot:
                filepath = os.path.join(save_manager.SAVE_DIR, f"{save_slot}.json")
                if os.path.exists(filepath):

                    print_anim(f"{Colors.YELLOW}Save '{save_slot}' already exists. Overwrite? (y/n)")
                    confirm = input(f"> {Colors.RESET}").strip().lower()

                    if confirm != "y":
                        print_anim(f"{Colors.RED}Save cancelled.{Colors.RESET}")
                        time.sleep(1.5)
                        continue
                save_manager.save_game(player, save_slot)
            else:
                print_anim(f"{Colors.RED}Invalid save name. Cancelled.{Colors.RESET}")
            time.sleep(1.5)

        # ── Load ─────────────────────────────────────────────────────────────
        elif choice == "5":
            save_files = save_manager.get_save_files()
            if not save_files:
                print_anim(f"{Colors.YELLOW}No save files found.{Colors.RESET}")
            else:
                print_anim("\nAvailable saves:")
                for idx, sf in enumerate(save_files, 1):
                    name = os.path.basename(sf).replace(".json", "")
                    print_anim(f"  [{idx}] {name}")

                print_anim("\nEnter number to load (or Enter to cancel)")
                save_choice = input(f"> {Colors.RESET}").strip()
                if save_choice.isdigit() and 1 <= int(save_choice) <= len(save_files):
                    slot_name   = os.path.basename(save_files[int(save_choice) - 1]).replace(".json", "")
                    loaded_hero = save_manager.load_game(slot_name)
                    if loaded_hero:
                        player = loaded_hero
                        print_anim(f"{Colors.GREEN}\nWelcome back, {player.name}!{Colors.RESET}")
                    # load_game prints its own error message when it returns None
                elif save_choice:
                    print_anim(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)

        # ── Delete save ───────────────────────────────────────────────────────
        elif choice == "6":
            save_files = save_manager.get_save_files()
            if not save_files:
                print_anim(f"{Colors.YELLOW}No save files found to delete.{Colors.RESET}")
            else:
                print_anim("\nAvailable saves:")
                for idx, sf in enumerate(save_files, 1):
                    name = os.path.basename(sf).replace(".json", "")
                    print_anim(f"  [{idx}] {name}")

                print_anim(f"\nEnter number to delete (or Enter to cancel)")
                del_choice = input(f"> {Colors.RESET}").strip()
                if del_choice.isdigit() and 1 <= int(del_choice) <= len(save_files):
                    slot_name = os.path.basename(save_files[int(del_choice) - 1]).replace(".json", "")
                    print_anim(
                        f"{Colors.RED}Delete '{slot_name}'? This cannot be undone. (y/n) > {Colors.RESET}"
                    )
                    confirm   = input().strip().lower()
                    if confirm == "y":
                        save_manager.delete_save(slot_name)
                elif del_choice:
                    print_anim(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)

        # ── New game ──────────────────────────────────────────────────────────
        elif choice == "7":
            print_anim(f"\n{Colors.YELLOW}Start a new game? Unsaved progress will be lost. (y/n)")
            confirm = input(f"> {Colors.RESET}").strip().lower()
            if confirm == "y":
                time.sleep(1.5)
                is_skip_intro()
                player = create_player()
                rooms  = encounter_generator()
            else:
                time.sleep(1.5)

        # ── Quit ──────────────────────────────────────────────────────────────
        elif choice == "8":
            print_anim(f"{Colors.YELLOW}\nUnsaved progress will be lost, are you sure? (y/n)\n> {Colors.RESET}")
            if input().strip() == 'y':
                print_anim(f"\n{Colors.GREEN}Thanks for playing! Goodbye.\n{Colors.RESET}")
                break
            else:
                continue


        else:
            print_anim(f"\n{Colors.RED}Invalid choice. Enter a number between 1 and 8.{Colors.RESET}")
            time.sleep(1)


# ── Entry point ───────────────────────────────────────────────────────────────

def start():
    """Main entry point. ask_if_load() always returns a valid Player."""
    clear_screen()
    hero          = ask_if_load()
    dungeon_rooms = encounter_generator()
    clear_screen()
    main_menu(hero, dungeon_rooms)


if __name__ == "__main__":
    start()